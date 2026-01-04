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
import os
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
DATABASE = os.path.join(app.instance_path, "aquacoach.db")
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Identifiants admin (à changer en production !)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")  # Mot de passe: admin123

# Configuration Mailjet (CLÉS QUI FONCTIONNAIENT HIER)
MAILJET_HOST = "in-v3.mailjet.com"
MAILJET_PORT = 587
MAILJET_USERNAME = "adf33e0c77039ed69396e3a8a07400cb"
MAILJET_PASSWORD = "05906e966c8e2933b1dc8b0f8bb1e18b"
MAILJET_FROM_EMAIL = "jacquesverdier4@gmail.com"
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
    montant="2,00 €",
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


# ============================================
# DATABASE FUNCTIONS
# ============================================


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS nageur (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS client (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT NOT NULL,
            tel TEXT NOT NULL,
            ville TEXT NOT NULL,
            dept TEXT NOT NULL,
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS selection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            nageur_id INTEGER NOT NULL,
            date_selection DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES client (id),
            FOREIGN KEY (nageur_id) REFERENCES nageur (id)
        )
    """)

    # Migration: Ajouter les colonnes manquantes à la table nageur si elles n'existent pas
    try:
        cursor = db.execute("PRAGMA table_info(nageur)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'disponibilites' not in columns:
            db.execute("ALTER TABLE nageur ADD COLUMN disponibilites TEXT")
            print("✅ Colonne 'disponibilites' ajoutée à la table nageur")
        
        if 'presentation' not in columns:
            db.execute("ALTER TABLE nageur ADD COLUMN presentation TEXT")
            print("✅ Colonne 'presentation' ajoutée à la table nageur")
        
        if 'diplome' not in columns:
            db.execute("ALTER TABLE nageur ADD COLUMN diplome TEXT")
            print("✅ Colonne 'diplome' ajoutée à la table nageur")
        
        if 'photo' not in columns:
            db.execute("ALTER TABLE nageur ADD COLUMN photo TEXT")
            print("✅ Colonne 'photo' ajoutée à la table nageur")
            
    except Exception as e:
        print(f"⚠️ Erreur lors de la migration: {e}")

    db.commit()
    db.close()


# ============================================
# ROUTES
# ============================================


@app.route("/")
def index():
    db = get_db()
    # Récupérer les derniers nageurs et clients pour la page d'accueil
    nageurs = db.execute(
        "SELECT * FROM nageur ORDER BY date_inscription DESC LIMIT 6"
    ).fetchall()
    clients = db.execute(
        "SELECT * FROM client ORDER BY date_inscription DESC LIMIT 3"
    ).fetchall()
    db.close()
    return render_template("index.html", nageurs=nageurs, clients=clients)


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

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO client (nom, prenom, email, tel, ville, dept)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (nom, prenom, email, tel, ville, dept),
    )
    client_id = cursor.lastrowid
    db.commit()
    db.close()

    session["client_id"] = client_id
    session["client_dept"] = dept

    return redirect(url_for("choix_nageur"))


@app.route("/choix_nageur", methods=["GET", "POST"])
def choix_nageur():
    if request.method == "POST":
        nageur_id = request.form.get("nageur_id")
        session["nageur_id"] = nageur_id
        return redirect(url_for("confirmation_paiement"))

    if "client_dept" not in session:
        return redirect(url_for("inscription_client"))

    db = get_db()
    nageurs = db.execute(
        "SELECT * FROM nageur WHERE dept = ?", (session["client_dept"],)
    ).fetchall()
    db.close()

    return render_template("choix_nageur.html", nageurs=nageurs)


@app.route("/confirmation_paiement")
def confirmation_paiement():
    """Page de confirmation de paiement (MODE DÉMO)"""
    if "nageur_id" not in session or "client_id" not in session:
        flash("Session expirée", "danger")
        return redirect(url_for("index"))

    db = get_db()
    nageur = db.execute(
        "SELECT * FROM nageur WHERE id = ?", (session["nageur_id"],)
    ).fetchone()
    client = db.execute(
        "SELECT * FROM client WHERE id = ?", (session["client_id"],)
    ).fetchone()
    db.close()

    if not nageur or not client:
        flash("Erreur lors de la récupération des informations", "danger")
        return redirect(url_for("index"))

    return render_template(
        "confirmation_paiement.html",
        nageur_prenom=nageur["prenom"],
        nageur_nom=nageur["nom"],
        client_email=client["email"],
    )


@app.route("/paiement", methods=["POST"])
def paiement():
    """Traiter le paiement simulé (MODE DÉMO)"""
    if "nageur_id" not in session or "client_id" not in session:
        flash("Session expirée", "danger")
        return redirect(url_for("index"))

    db = get_db()
    nageur = db.execute(
        "SELECT * FROM nageur WHERE id = ?", (session["nageur_id"],)
    ).fetchone()
    client = db.execute(
        "SELECT * FROM client WHERE id = ?", (session["client_id"],)
    ).fetchone()

    # Enregistrer la sélection
    db.execute(
        """
        INSERT INTO selection (client_id, nageur_id, date_selection)
        VALUES (?, ?, ?)
    """,
        (session["client_id"], session["nageur_id"], datetime.now()),
    )
    db.commit()
    db.close()

    # Envoi des emails
    code_validation = send_confirmation_email(
        client_email=client["email"],
        client_prenom=client["prenom"],
        client_nom=client["nom"],
        nageur_prenom=nageur["prenom"],
        nageur_nom=nageur["nom"],
        nageur_email=nageur["email"],
        nageur_tel=nageur["tel"],
        nageur_ville=nageur["ville"],
        montant="2,00 €",
    )

    if code_validation:
        flash("Un email de confirmation vous a été envoyé !", "success")
    else:
        flash(
            "Réservation enregistrée mais erreur lors de l'envoi de l'email.", "warning"
        )

    # Nettoyer la session
    session.pop("nageur_id", None)
    session.pop("client_id", None)

    return render_template(
        "success.html",
        client_prenom=client["prenom"],
        client_nom=client["nom"],
        nageur_prenom=nageur["prenom"],
        nageur_nom=nageur["nom"],
        code_validation=code_validation,
    )


@app.route("/inscription_nageur")
def inscription_nageur():
    return render_template("inscription_nageur.html", departements=DEPARTEMENTS)


@app.route("/submit_inscription_nageur", methods=["POST"])
def submit_inscription_nageur():
    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    email = request.form.get("email")
    tel = request.form.get("tel")
    ville = request.form.get("ville")
    dept = request.form.get("dept")
    diplome = request.form.get("diplome")
    presentation = request.form.get("presentation")
    disponibilites = request.form.get("disponibilites")
    tarif = request.form.get("tarif")

    photo = None
    if "photo" in request.files:
        file = request.files["photo"]
        if file and file.filename:
            filename = f"{secrets.token_hex(8)}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            photo = filename

    db = get_db()
    db.execute(
        """
        INSERT INTO nageur (nom, prenom, email, tel, ville, dept, diplome, presentation, disponibilites, tarif, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            nom,
            prenom,
            email,
            tel,
            ville,
            dept,
            diplome,
            presentation,
            disponibilites,
            tarif,
            photo,
        ),
    )
    db.commit()
    db.close()

    flash("Inscription réussie ! Vous serez contacté prochainement.", "success")
    return redirect(url_for("inscription_nageur"))


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
    db = get_db()
    clients = db.execute(
        "SELECT * FROM client ORDER BY date_inscription DESC"
    ).fetchall()
    nageurs = db.execute(
        "SELECT * FROM nageur ORDER BY date_inscription DESC"
    ).fetchall()
    selections = db.execute("""
        SELECT s.*, c.nom as client_nom, c.prenom as client_prenom, 
               n.nom as nageur_nom, n.prenom as nageur_prenom
        FROM selection s
        JOIN client c ON s.client_id = c.id
        JOIN nageur n ON s.nageur_id = n.id
        ORDER BY s.date_selection DESC
    """).fetchall()
    db.close()

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
    db = get_db()
    
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        tel = request.form.get('tel')
        ville = request.form.get('ville')
        dept = request.form.get('dept')
        
        db.execute('''
            UPDATE client 
            SET nom = ?, prenom = ?, email = ?, tel = ?, ville = ?, dept = ?
            WHERE id = ?
        ''', (nom, prenom, email, tel, ville, dept, id))
        db.commit()
        db.close()
        
        flash('Client modifié avec succès !', 'success')
        return redirect(url_for('admin_index'))
    
    # GET : afficher le formulaire
    client = db.execute('SELECT * FROM client WHERE id = ?', (id,)).fetchone()
    db.close()
    
    if not client:
        flash('Client introuvable', 'danger')
        return redirect(url_for('admin_index'))
    
    return render_template('edit_client.html', client=client, departements=DEPARTEMENTS)


