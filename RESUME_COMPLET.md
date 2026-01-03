# 🎉 AQUACOACH - Résumé des Fonctionnalités

## ✅ Fonctionnalités Implémentées

### 1. 🏠 Site Web Moderne
- Design inspiré d'AquaVelo
- Interface responsive (mobile, tablette, desktop)
- Palette de couleurs turquoise professionnelle
- Navigation intuitive

### 2. 👤 Gestion des Utilisateurs

#### Clients :
- Inscription avec formulaire complet
- Sélection du département
- Choix du maître-nageur
- Système de réservation

#### Maîtres-nageurs :
- Inscription avec photo de profil
- Profil complet (diplôme, expérience, tarifs, disponibilités)
- Affichage par département

### 3. 🔐 Administration Sécurisée
- **Connexion** : `/admin/login`
- **Identifiants par défaut** :
  - Username: `admin`
  - Password: `admin123`
- Dashboard complet :
  - Liste des nageurs inscrits
  - Liste des clients
  - Historique des réservations
  - Statistiques
- Protection par mot de passe hashé (werkzeug.security)
- Session sécurisée

### 4. 💳 Système de Paiement

#### Mode Démo (ACTUEL) :
- ✅ **Paiement simulé** sans Stripe
- Interface de paiement stylisée
- Frais de dossier : 2,00 €
- Aucune configuration requise
- Parfait pour les tests

#### Mode Production (Prêt) :
- Code Stripe Checkout préparé
- Instructions détaillées dans `STRIPE_CONFIG.md`
- Basculement facile (décommenter quelques lignes)

### 5. 📧 Système d'Emailing Mailjet

#### Automatique après paiement :
✅ **Email au client** :
- Message de confirmation personnalisé
- **Coordonnées complètes du maître-nageur** :
  - Nom, prénom
  - Ville
  - Email (cliquable)
  - Téléphone (cliquable)
- Code de validation unique (8 caractères)
- Bon de réservation HTML stylisé

✅ **Email à l'admin** :
- Notification de chaque nouvelle réservation
- Détails complets (client + nageur)
- Code de validation pour référence

#### Configuration :
- Serveur SMTP : `in-v3.mailjet.com`
- Port : `587` (STARTTLS)
- Emails réellement envoyés ✅
- Design responsive

### 6. 🗄️ Base de Données SQLite

#### Tables :
1. **client** : Informations clients
2. **nageur** : Profils maîtres-nageurs
3. **selection** : Historique des réservations

#### Fonctionnalités :
- Création automatique au démarrage
- Recherche par département
- Historique des transactions

## 🚀 Comment Utiliser

### Démarrage du serveur :
```bash
cd /Applications/MAMP/htdocs/natation
python3 app.py
```

### Accès :
- **Site public** : http://localhost:8080
- **Admin** : http://localhost:8080/admin/login

### Tests complets :
1. Inscription client avec votre vraie adresse email
2. Choix d'un nageur (département 06 recommandé)
3. Paiement simulé
4. **Vérification de votre boîte mail** 📧

## 📁 Structure du Projet

```
natation/
├── app.py                      # Application Flask principale
├── instance/
│   └── aquacoach.db           # Base de données SQLite
├── static/
│   ├── css/
│   │   └── style.css          # Styles globaux
│   ├── images/                # Images du site
│   └── uploads/               # Photos des nageurs
├── templates/
│   ├── index.html             # Page d'accueil
│   ├── inscription_client.html
│   ├── inscription_nageur.html
│   ├── choix_nageur.html
│   ├── confirmation_paiement.html  # Mode DÉMO
│   ├── success.html           # Page de succès
│   ├── admin.html             # Dashboard admin
│   └── admin_login.html
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation
├── QUICKSTART.md             # Guide de démarrage
├── STRIPE_CONFIG.md          # Config Stripe (production)
├── EMAIL_CONFIG.md           # Config Mailjet ✅
└── PROBLEME_PAIEMENT.md      # Troubleshooting
```

## 🔧 Configuration Actuelle

### Emails (Mailjet) :
- ✅ **ACTIF et FONCTIONNEL**
- Envoi automatique après chaque paiement
- Client : `jacquesverdier4@gmail.com`
- Admin : `aqua.cannes@gmail.com`

### Paiement :
- ✅ **MODE DÉMO** (simulation)
- Stripe désactivé temporairement
- Montant : 2,00 €

### Admin :
- ✅ **SÉCURISÉ**
- Login/mot de passe requis
- Session protégée

## 📊 Statistiques

- **Lignes de code** : ~550 (Python + HTML)
- **Templates** : 8 pages
- **Routes** : 12 endpoints
- **Base de données** : 3 tables
- **Emails** : 2 types (client + admin)

## 🎯 Prochaines Étapes

### Pour passer en production :

1. **Activer Stripe** (optionnel) :
   - Obtenir les clés API Stripe
   - Décommenter les lignes dans `app.py`
   - Tester avec les cartes de test Stripe

2. **Déploiement** :
   - Choisir un hébergeur (Heroku, PythonAnywhere, etc.)
   - Configurer les variables d'environnement
   - Activer HTTPS

3. **Personnalisation** :
   - Changer les identifiants admin
   - Modifier les emails expéditeur/destinataire
   - Ajuster les tarifs

## 🐛 Dépannage

### Le serveur ne démarre pas :
```bash
# Tuer le processus sur le port 8080
lsof -ti:8080 | xargs kill -9
# Redémarrer
python3 app.py
```

### Les emails ne partent pas :
- Vérifier la connexion internet
- Vérifier les identifiants Mailjet dans `app.py`
- Consulter les logs du serveur

### Erreur de base de données :
```bash
# Supprimer et recréer la DB
rm instance/aquacoach.db
# Redémarrer le serveur (recrée automatiquement)
python3 app.py
```

## 💡 Conseils

- **Test** : Utilisez votre vraie adresse email pour tester l'envoi
- **Sécurité** : Changez le mot de passe admin en production
- **Backup** : Sauvegardez régulièrement `aquacoach.db`
- **Logs** : Consultez le terminal pour les erreurs

## 📞 Support

Pour toute question :
- 📧 Email : jacquesverdier4@gmail.com
- 📝 Documentation : Voir fichiers `.md` dans le projet

---

**🌊 AquaCoach - Votre plateforme de réservation de cours de natation ! 🏊‍♂️**

*Développé avec Flask, SQLite, Mailjet et amour* ❤️

