from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
import sqlite3
import pymysql
import pymysql.cursors
import os
from urllib.parse import urlencode
from datetime import datetime
import secrets
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import stripe

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Configuration Base de données (MySQL sur o2switch, SQLite en local)
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME')

DATABASE = os.path.join(app.instance_path, "aquacoach.db")
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Configuration Stripe Payment Link
STRIPE_PAYMENT_LINK = os.environ.get('STRIPE_PAYMENT_LINK', 'https://buy.stripe.com/4gM8wQ6IfbWIf2m2JDe7m0d')

# Configuration Stripe Checkout (recommandé: montant contrôlé côté serveur)
# IMPORTANT: ne jamais mettre la clé dans le code. Définissez-la dans .htaccess:
# SetEnv STRIPE_SECRET_KEY "sk_live_..." (ou sk_test_... en mode test)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Configuration OAuth Strava
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.environ.get(
    "STRAVA_REDIRECT_URI",
    "https://aquacoach.fr/auth/callback",
)
STRAVA_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_SCOPE = "read,activity:read_all,profile:read_all"

# Identifiants admin (à changer en production !)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")  # Mot de passe: admin123

# Configuration Gmail (SMTP)
MAILJET_HOST = "smtp.gmail.com"
MAILJET_PORT = 587
MAILJET_USERNAME = "aqua.cannes@gmail.com"
MAILJET_PASSWORD = "hnhh yavb ided rwcg"
MAILJET_FROM_EMAIL = "aqua.cannes@gmail.com"
MAILJET_FROM_NAME = "AquaCoach"
ADMIN_EMAIL = "aqua.cannes@gmail.com"

# Liste des départements français
DEPARTEMENTS = [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
    "32",
    "33",
    "34",
    "35",
    "36",
    "37",
    "38",
    "39",
    "40",
    "41",
    "42",
    "43",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "50",
    "51",
    "52",
    "53",
    "54",
    "55",
    "56",
    "57",
    "58",
    "59",
    "60",
    "61",
    "62",
    "63",
    "64",
    "65",
    "66",
    "67",
    "68",
    "69",
    "70",
    "71",
    "72",
    "73",
    "74",
    "75",
    "76",
    "77",
    "78",
    "79",
    "80",
    "81",
    "82",
    "83",
    "84",
    "85",
    "86",
    "87",
    "88",
    "89",
    "90",
    "91",
    "92",
    "93",
    "94",
    "95",
    "971",
    "972",
    "973",
    "974",
    "976",
]

# ============================================
# EMAIL FUNCTIONS
# ============================================


def send_confirmation_email(
    client_email,
    client_prenom,
    client_nom,
    nageur_prenom,
    nageur_nom,
    nageur_email,
    nageur_tel,
    nageur_ville,
    montant="5,00 €",
):
    """Envoie un email de confirmation au client et à l'admin"""
    print(f"\n🔔 ENVOI D'EMAIL")
    print(f"   Client: {client_prenom} {client_nom} <{client_email}>")
    print(f"   Nageur: {nageur_prenom} {nageur_nom}")

    try:
        # Génération du code de validation
        code_validation = secrets.token_hex(4).upper()

        # Connexion SMTP
        print(f"📤 Connexion à Mailjet...")
        server = smtplib.SMTP(MAILJET_HOST, MAILJET_PORT, timeout=30)
        server.starttls()
        server.login(MAILJET_USERNAME, MAILJET_PASSWORD)

        # EMAIL 1 : Au client
        msg_client = MIMEMultipart("alternative")
        msg_client["Subject"] = "Confirmation de réservation - AquaCoach"
        msg_client["From"] = f"{MAILJET_FROM_NAME} <{MAILJET_FROM_EMAIL}>"
        msg_client["To"] = client_email

        html_client = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #3fb0ac;">🌊 Merci pour votre réservation !</h2>
            <p>Bonjour <strong>{client_prenom} {client_nom}</strong>,</p>
            <p>Votre réservation avec <strong>{nageur_prenom} {nageur_nom}</strong> a été confirmée.</p>
            <div style="padding:20px;border:2px dashed #3fb0ac;background:#f4f8fb;margin:20px 0;">
              <h3 style="text-align:center;color:#3fb0ac;">🎟️ Bon de réservation</h3>
              <p><strong>Votre maître-nageur :</strong></p>
              <ul>
                <li>👤 {nageur_prenom} {nageur_nom}</li>
                <li>📍 Ville : {nageur_ville}</li>
                <li>📧 Email : <a href="mailto:{nageur_email}">{nageur_email}</a></li>
                <li>📞 Téléphone : {nageur_tel}</li>
              </ul>
              <p><strong>Montant payé :</strong> {montant}</p>
              <p><strong>Code de validation :</strong> <span style="font-size:1.5em;color:#cc3366;">{code_validation}</span></p>
            </div>
            <p>Contactez votre maître-nageur pour planifier vos séances.</p>
            <p style="font-size: 0.9em; color: #666; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px;">
                <em>Note : La mise en relation est effective. Merci de vérifier que la carte professionnelle du nageur est à jour pour la saison en cours.</em>
            </p>
            <p>À très bientôt dans l'eau ! 🏊‍♂️</p>
            <p>L'équipe AquaCoach</p>
        </body>
        </html>
        """

        msg_client.attach(MIMEText(html_client, "html", "utf-8"))
        server.send_message(msg_client)
        print(f"✅ Email CLIENT envoyé")

        # EMAIL 2 : À l'admin
        msg_admin = MIMEMultipart("alternative")
        msg_admin["Subject"] = f"Nouveau paiement - {client_prenom} {client_nom}"
        msg_admin["From"] = f"{MAILJET_FROM_NAME} <{MAILJET_FROM_EMAIL}>"
        msg_admin["To"] = ADMIN_EMAIL

        html_admin = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #3fb0ac;">💰 Nouveau Paiement</h2>
            <p><strong>M. {client_nom} {client_prenom}</strong> a acheté des frais de dossier ({montant}) 
            et a choisi <strong>{nageur_prenom} {nageur_nom}</strong> comme coach.</p>
            <h3>Informations Client</h3>
            <ul>
                <li><strong>Nom :</strong> {client_prenom} {client_nom}</li>
                <li><strong>Email :</strong> {client_email}</li>
            </ul>
            <h3>Coach sélectionné</h3>
            <ul>
                <li><strong>Nom :</strong> {nageur_prenom} {nageur_nom}</li>
                <li><strong>Ville :</strong> {nageur_ville}</li>
                <li><strong>Email :</strong> {nageur_email}</li>
                <li><strong>Téléphone :</strong> {nageur_tel}</li>
            </ul>
            <h3>Transaction</h3>
            <ul>
                <li><strong>Montant :</strong> {montant}</li>
                <li><strong>Code :</strong> {code_validation}</li>
                <li><strong>Date :</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}</li>
            </ul>
        </body>
        </html>
        """

        msg_admin.attach(MIMEText(html_admin, "html", "utf-8"))
        server.send_message(msg_admin)
        server.quit()
        print(f"✅ Email ADMIN envoyé")
        print(f"📧 Code: {code_validation}\n")

        return code_validation

    except Exception as e:
        print(f"❌ ERREUR EMAIL: {e}\n")
        import traceback

        traceback.print_exc()
        return None