@app.route('/admin/client/<int:id>/delete', methods=['POST'])
@login_required
def delete_client(id):
    """Supprimer un client"""
    db = get_db()
    
    # Supprimer d'abord les sélections associées
    db.execute('DELETE FROM selection WHERE client_id = ?', (id,))
    # Puis supprimer le client
    db.execute('DELETE FROM client WHERE id = ?', (id,))
    db.commit()
    db.close()
    
    flash('Client supprimé avec succès !', 'success')
    return redirect(url_for('admin_index'))


@app.route('/admin/nageur/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_nageur(id):
    """Modifier un maître-nageur"""
    db = get_db()
    
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        tel = request.form.get('tel')
        ville = request.form.get('ville')
        dept = request.form.get('dept')
        diplome = request.form.get('diplome')
        presentation = request.form.get('presentation')
        disponibilites = request.form.get('disponibilites')
        tarif = request.form.get('tarif')
        
        db.execute('''
            UPDATE nageur 
            SET nom = ?, prenom = ?, email = ?, tel = ?, ville = ?, dept = ?,
                diplome = ?, presentation = ?, disponibilites = ?, tarif = ?
            WHERE id = ?
        ''', (nom, prenom, email, tel, ville, dept, diplome, presentation, disponibilites, tarif, id))
        db.commit()
        db.close()
        
        flash('Maître-nageur modifié avec succès !', 'success')
        return redirect(url_for('admin_index'))
    
    # GET : afficher le formulaire
    nageur = db.execute('SELECT * FROM nageur WHERE id = ?', (id,)).fetchone()
    db.close()
    
    if not nageur:
        flash('Maître-nageur introuvable', 'danger')
        return redirect(url_for('admin_index'))
    
    return render_template('edit_nageur.html', nageur=nageur, departements=DEPARTEMENTS)


@app.route('/admin/nageur/<int:id>/delete', methods=['POST'])
@login_required
def delete_nageur(id):
    """Supprimer un maître-nageur"""
    db = get_db()
    
    # Supprimer d'abord les sélections associées
    db.execute('DELETE FROM selection WHERE nageur_id = ?', (id,))
    # Puis supprimer le nageur
    db.execute('DELETE FROM nageur WHERE id = ?', (id,))
    db.commit()
    db.close()
    
    flash('Maître-nageur supprimé avec succès !', 'success')
    return redirect(url_for('admin_index'))


# ============================================
# INITIALISATION
# ============================================

if __name__ == "__main__":
    init_db()
    print("🌊 AquaCoach est prêt!")
    print("🌐 Ouvrez votre navigateur à: http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=True)