def send_nageur_inscription_email(
    nageur_prenom,
    nageur_nom,
    nageur_email,
    nageur_tel,
    nageur_ville,
    nageur_dept,
    nageur_diplome,
    nageur_tarif
):
    """Envoie un email de confirmation d'inscription au nageur et à l'admin"""
    print(f"\n🔔 ENVOI D'EMAIL INSCRIPTION NAGEUR")
    print(f"   Nageur: {nageur_prenom} {nageur_nom} <{nageur_email}>")

    try:
        # Connexion SMTP
        print(f"📤 Connexion à Mailjet...")
        server = smtplib.SMTP(MAILJET_HOST, MAILJET_PORT, timeout=30)
        server.starttls()
        server.login(MAILJET_USERNAME, MAILJET_PASSWORD)

        # EMAIL 1 : Au nageur
        msg_nageur = MIMEMultipart("alternative")
        msg_nageur["Subject"] = "Bienvenue sur AquaCoach - Inscription confirmée !"
        msg_nageur["From"] = f"{MAILJET_FROM_NAME} <{MAILJET_FROM_EMAIL}>"
        msg_nageur["To"] = nageur_email

        html_nageur = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #3fb0ac; border-bottom: 3px solid #3fb0ac; padding-bottom: 10px;">
                    🌊 Bienvenue sur AquaCoach !
                </h2>
                
                <p>Bonjour <strong>{nageur_prenom} {nageur_nom}</strong>,</p>
                
                <p style="font-size: 1.1em; background: #f0f9ff; padding: 15px; border-left: 4px solid #3fb0ac;">
                    🎉 <strong>Félicitations !</strong> Votre inscription en tant que maître-nageur sur AquaCoach a été confirmée.
                </p>
                
                <h3 style="color: #3fb0ac; margin-top: 30px;">📋 Récapitulatif de votre profil :</h3>
                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 15px 0;">
                    <ul style="list-style: none; padding: 0;">
                        <li style="padding: 8px 0;"><strong>👤 Nom :</strong> {nageur_prenom} {nageur_nom}</li>
                        <li style="padding: 8px 0;"><strong>📧 Email :</strong> {nageur_email}</li>
                        <li style="padding: 8px 0;"><strong>📞 Téléphone :</strong> {nageur_tel}</li>
                        <li style="padding: 8px 0;"><strong>📍 Ville :</strong> {nageur_ville} ({nageur_dept})</li>
                        <li style="padding: 8px 0;"><strong>🎓 Diplôme :</strong> {nageur_diplome or 'Non renseigné'}</li>
                        <li style="padding: 8px 0;"><strong>💰 Tarif :</strong> {nageur_tarif}€/séance</li>
                    </ul>
                </div>
                
                <h3 style="color: #3fb0ac; margin-top: 30px;">🚀 Que se passe-t-il maintenant ?</h3>
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 10px 0;">
                        🔑 <strong>Accédez à votre espace :</strong> Vous pouvez vous connecter à votre espace personnel pour modifier votre profil à tout moment :<br>
                        <a href="https://aquacoach.fr/nageur/login" style="color: #3fb0ac; font-weight: bold;">Accéder à mon Espace Maître-Nageur</a>
                    </p>
                    <p style="margin: 10px 0;">
                        ✅ <strong>Votre profil est maintenant visible</strong> par tous les clients cherchant un maître-nageur dans le département <strong>{nageur_dept}</strong>.
                    </p>
                    <p style="margin: 10px 0;">
                        📱 <strong>Vous serez contacté directement</strong> par les clients intéressés par vos services via l'email <strong>{nageur_email}</strong> et le téléphone <strong>{nageur_tel}</strong>.
                    </p>
                    <p style="margin: 10px 0;">
                        💼 <strong>Aucune commission</strong> n'est prélevée sur vos cours - vous gérez directement la relation avec vos clients.
                    </p>
                </div>
                
                <h3 style="color: #3fb0ac; margin-top: 30px;">💡 Conseils pour réussir :</h3>
                <ul style="line-height: 1.8;">
                    <li>📸 <strong>Ajoutez une photo professionnelle</strong> pour inspirer confiance</li>
                    <li>📝 <strong>Complétez votre présentation</strong> pour vous démarquer</li>
                    <li>📅 <strong>Indiquez vos disponibilités</strong> clairement</li>
                    <li>⚡ <strong>Répondez rapidement</strong> aux demandes pour maximiser vos chances</li>
                </ul>
                
                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
                    <p style="font-size: 1.2em; margin: 0;">
                        <strong>🎯 Prêt à partager votre passion de la natation ?</strong>
                    </p>
                    <p style="margin: 10px 0;">
                        Les premiers clients vont bientôt vous contacter !
                    </p>
                </div>
                
                <p style="margin-top: 30px;">Si vous avez des questions, n'hésitez pas à nous contacter.</p>
                
                <p style="margin-top: 20px;">
                    À très bientôt dans l'eau ! 🏊‍♂️<br>
                    <strong>L'équipe AquaCoach</strong>
                </p>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; text-align: center; color: #999; font-size: 0.9em;">
                    <p>AquaCoach - La plateforme qui connecte les passionnés de natation</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_nageur = f"""
Bienvenue sur AquaCoach !

Bonjour {nageur_prenom} {nageur_nom},

Félicitations ! Votre inscription en tant que maître-nageur sur AquaCoach a été confirmée.

RÉCAPITULATIF :
- Nom : {nageur_prenom} {nageur_nom}
- Email : {nageur_email}
- Téléphone : {nageur_tel}
- Ville : {nageur_ville} ({nageur_dept})
- Diplôme : {nageur_diplome or 'Non renseigné'}
- Tarif : {nageur_tarif}€/séance

QUE SE PASSE-T-IL MAINTENANT ?

🔑 Votre Espace Maître-Nageur : https://aquacoach.fr/nageur/login

✓ Votre profil est maintenant visible par tous les clients cherchant un maître-nageur dans le département {nageur_dept}.
✓ Vous serez contacté directement par les clients intéressés.
✓ Aucune commission n'est prélevée sur vos cours.

CONSEILS :
- Ajoutez une photo professionnelle
- Complétez votre présentation
- Répondez rapidement aux demandes

À très bientôt dans l'eau !
L'équipe AquaCoach
        """

        msg_nageur.attach(MIMEText(text_nageur, "plain", "utf-8"))
        msg_nageur.attach(MIMEText(html_nageur, "html", "utf-8"))
        server.send_message(msg_nageur)
        print(f"✅ Email NAGEUR envoyé à {nageur_email}")

        # EMAIL 2 : À l'admin
        msg_admin = MIMEMultipart("alternative")
        msg_admin["Subject"] = f"Nouvelle inscription nageur - {nageur_prenom} {nageur_nom}"
        msg_admin["From"] = f"{MAILJET_FROM_NAME} <{MAILJET_FROM_EMAIL}>"
        msg_admin["To"] = ADMIN_EMAIL

        html_admin = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #3fb0ac;">🏊‍♂️ Nouvelle Inscription Maître-Nageur</h2>
            <p><strong>{nageur_prenom} {nageur_nom}</strong> vient de s'inscrire sur AquaCoach.</p>
            
            <h3 style="color: #3fb0ac;">Informations :</h3>
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
                <ul style="line-height: 1.8;">
                    <li><strong>Nom :</strong> {nageur_prenom} {nageur_nom}</li>
                    <li><strong>Email :</strong> <a href="mailto:{nageur_email}">{nageur_email}</a></li>
                    <li><strong>Téléphone :</strong> {nageur_tel}</li>
                    <li><strong>Ville :</strong> {nageur_ville}</li>
                    <li><strong>Département :</strong> {nageur_dept}</li>
                    <li><strong>Diplôme :</strong> {nageur_diplome or 'Non renseigné'}</li>
                    <li><strong>Tarif :</strong> {nageur_tarif}€/séance</li>
                </ul>
            </div>
            
            <p style="margin-top: 20px;">
                <a href="https://aquacoach.fr/admin/login" style="display: inline-block; background-color: #3fb0ac; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Accéder à l'interface Admin
                </a>
            </p>
            <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                Vérifiez le profil dans l'interface admin si nécessaire.
            </p>
        </body>
        </html>
        """

        msg_admin.attach(MIMEText(html_admin, "html", "utf-8"))
        server.send_message(msg_admin)
        print(f"✅ Email ADMIN envoyé à {ADMIN_EMAIL}")

        server.quit()
        print("✅ Tous les emails d'inscription nageur envoyés")
        return True

    except Exception as e:
        print(f"❌ ERREUR EMAIL INSCRIPTION NAGEUR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def send_nageur_update_email(nageur_prenom, nageur_nom, nageur_email):
    """Envoie un email de remerciement au nageur après modification de son profil"""
    print(f"\n🔔 ENVOI D'EMAIL MODIFICATION NAGEUR")
    print(f"   Nageur: {nageur_prenom} {nageur_nom} <{nageur_email}>")

    try:
        # Connexion SMTP
        server = smtplib.SMTP(MAILJET_HOST, MAILJET_PORT, timeout=30)
        server.starttls()
        server.login(MAILJET_USERNAME, MAILJET_PASSWORD)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Mise à jour de votre profil - AquaCoach"
        msg["From"] = f"{MAILJET_FROM_NAME} <{MAILJET_FROM_EMAIL}>"
        msg["To"] = nageur_email

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #3fb0ac; border-bottom: 3px solid #3fb0ac; padding-bottom: 10px;">
                    ✅ Profil mis à jour !
                </h2>
                <p>Bonjour <strong>{nageur_prenom} {nageur_nom}</strong>,</p>
                <p>Nous vous confirmons que les modifications apportées à votre profil AquaCoach ont bien été enregistrées.</p>
                <p>Merci de maintenir vos informations à jour pour les futurs clients.</p>
                
                <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3fb0ac;">
                    <p style="margin: 0;">
                        🔗 <strong>Votre espace :</strong> <a href="https://aquacoach.fr/nageur/login" style="color: #3fb0ac; font-weight: bold;">Accéder à mon Espace Maître-Nageur</a>
                    </p>
                </div>

                <p>À très bientôt dans l'eau ! 🏊‍♂️<br>
                <strong>L'équipe AquaCoach</strong></p>
            </div>
        </body>
        </html>
        """
        
        text = f"""
Bonjour {nageur_prenom} {nageur_nom},

Nous vous confirmons que les modifications apportées à votre profil AquaCoach ont bien été enregistrées.
Merci de maintenir vos informations à jour pour les futurs clients.

Votre espace : https://aquacoach.fr/nageur/login

À très bientôt dans l'eau !
L'équipe AquaCoach
        """

        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        server.send_message(msg)
        server.quit()
        print(f"✅ Email de mise à jour envoyé à {nageur_email}")
        return True

    except Exception as e:
        print(f"❌ ERREUR EMAIL MISE À JOUR NAGEUR: {e}\n")
        return False


def send_client_inscription_email(client_prenom, client_nom, client_email, client_tel, client_ville, client_dept):
    """Envoie un email à l'admin quand un nouveau client s'inscrit"""
    print(f"\n🔔 ENVOI D'EMAIL INSCRIPTION CLIENT")
    print(f"   Client: {client_prenom} {client_nom} <{client_email}>")

    try:
        # Connexion SMTP
        server = smtplib.SMTP(MAILJET_HOST, MAILJET_PORT, timeout=30)
        server.starttls()
        server.login(MAILJET_USERNAME, MAILJET_PASSWORD)

        # Email à l'admin
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🆕 Nouveau client inscrit : {client_prenom} {client_nom}"
        msg["From"] = f"{MAILJET_FROM_NAME} <{MAILJET_FROM_EMAIL}>"
        msg["To"] = ADMIN_EMAIL

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #3fb0ac; border-bottom: 3px solid #3fb0ac; padding-bottom: 10px;">
                    🆕 Nouveau Client Inscrit !
                </h2>

                <p>Un nouveau client vient de s'inscrire sur AquaCoach :</p>

                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 15px 0;">
                    <ul style="list-style: none; padding: 0;">
                        <li style="padding: 8px 0;"><strong>👤 Nom :</strong> {client_prenom} {client_nom}</li>
                        <li style="padding: 8px 0;"><strong>📧 Email :</strong> {client_email}</li>
                        <li style="padding: 8px 0;"><strong>📞 Téléphone :</strong> {client_tel}</li>
                        <li style="padding: 8px 0;"><strong>📍 Localisation :</strong> {client_ville} ({client_dept})</li>
                    </ul>
                </div>

                <p style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    ⏳ <strong>En attente d'achat</strong> - Ce client n'a pas encore acheté de prestation.
                </p>

                <p>
                    🔗 <a href="https://aquacoach.fr/admin" style="color: #3fb0ac; font-weight: bold;">Accéder à l'administration</a>
                </p>

                <p>L'équipe AquaCoach 🌊</p>
            </div>
        </body>
        </html>
        """

        text = f"""
Nouveau client inscrit sur AquaCoach !

Nom : {client_prenom} {client_nom}
Email : {client_email}
Téléphone : {client_tel}
Localisation : {client_ville} ({client_dept})

⏳ En attente d'achat - Ce client n'a pas encore acheté de prestation.

Administration : https://aquacoach.fr/admin
        """

        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        server.send_message(msg)
        server.quit()
        print(f"✅ Email inscription client envoyé à {ADMIN_EMAIL}")
        return True

    except Exception as e:
        print(f"❌ ERREUR EMAIL INSCRIPTION CLIENT: {e}\n")
        return False


# ============================================
# AUTHENTICATION
# ============================================


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session:
            flash("Veuillez vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated_function


def nageur_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "nageur_id" not in session:
            flash("Veuillez vous connecter à votre espace Maître-Nageur.", "warning")
            return redirect(url_for("nageur_login"))
        return f(*args, **kwargs)

    return decorated_function


# ============================================
# DATABASE FUNCTIONS
# ============================================


def get_db():
    if DB_HOST:
        # Connexion MySQL (o2switch)
        db = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return db
    else:
        # Connexion SQLite (local)
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        return db


def query_db(query, args=(), one=False):
    db = get_db()
    
    # Adapter le placeholder selon la base
    if DB_HOST:
        query = query.replace('?', '%s')
        
    try:
        if DB_HOST:
            with db.cursor() as cursor:
                cursor.execute(query, args)
                rv = cursor.fetchall()
        else:
            cur = db.execute(query, args)
            rv = cur.fetchall()
            db.commit()
            
        return (rv[0] if rv else None) if one else rv
    finally:
        db.close()


def execute_db(query, args=()):
    db = get_db()
    
    # Adapter le placeholder selon la base
    if DB_HOST:
        query = query.replace('?', '%s')
        
    try:
        if DB_HOST:
            with db.cursor() as cursor:
                cursor.execute(query, args)
                db.commit()  # IMPORTANT: Commit pour MySQL
                last_id = cursor.lastrowid
        else:
            cur = db.execute(query, args)
            db.commit()
            last_id = cur.lastrowid
        return last_id
    except Exception as e:
        if DB_HOST:
            db.rollback()
        raise e
    finally:
        db.close()


def save_strava_connection(token_data, accepted_scope):
    """Enregistre les informations Strava et les jetons cote serveur."""
    athlete = token_data.get("athlete") or {}
    athlete_id = str(athlete.get("id") or "")

    if not athlete_id:
        raise ValueError("Identifiant athlete Strava manquant")

    existing_athlete = query_db(
        "SELECT athlete_id FROM strava_athlete WHERE athlete_id = ?",
        (athlete_id,),
        one=True,
    )
    athlete_values = (
        athlete.get("firstname", ""),
        athlete.get("lastname", ""),
        athlete.get("profile", ""),
        athlete.get("city", ""),
        athlete.get("country", ""),
        accepted_scope or token_data.get("scope", ""),
    )

    if existing_athlete:
        execute_db(
            """
            UPDATE strava_athlete
            SET firstname = ?, lastname = ?, profile = ?, city = ?, country = ?,
                scope = ?, updated_at = CURRENT_TIMESTAMP
            WHERE athlete_id = ?
            """,
            athlete_values + (athlete_id,),
        )
    else:
        execute_db(
            """
            INSERT INTO strava_athlete
                (athlete_id, firstname, lastname, profile, city, country, scope)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (athlete_id,) + athlete_values,
        )

    existing_token = query_db(
        "SELECT athlete_id FROM strava_token WHERE athlete_id = ?",
        (athlete_id,),
        one=True,
    )
    token_values = (
        token_data["access_token"],
        token_data["refresh_token"],
        int(token_data["expires_at"]),
        token_data.get("token_type", "Bearer"),
    )

    if existing_token:
        execute_db(
            """
            UPDATE strava_token
            SET access_token = ?, refresh_token = ?, expires_at = ?,
                token_type = ?, updated_at = CURRENT_TIMESTAMP
            WHERE athlete_id = ?
            """,
            token_values + (athlete_id,),
        )
    else:
        execute_db(
            """
            INSERT INTO strava_token
                (athlete_id, access_token, refresh_token, expires_at, token_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (athlete_id,) + token_values,
        )

    return athlete_id, athlete


def get_valid_strava_token(athlete_id):
    """Retourne un jeton Strava valide et le rafraichit si necessaire."""
    token = query_db(
        "SELECT * FROM strava_token WHERE athlete_id = ?",
        (athlete_id,),
        one=True,
    )
    if not token:
        return None

    if int(token["expires_at"]) > int(datetime.now().timestamp()) + 60:
        return token["access_token"]

    response = requests.post(
        STRAVA_TOKEN_URL,
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "AquaCoach/1.0 (+https://aquacoach.fr)",
        },
        timeout=20,
    )
    response.raise_for_status()
    refreshed = response.json()

    execute_db(
        """
        UPDATE strava_token
        SET access_token = ?, refresh_token = ?, expires_at = ?,
            token_type = ?, updated_at = CURRENT_TIMESTAMP
        WHERE athlete_id = ?
        """,
        (
            refreshed["access_token"],
            refreshed["refresh_token"],
            int(refreshed["expires_at"]),
            refreshed.get("token_type", "Bearer"),
            athlete_id,
        ),
    )
    return refreshed["access_token"]


def format_activity(activity):
    """Prepare une activite Strava pour son affichage."""
    type_labels = {
        "Ride": "Velo",
        "VirtualRide": "Velo virtuel",
        "Run": "Course",
        "Walk": "Marche",
        "Hike": "Randonnee",
        "Swim": "Natation",
        "Workout": "Entrainement",
        "WeightTraining": "Musculation",
        "Yoga": "Yoga",
    }
    started_at = activity.get("start_date_local") or activity.get("start_date")
    try:
        activity_date = datetime.strptime(started_at[:19], "%Y-%m-%dT%H:%M:%S")
        date_label = activity_date.strftime("%d/%m/%Y a %H:%M")
    except (TypeError, ValueError):
        date_label = "Date inconnue"

    moving_seconds = int(activity.get("moving_time") or 0)
    hours, remainder = divmod(moving_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        duration_label = "{} h {:02d}".format(hours, minutes)
    else:
        duration_label = "{} min {:02d}".format(minutes, seconds)

    return {
        "id": activity.get("id"),
        "name": activity.get("name") or "Activite Strava",
        "type": type_labels.get(
            activity.get("sport_type") or activity.get("type"),
            activity.get("sport_type") or activity.get("type") or "Activite",
        ),
        "date": date_label,
        "distance": round(float(activity.get("distance") or 0) / 1000, 2),
        "duration": duration_label,
        "elevation": round(float(activity.get("total_elevation_gain") or 0)),
        "average_heartrate": activity.get("average_heartrate"),
        "private": bool(activity.get("private")),
    }


def init_db():
    print("🛠️ Initialisation de la base de données...")
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    db = get_db()
    
    # Syntaxe adaptée selon la base
    auto_inc = "AUTO_INCREMENT" if DB_HOST else "AUTOINCREMENT"
    pk_type = "INT PRIMARY KEY" if DB_HOST else "INTEGER PRIMARY KEY"
    
    queries = [
        f"""
        CREATE TABLE IF NOT EXISTS article (
            id {pk_type} {auto_inc},
            titre TEXT NOT NULL,
            slug VARCHAR(255) UNIQUE NOT NULL,
            resume TEXT,
            contenu TEXT NOT NULL,
            image TEXT,
            date_publication DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_published INTEGER DEFAULT 1
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS nageur (
            id {pk_type} {auto_inc},
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT NOT NULL,
            tel TEXT NOT NULL,
            ville TEXT NOT NULL,
            dept TEXT NOT NULL,
            diplome TEXT,
            presentation TEXT,
            disponibilites TEXT,
            tarif REAL,
            photo TEXT,
            preferences TEXT,
            sexe TEXT,
            login VARCHAR(100) UNIQUE,
            password_hash TEXT,
            carte_pro_photo TEXT,
            is_active INTEGER DEFAULT 1,
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS client (
            id {pk_type} {auto_inc},
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT NOT NULL,
            tel TEXT NOT NULL,
            ville TEXT NOT NULL,
            dept TEXT NOT NULL,
            login VARCHAR(100) UNIQUE,
            password_hash TEXT,
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS selection (
            id {pk_type} {auto_inc},
            client_id INTEGER NOT NULL,
            nageur_id INTEGER NOT NULL,
            date_selection DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS strava_athlete (
            athlete_id VARCHAR(32) PRIMARY KEY,
            firstname VARCHAR(120),
            lastname VARCHAR(120),
            profile TEXT,
            city VARCHAR(160),
            country VARCHAR(160),
            scope TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS strava_token (
            athlete_id VARCHAR(32) PRIMARY KEY,
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            expires_at BIGINT NOT NULL,
            token_type VARCHAR(32) DEFAULT 'Bearer',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    try:
        if DB_HOST:
            with db.cursor() as cursor:
                # Créer les tables si elles n'existent pas
                for q in queries:
                    cursor.execute(q)
                
                # Migration : Ajouter les nouvelles colonnes si elles n'existent pas
                try:
                    cursor.execute("SELECT carte_pro_photo FROM nageur LIMIT 1")
                except Exception as e:
                    db.rollback() 
                    print(f"🚀 Migration : Ajout de la colonne carte_pro_photo")
                    with db.cursor() as alt_cursor:
                        alt_cursor.execute("ALTER TABLE nageur ADD COLUMN carte_pro_photo TEXT")
                
                try:
                    cursor.execute("SELECT is_active FROM nageur LIMIT 1")
                except Exception as e:
                    db.rollback()
                    print(f"🚀 Migration : Ajout de la colonne is_active")
                    with db.cursor() as alt_cursor:
                        alt_cursor.execute("ALTER TABLE nageur ADD COLUMN is_active INTEGER DEFAULT 1")
        else:
            for q in queries:
                db.execute(q)
            
            # Migration SQLite
            try:
                db.execute("SELECT carte_pro_photo FROM nageur LIMIT 1")
            except sqlite3.OperationalError:
                print("🚀 Migration SQLite : Ajout de la colonne carte_pro_photo")
                db.execute("ALTER TABLE nageur ADD COLUMN carte_pro_photo TEXT")
            
            try:
                db.execute("SELECT is_active FROM nageur LIMIT 1")
            except sqlite3.OperationalError:
                print("🚀 Migration SQLite : Ajout de la colonne is_active")
                db.execute("ALTER TABLE nageur ADD COLUMN is_active INTEGER DEFAULT 1")
            
            db.commit()
        print("✅ Base de données initialisée et migrée")
    except Exception as e:
        print(f"⚠️ Erreur initialisation BDD: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


# ============================================
# ROUTES
# ============================================


@app.route("/")
def index():
    # Récupérer les derniers nageurs actifs et clients pour la page d'accueil
    nageurs = query_db("SELECT * FROM nageur WHERE is_active = 1 ORDER BY date_inscription DESC LIMIT 6")
    clients = query_db("SELECT * FROM client ORDER BY date_inscription DESC LIMIT 3")
    return render_template("index.html", nageurs=nageurs, clients=clients)


@app.route("/strava")
def strava_login():
    """Page publique de connexion Strava."""
    return render_template(
        "strava_login.html",
        strava_configured=bool(STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET),
    )


@app.route("/strava/connect")
def strava_connect():
    """Demarre le parcours OAuth Strava."""
    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
        flash(
            "La connexion Strava n'est pas encore configuree sur le serveur.",
            "danger",
        )
        return redirect(url_for("strava_login"))

    state = secrets.token_urlsafe(32)
    session["strava_oauth_state"] = state

    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": STRAVA_REDIRECT_URI,
        "response_type": "code",
        "approval_prompt": "force",
        "scope": STRAVA_SCOPE,
        "state": state,
    }
    return redirect(f"{STRAVA_AUTHORIZE_URL}?{urlencode(params)}")


@app.route("/auth/callback")
def strava_callback():
    """Recoit le code Strava et l'echange contre les jetons OAuth."""
    error = request.args.get("error")
    if error:
        flash("La connexion Strava a ete annulee.", "warning")
        return redirect(url_for("strava_login"))

    code = request.args.get("code")
    returned_state = request.args.get("state", "")
    expected_state = session.pop("strava_oauth_state", "")

    if (
        not code
        or not expected_state
        or not secrets.compare_digest(returned_state, expected_state)
    ):
        flash("La verification de securite Strava a echoue. Reessayez.", "danger")
        return redirect(url_for("strava_login"))

    try:
        response = requests.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id": STRAVA_CLIENT_ID,
                "client_secret": STRAVA_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
            },
            headers={
                "Accept": "application/json",
                "User-Agent": "AquaCoach/1.0 (+https://aquacoach.fr)",
            },
            timeout=20,
        )
        response.raise_for_status()
        token_data = response.json()
        athlete_id, athlete = save_strava_connection(
            token_data,
            request.args.get("scope", ""),
        )
    except (requests.RequestException, ValueError, KeyError) as exc:
        app.logger.error("Echec OAuth Strava: %s", exc)
        flash(
            "Strava a autorise l'acces, mais le serveur n'a pas pu finaliser la connexion.",
            "danger",
        )
        return redirect(url_for("strava_login"))

    session["strava_athlete_id"] = athlete_id
    return render_template("strava_success.html", athlete=athlete)


@app.route("/strava/activities")
def strava_activities():
    """Affiche les dernieres activites du compte Strava connecte."""
    athlete_id = session.get("strava_athlete_id")
    if not athlete_id:
        flash("Connectez d'abord votre compte Strava.", "warning")
        return redirect(url_for("strava_login"))

    athlete = query_db(
        "SELECT * FROM strava_athlete WHERE athlete_id = ?",
        (athlete_id,),
        one=True,
    )

    try:
        access_token = get_valid_strava_token(athlete_id)
        if not access_token:
            raise ValueError("Jeton Strava introuvable")

        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            params={"page": 1, "per_page": 30},
            headers={
                "Authorization": "Bearer {}".format(access_token),
                "Accept": "application/json",
                "User-Agent": "AquaCoach/1.0 (+https://aquacoach.fr)",
            },
            timeout=20,
        )
        response.raise_for_status()
        activities = [format_activity(item) for item in response.json()]
    except (requests.RequestException, ValueError, KeyError) as exc:
        app.logger.error("Echec lecture activites Strava: %s", exc)
        flash(
            "Impossible de charger vos activites Strava. Reconnectez votre compte.",
            "danger",
        )
        return redirect(url_for("strava_login"))

    totals = {
        "count": len(activities),
        "distance": round(sum(item["distance"] for item in activities), 1),
        "elevation": int(sum(item["elevation"] for item in activities)),
    }
    return render_template(
        "strava_activities.html",
        athlete=athlete,
        activities=activities,
        totals=totals,
    )


@app.route("/inscription_client")
def inscription_client():
    return render_template("inscription_client.html", departements=DEPARTEMENTS)


@app.route("/submit_inscription_client", methods=["POST"])
def submit_inscription_client():
    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    email = request.form.get("email")
    tel = request.form.get("tel")
    ville = request.form.get("ville")
    dept = request.form.get("dept")

    client_id = execute_db(
        """
        INSERT INTO client (nom, prenom, email, tel, ville, dept)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (nom, prenom, email, tel, ville, dept),
    )

    session["client_id"] = client_id
    session["client_dept"] = dept

    # Envoyer un email à l'admin pour notifier de l'inscription
    send_client_inscription_email(prenom, nom, email, tel, ville, dept)

    return redirect(url_for("choix_nageur"))


@app.route("/client/login", methods=["GET", "POST"])
def client_login():
    """Page de connexion client"""
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        client = query_db("SELECT * FROM client WHERE login = ?", (login,), one=True)

        if client and check_password_hash(client["password_hash"], password):
            session["client_id"] = client["id"]
            session["client_dept"] = client["dept"]
            session["client_logged_in"] = True
            session["client_login"] = client["login"]
            
            flash(f"Bienvenue {client['prenom']} ! Vous êtes connecté.", "success")
            return redirect(url_for("choix_nageur"))
        else:
            flash("Identifiants incorrects", "danger")

    return render_template("client_login.html")


@app.route("/client/logout")
def client_logout():
    """Déconnexion client"""
    session.pop("client_id", None)
    session.pop("client_dept", None)
    session.pop("client_logged_in", None)
    session.pop("client_login", None)
    session.pop("nageur_id", None)
    
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for("index"))


@app.route("/choix_nageur", methods=["GET", "POST"])
def choix_nageur():
    if request.method == "POST":
        nageur_ids = request.form.getlist("nageur_ids")  # Récupérer la liste des IDs
        if not nageur_ids:
            flash("Veuillez sélectionner au moins un maître-nageur", "danger")
            return redirect(url_for("choix_nageur"))
        
        session["nageur_ids"] = nageur_ids  # Stocker la liste
        return redirect(url_for("confirmation_paiement"))

    if "client_dept" not in session:
        return redirect(url_for("inscription_client"))

    nageurs = query_db("SELECT * FROM nageur WHERE dept = ? AND is_active = 1", (session["client_dept"],))

    return render_template("choix_nageur.html", nageurs=nageurs, dept=session["client_dept"])


# Configuration Stripe (TEST ou PRODUCTION)
STRIPE_TEST_MODE = False  # Mettez à False pour passer en production réellle

# Liens de PRODUCTION
LIENS_PROD = {
    1: "https://buy.stripe.com/4gM8wQ6IfbWIf2m2JDe7m0d",
    2: "https://buy.stripe.com/fZudRa0jR7Gs2fAfwpe7m0e",
    3: "https://buy.stripe.com/fZu4gA0jR3qc07sdohe7m0f",
    4: "https://buy.stripe.com/8x29AU4A7gcY8DY5VPe7m0g",
    5: "https://buy.stripe.com/fZu7sMd6DaSE7zU2JDe7m0h",
    6: "https://buy.stripe.com/4gM9AU8QnbWI8DYfwpe7m0i",
    7: "https://buy.stripe.com/8x2aEYc2z8Kw6vQfwpe7m0j",
    8: "https://buy.stripe.com/aFa9AUaYv1i4bQackde7m0k",
    9: "https://buy.stripe.com/fZufZi3w3e4Q5rMfwpe7m0l",
    10: "https://buy.stripe.com/14AdRac2z3qc7zUfwpe7m0m"
}

# Liens de TEST
LIENS_TEST = {
    1: "https://buy.stripe.com/test_4gM8wQ6IfbWIf2m2JDe7m0d",
    2: "https://buy.stripe.com/test_fZudRa0jR7Gs2fAfwpe7m0e",
    3: "https://buy.stripe.com/test_fZu4gA0jR3qc07sdohe7m0f",
    4: "https://buy.stripe.com/test_8x29AU4A7gcY8DY5VPe7m0g",
    5: "https://buy.stripe.com/test_fZu7sMd6DaSE7zU2JDe7m0h",
    6: "https://buy.stripe.com/test_4gM9AU8QnbWI8DYfwpe7m0i",
    7: "https://buy.stripe.com/test_8x2aEYc2z8Kw6vQfwpe7m0j",
    8: "https://buy.stripe.com/test_aFa9AUaYv1i4bQackde7m0k",
    9: "https://buy.stripe.com/test_fZufZi3w3e4Q5rMfwpe7m0l",
    10: "https://buy.stripe.com/test_14AdRac2z3qc7zUfwpe7m0m"
}

@app.route("/confirmation_paiement")
def confirmation_paiement():
    """Page de confirmation avant paiement via multi-liens Stripe"""
    if "nageur_ids" not in session or "client_id" not in session:
        return redirect(url_for("index"))

    # Récupérer tous les nageurs sélectionnés
    nageur_ids = session["nageur_ids"]
    nombre = len(nageur_ids)
    placeholders = ','.join(['?'] * nombre)
    nageurs = query_db(f"SELECT * FROM nageur WHERE id IN ({placeholders})", nageur_ids)
    
    client = query_db("SELECT * FROM client WHERE id = ?", (session["client_id"],), one=True)

    if not nageurs or not client:
        flash("Erreur lors de la récupération des informations", "danger")
        return redirect(url_for("index"))

    # Choisir le dictionnaire selon le mode
    liens = LIENS_TEST if STRIPE_TEST_MODE else LIENS_PROD
    
    # Récupérer le lien correspondant au nombre
    base_url = liens.get(nombre, liens[1])
    
    # On ajoute client_reference_id et prefilled_email pour le suivi
    stripe_link = f"{base_url}?client_reference_id={session['client_id']}&prefilled_email={client['email']}"

    return render_template(
        "confirmation_paiement.html",
        nageurs=nageurs,
        total=nombre * 5.00,
        count=nombre,
        stripe_link=stripe_link,
        test_mode=STRIPE_TEST_MODE
    )


@app.route("/paiement_valide")
def paiement_valide():
    """Route de succès automatique après paiement Stripe"""
    if "nageur_ids" not in session or "client_id" not in session:
        flash("Session expirée. Vos sélections ont peut-être déjà été traitées.", "info")
        return redirect(url_for("index"))

    nageur_ids = session["nageur_ids"]
    placeholders = ','.join(['?'] * len(nageur_ids))
    nageurs = query_db(f"SELECT * FROM nageur WHERE id IN ({placeholders})", nageur_ids)
    client = query_db("SELECT * FROM client WHERE id = ?", (session["client_id"],), one=True)

    if not nageurs or not client:
        return redirect(url_for("index"))

    # 1. Enregistrer les sélections en base de données
    for nageur_id in nageur_ids:
        execute_db(
            "INSERT INTO selection (client_id, nageur_id, date_selection) VALUES (?, ?, ?)",
            (session["client_id"], nageur_id, datetime.now()),
        )

    # 2. Envoyer les emails de mise en relation
    for nageur in nageurs:
        send_confirmation_email(
            client_email=client["email"],
            client_prenom=client["prenom"],
            client_nom=client["nom"],
            nageur_prenom=nageur["prenom"],
            nageur_nom=nageur["nom"],
            nageur_email=nageur["email"],
            nageur_tel=nageur["tel"],
            nageur_ville=nageur["ville"],
            montant="5,00 €",
        )

    total = len(nageurs) * 5.00
    code_validation = f"AQ{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 3. Nettoyer la session
    session.pop("nageur_ids", None)
    session.pop("client_id", None)
    session.pop("client_dept", None)

    return render_template(
        "success.html",
        client_prenom=client["prenom"],
        client_nom=client["nom"],
        nageurs=nageurs,
        total=total,
        count=len(nageurs),
        code_validation=code_validation,
    )


@app.route("/contact")
def contact():
    """Page de contact"""
    return render_template("contact.html")


@app.route("/mentions-legales")
def mentions_legales():
    """Page des mentions légales"""
    return render_template("mentions_legales.html")


@app.route("/politique-confidentialite")
def politique_confidentialite():
    """Page de la politique de confidentialité"""
    return render_template("politique_confidentialite.html")


@app.route("/robots.txt")
def robots():
    """Fichier robots.txt pour le SEO"""
    return app.send_static_file("robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    """Sitemap XML pour le SEO"""
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://aquacoach.fr/</loc>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://aquacoach.fr/blog</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://aquacoach.fr/inscription_nageur</loc>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://aquacoach.fr/inscription_client</loc>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://aquacoach.fr/nageur/login</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://aquacoach.fr/contact</loc>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://aquacoach.fr/mentions-legales</loc>
        <changefreq>yearly</changefreq>
        <priority>0.3</priority>
    </url>
    <url>
        <loc>https://aquacoach.fr/politique-confidentialite</loc>
        <changefreq>yearly</changefreq>
        <priority>0.3</priority>
    </url>
</urlset>"""
    return sitemap_xml, 200, {'Content-Type': 'application/xml'}


@app.route("/submit_contact", methods=["POST"])
def submit_contact():
    """Traiter le formulaire de contact"""
    nom = request.form.get("nom")
    email = request.form.get("email")
    ville = request.form.get("ville")
    sujet = request.form.get("sujet")
    message = request.form.get("message")

    if not nom or not email or not message:
        flash("Veuillez remplir tous les champs obligatoires.", "danger")
        return redirect(url_for("contact"))

    # Préparer le contenu de l'email pour l'admin
    email_body = f"""
    NOUVEAU MESSAGE DE CONTACT - AQUACOACH
    
    Nom : {nom}
    Email : {email}
    Ville : {ville if ville else 'Non précisée'}
    Sujet : {sujet if sujet else 'Sans sujet'}
    
    Message :
    {message}
    """

    try:
        # Envoyer l'email à l'admin
        msg = MIMEMultipart()
        msg["From"] = f"{MAILJET_FROM_NAME} <{MAILJET_FROM_EMAIL}>"
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = f"NOUVEAU CONTACT : {sujet if sujet else 'Message de ' + nom}"

        msg.attach(MIMEText(email_body, "plain"))

        with smtplib.SMTP(MAILJET_HOST, MAILJET_PORT) as server:
            server.starttls()
            server.login(MAILJET_USERNAME, MAILJET_PASSWORD)
            server.send_message(msg)

        flash("Votre message a été envoyé avec succès ! Nous vous répondrons rapidement.", "success")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email de contact: {str(e)}")
        flash("Votre message a été enregistré, mais un problème est survenu lors de l'envoi de la notification.", "warning")

    return redirect(url_for("contact"))


@app.route("/inscription_nageur")
def inscription_nageur():
    return render_template("inscription_nageur.html", departements=DEPARTEMENTS)


@app.route("/submit_inscription_nageur", methods=["POST"])
def submit_inscription_nageur():
    try:
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        tel = request.form.get("tel")
        ville = request.form.get("ville")
        dept = request.form.get("dept")
        sexe = request.form.get("sexe")
        diplome = request.form.get("diplome")
        presentation = request.form.get("presentation")
        disponibilites = request.form.get("disponibilites")
        tarif = request.form.get("tarif")
        preferences = request.form.get("preferences")
        login = request.form.get("login")
        password = request.form.get("password")

        # Vérifier si le login existe déjà
        if login:
            existing = query_db("SELECT id FROM nageur WHERE login = ?", (login,), one=True)
            if existing:
                flash("Cet identifiant est déjà utilisé. Veuillez en choisir un autre.", "danger")
                return redirect(url_for("inscription_nageur"))

        password_hash = generate_password_hash(password) if password else None

        photo = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename:
                filename = f"{secrets.token_hex(8)}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                photo = filename

        carte_pro_photo = None
        if "carte_pro_photo" in request.files:
            file = request.files["carte_pro_photo"]
            if file and file.filename:
                filename = f"carte_pro_{secrets.token_hex(8)}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                carte_pro_photo = filename

        nageur_id = execute_db(
            """
            INSERT INTO nageur (nom, prenom, email, tel, ville, dept, sexe, diplome, presentation, disponibilites, tarif, photo, preferences, login, password_hash, carte_pro_photo, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                nom,
                prenom,
                email,
                tel,
                ville,
                dept,
                sexe,
                diplome,
                presentation,
                disponibilites,
                tarif,
                photo,
                preferences,
                login,
                password_hash,
                carte_pro_photo,
                1  # Actif par défaut
            ),
        )

        # Connexion automatique après inscription
        session["nageur_id"] = nageur_id
        session["nageur_nom"] = f"{prenom} {nom}"

        # Envoi des emails de confirmation
        try:
            send_nageur_inscription_email(
                nageur_prenom=prenom,
                nageur_nom=nom,
                nageur_email=email,
                nageur_tel=tel,
                nageur_ville=ville,
                nageur_dept=dept,
                nageur_diplome=diplome,
                nageur_tarif=tarif
            )
        except Exception as e:
            print(f"⚠️ Erreur envoi email inscription: {e}")

        # Redirection vers la page de succès
        return redirect(url_for("remerciements_nageur", nageur_id=nageur_id))

    except Exception as e:
        print(f"❌ Erreur lors de l'inscription nageur: {e}")
        import traceback
        traceback.print_exc()
        flash(f"Une erreur est survenue lors de l'inscription : {str(e)}", "danger")
        return redirect(url_for("inscription_nageur"))


@app.route("/remerciements_nageur/<int:nageur_id>")
def remerciements_nageur(nageur_id):
    """Page de confirmation après inscription réussie"""
    nageur = query_db("SELECT * FROM nageur WHERE id = ?", (nageur_id,), one=True)
    if not nageur:
        return redirect(url_for("index"))
    
    return render_template("confirmation_inscription_nageur.html", nageur=nageur)


# ============================================
# NAGEUR SPACE ROUTES
# ============================================


@app.route("/nageur/login", methods=["GET", "POST"])
def nageur_login():
    if request.method == "POST":
        login_input = request.form.get("login", "").strip().lower()
        password = request.form.get("password", "")

        # Recherche par login ou email (insensible à la casse)
        nageur = query_db("SELECT * FROM nageur WHERE LOWER(login) = ? OR LOWER(email) = ?", (login_input, login_input), one=True)

        if nageur:
            if check_password_hash(nageur["password_hash"], password):
                session["nageur_id"] = nageur["id"]
                session["nageur_nom"] = f"{nageur['prenom']} {nageur['nom']}"
                flash(f"Bienvenue {nageur['prenom']} !", "success")
                return redirect(url_for("mon_profil"))
            else:
                flash("Mot de passe incorrect.", "danger")
        else:
            flash("Identifiant ou email non trouvé.", "danger")

    return render_template("nageur_login.html")


@app.route("/nageur/reset-password", methods=["GET", "POST"])
def nageur_reset_password():
    """Réinitialisation du mot de passe nageur"""
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template("nageur_reset_password.html")

        nageur = query_db("SELECT id, prenom, nom FROM nageur WHERE email = ?", (email,), one=True)

        if nageur:
            password_hash = generate_password_hash(new_password)
            execute_db("UPDATE nageur SET password_hash = ? WHERE id = ?", (password_hash, nageur["id"]))
            
            flash("Votre mot de passe a été modifié avec succès. Connectez-vous maintenant.", "success")
            return redirect(url_for("nageur_login"))
        else:
            flash("Aucun compte trouvé avec cet email.", "danger")

    return render_template("nageur_reset_password.html")


@app.route("/nageur/logout")
def nageur_logout():
    session.pop("nageur_id", None)
    session.pop("nageur_nom", None)
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("index"))


@app.route("/mon_profil", methods=["GET", "POST"])
@nageur_login_required
def mon_profil():
    nageur_id = session["nageur_id"]

    if request.method == "POST":
        # Traitement de la mise à jour
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        tel = request.form.get("tel")
        ville = request.form.get("ville")
        dept = request.form.get("dept")
        sexe = request.form.get("sexe")
        diplome = request.form.get("diplome")
        presentation = request.form.get("presentation")
        disponibilites = request.form.get("disponibilites")
        tarif = request.form.get("tarif")
        preferences = request.form.get("preferences")

        # Gestion de la photo de profil
        photo_sql = ""
        params = [nom, prenom, email, tel, ville, dept, sexe, diplome, presentation, disponibilites, tarif, preferences]

        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename:
                # Supprimer l'ancienne photo si elle existe
                old_photo = query_db("SELECT photo FROM nageur WHERE id = ?", (nageur_id,), one=True)
                if old_photo and old_photo["photo"]:
                    old_path = os.path.join(UPLOAD_FOLDER, old_photo["photo"])
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass

                filename = f"{secrets.token_hex(8)}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                photo_sql = ", photo = ?"
                params.append(filename)

        # Gestion de la carte professionnelle
        carte_sql = ""
        if "carte_pro_photo" in request.files:
            file = request.files["carte_pro_photo"]
            if file and file.filename:
                # Supprimer l'ancienne carte si elle existe
                old_carte = query_db("SELECT carte_pro_photo FROM nageur WHERE id = ?", (nageur_id,), one=True)
                if old_carte and old_carte["carte_pro_photo"]:
                    old_path = os.path.join(UPLOAD_FOLDER, old_carte["carte_pro_photo"])
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass

                filename = f"carte_pro_{secrets.token_hex(8)}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                carte_sql = ", carte_pro_photo = ?"
                params.append(filename)

        params.append(nageur_id)

        execute_db(
            f"""
            UPDATE nageur 
            SET nom = ?, prenom = ?, email = ?, tel = ?, ville = ?, dept = ?, sexe = ?, 
                diplome = ?, presentation = ?, disponibilites = ?, tarif = ?, preferences = ? {photo_sql} {carte_sql}
            WHERE id = ?
        """,
            tuple(params),
        )
        
        # Envoi de l'email de confirmation de modification
        send_nageur_update_email(prenom, nom, email)
        
        flash("Votre profil a été mis à jour avec succès !", "success")
        return redirect(url_for("mon_profil"))

    nageur = query_db("SELECT * FROM nageur WHERE id = ?", (nageur_id,), one=True)
    return render_template("mon_profil.html", nageur=nageur, departements=DEPARTEMENTS)


import re
import unicodedata

def slugify(value):
    """
    Convertit une chaîne en slug (ex: "Mon Article !" -> "mon-article")
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

# ============================================
# BLOG ADMIN ROUTES
# ============================================

@app.route("/admin/blog")
@login_required
def admin_blog():
    """Liste tous les articles côté admin"""
    articles = query_db("SELECT * FROM article ORDER BY date_publication DESC")
    return render_template("admin_blog.html", articles=articles)

@app.route("/admin/blog/new", methods=["GET", "POST"])
@login_required
def admin_blog_new():
    """Créer un nouvel article"""
    if request.method == "POST":
        titre = request.form.get("titre")
        resume = request.form.get("resume")
        contenu = request.form.get("contenu")
        is_published = 1 if request.form.get("is_published") else 0
        
        slug = slugify(titre)
        
        # Vérifier si le slug existe déjà
        existing = query_db("SELECT id FROM article WHERE slug = ?", (slug,), one=True)
        if existing:
            slug = f"{slug}-{secrets.token_hex(4)}"
            
        image = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename:
                filename = f"blog_{secrets.token_hex(8)}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image = filename
        
        execute_db(
            "INSERT INTO article (titre, slug, resume, contenu, image, is_published) VALUES (?, ?, ?, ?, ?, ?)",
            (titre, slug, resume, contenu, image, is_published)
        )
        
        flash("Article créé avec succès !", "success")
        return redirect(url_for("admin_blog"))
        
    return render_template("edit_article.html", article=None)

@app.route("/admin/blog/edit/<int:id>", methods=["GET", "POST"])
@login_required
def admin_blog_edit(id):
    """Modifier un article"""
    article = query_db("SELECT * FROM article WHERE id = ?", (id,), one=True)
    if not article:
        flash("Article introuvable", "danger")
        return redirect(url_for("admin_blog"))
        
    if request.method == "POST":
        titre = request.form.get("titre")
        resume = request.form.get("resume")
        contenu = request.form.get("contenu")
        is_published = 1 if request.form.get("is_published") else 0
        
        # Gestion de l'image
        image = article['image']
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename:
                filename = f"blog_{secrets.token_hex(8)}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image = filename
        
        # On ne change pas le slug pour ne pas casser le SEO des anciens articles
        execute_db(
            "UPDATE article SET titre = ?, resume = ?, contenu = ?, image = ?, is_published = ? WHERE id = ?",
            (titre, resume, contenu, image, is_published, id)
        )
        
        flash("Article mis à jour !", "success")
        return redirect(url_for("admin_blog"))
        
    return render_template("edit_article.html", article=article)

@app.route("/admin/blog/delete/<int:id>", methods=["POST"])
@login_required
def admin_blog_delete(id):
    """Supprimer un article"""
    execute_db("DELETE FROM article WHERE id = ?", (id,))
    flash("Article supprimé !", "success")
    return redirect(url_for("admin_blog"))

# ============================================
# ADMIN AUTHENTICATION ROUTES
# ============================================


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and check_password_hash(
            ADMIN_PASSWORD_HASH, password
        ):
            session["admin_logged_in"] = True
            flash("Connexion réussie !", "success")
            return redirect(url_for("admin_index"))
        else:
            flash("Identifiants incorrects", "danger")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Vous avez été déconnecté", "info")
    return redirect(url_for("index"))


@app.route("/admin")
@login_required
def admin_index():
    clients = query_db("SELECT * FROM client ORDER BY date_inscription DESC")
    nageurs = query_db("SELECT * FROM nageur ORDER BY date_inscription DESC")
    selections = query_db("""
        SELECT s.*, c.nom as client_nom, c.prenom as client_prenom, 
               n.nom as nageur_nom, n.prenom as nageur_prenom
        FROM selection s
        JOIN client c ON s.client_id = c.id
        JOIN nageur n ON s.nageur_id = n.id
        ORDER BY s.date_selection DESC
    """)

    return render_template(
        "admin.html", clients=clients, nageurs=nageurs, selections=selections
    )


# ============================================
# ADMIN CRUD ROUTES
# ============================================

@app.route('/admin/client/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    """Modifier un client"""
    
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        tel = request.form.get('tel')
        ville = request.form.get('ville')
        dept = request.form.get('dept')
        login = request.form.get('login')
        password = request.form.get('password')
        
        # SQL et paramètres de base
        sql = '''
            UPDATE client 
            SET nom = ?, prenom = ?, email = ?, tel = ?, ville = ?, dept = ?, login = ?
        '''
        params = [nom, prenom, email, tel, ville, dept, login]

        # Si un nouveau mot de passe est saisi, on le hache
        if password and password.strip():
            sql += ", password_hash = ?"
            params.append(generate_password_hash(password))
            print(f"🔐 Mot de passe mis à jour pour client {login}")

        sql += " WHERE id = ?"
        params.append(id)

        execute_db(sql, tuple(params))
        
        flash('✅ Client modifié avec succès !', 'success')
        return redirect(url_for('admin_index'))
    
    # GET : afficher le formulaire
    client = query_db('SELECT * FROM client WHERE id = ?', (id,), one=True)
    
    if not client:
        flash('Client introuvable', 'danger')
        return redirect(url_for('admin_index'))
    
    return render_template('edit_client.html', client=client, departements=DEPARTEMENTS)


@app.route('/admin/client/<int:id>/delete', methods=['POST'])
@login_required
def delete_client(id):
    """Supprimer un client"""
    
    # Supprimer d'abord les sélections associées
    execute_db('DELETE FROM selection WHERE client_id = ?', (id,))
    # Puis supprimer le client
    execute_db('DELETE FROM client WHERE id = ?', (id,))
    
    flash('Client supprimé avec succès !', 'success')
    return redirect(url_for('admin_index'))


@app.route('/admin/nageur/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_nageur(id):
    """Modifier un maître-nageur"""
    
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        tel = request.form.get('tel')
        ville = request.form.get('ville')
        dept = request.form.get('dept')
        sexe = request.form.get('sexe')
        diplome = request.form.get('diplome')
        presentation = request.form.get('presentation')
        disponibilites = request.form.get('disponibilites')
        tarif = request.form.get('tarif')
        preferences = request.form.get('preferences')
        login = request.form.get('login')
        password = request.form.get('password')
        is_active = request.form.get('is_active') == '1'
        
        # Récupérer les données actuelles
        nageur = query_db('SELECT photo, carte_pro_photo FROM nageur WHERE id = ?', (id,), one=True)
        current_photo = nageur['photo'] if nageur else None
        current_carte = nageur['carte_pro_photo'] if nageur else None
        
        new_photo = current_photo
        new_carte = current_carte
        
        # Gestion de la suppression de photo
        if request.form.get('delete_photo') == '1':
            if current_photo:
                old_path = os.path.join(UPLOAD_FOLDER, current_photo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            new_photo = None
        
        # Gestion de la suppression de la carte pro
        if request.form.get('delete_carte') == '1':
            if current_carte:
                old_path = os.path.join(UPLOAD_FOLDER, current_carte)
                if os.path.exists(old_path):
                    os.remove(old_path)
            new_carte = None
        
        # Upload photo
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                if current_photo and not request.form.get('delete_photo'):
                    old_path = os.path.join(UPLOAD_FOLDER, current_photo)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = f"{secrets.token_hex(8)}_{file.filename}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                new_photo = filename
        
        # Upload carte pro
        if 'carte_pro_photo' in request.files:
            file = request.files['carte_pro_photo']
            if file and file.filename:
                if current_carte and not request.form.get('delete_carte'):
                    old_path = os.path.join(UPLOAD_FOLDER, current_carte)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = f"carte_pro_{secrets.token_hex(8)}_{file.filename}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                new_carte = filename
        
        # SQL et paramètres de base
        sql = '''
            UPDATE nageur 
            SET nom = ?, prenom = ?, email = ?, tel = ?, ville = ?, dept = ?, sexe = ?,
                diplome = ?, presentation = ?, disponibilites = ?, tarif = ?, photo = ?, preferences = ?,
                login = ?, carte_pro_photo = ?, is_active = ?
        '''
        params = [nom, prenom, email, tel, ville, dept, sexe, diplome, presentation, disponibilites, tarif, new_photo, preferences, login, new_carte, 1 if is_active else 0]

        # Si un nouveau mot de passe est saisi, on le hache
        if password and password.strip():
            sql += ", password_hash = ?"
            params.append(generate_password_hash(password))

        sql += " WHERE id = ?"
        params.append(id)

        execute_db(sql, tuple(params))
        
        flash('✅ Maître-nageur modifié avec succès !', 'success')
        return redirect(url_for('admin_index'))
    
    # GET : afficher le formulaire
    nageur = query_db('SELECT * FROM nageur WHERE id = ?', (id,), one=True)
    
    if not nageur:
        flash('Maître-nageur introuvable', 'danger')
        return redirect(url_for('admin_index'))
    
    return render_template('edit_nageur.html', nageur=nageur, departements=DEPARTEMENTS)


@app.route('/admin/nageur/<int:id>/delete', methods=['POST'])
@login_required
def delete_nageur(id):
    """Supprimer un maître-nageur"""
    
    # Supprimer d'abord les sélections associées
    execute_db('DELETE FROM selection WHERE nageur_id = ?', (id,))
    # Puis supprimer le nageur
    execute_db('DELETE FROM nageur WHERE id = ?', (id,))
    
    flash('Maître-nageur supprimé avec succès !', 'success')
    return redirect(url_for('admin_index'))



# ============================================
# BLOG ROUTES
# ============================================

@app.route("/blog")
def blog_index():
    """Liste tous les articles du blog"""
    articles = query_db("SELECT * FROM article WHERE is_published = 1 ORDER BY date_publication DESC")
    return render_template("blog.html", articles=articles)

@app.route("/blog/<slug>")
def blog_article(slug):
    """Affiche un article complet"""
    article = query_db("SELECT * FROM article WHERE slug = ?", (slug,), one=True)
    if not article:
        flash("Article non trouvé.", "danger")
        return redirect(url_for("blog_index"))
    
    # Récupérer quelques articles récents pour la barre latérale
    recent_articles = query_db("SELECT * FROM article WHERE slug != ? AND is_published = 1 ORDER BY date_publication DESC LIMIT 3", (slug,))
    
    return render_template("article.html", article=article, recent_articles=recent_articles)

# ============================================
# INITIALISATION
# ============================================

# Initialiser la base de données au démarrage (nécessaire pour Passenger sur o2switch)
with app.app_context():
    init_db()

if __name__ == "__main__":
    print("🌊 AquaCoach est prêt!")
    print("🌐 Ouvrez votre navigateur à: http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=True)
