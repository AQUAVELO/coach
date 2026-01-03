# 🌊 AquaCoach - Plateforme de Mise en Relation avec des Maîtres-Nageurs

**AquaCoach** est une application Flask qui connecte des clients avec des maîtres-nageurs certifiés partout en France.

## ✨ Fonctionnalités

### 👥 Pour les Clients
- ✅ Inscription rapide avec sélection du département
- 🔍 Recherche de maîtres-nageurs disponibles dans votre région
- 👁️ Consultation des profils détaillés (diplômes, tarifs, disponibilités)
- 💳 Paiement sécurisé des frais de dossier (2€)
- 📧 Réception d'un email de confirmation avec coordonnées du coach
- 🎟️ Code de validation unique

### 🏊 Pour les Maîtres-Nageurs
- ✅ Inscription avec profil complet
- 📸 Upload de photo de profil
- 💰 Définition de vos tarifs personnalisés
- 📅 Indication de vos disponibilités
- 📊 Visibilité auprès des clients de votre département

### 🔐 Panel Administrateur
- 📊 Dashboard avec statistiques complètes
- 👥 Gestion des clients et maîtres-nageurs
- 🤝 Suivi des réservations
- 📧 Notifications email automatiques

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation rapide

```bash
# Cloner le repository
git clone https://github.com/AQUAVELO/coach.git
cd coach

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
# Sur macOS/Linux:
source venv/bin/activate
# Sur Windows:
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

L'application sera accessible sur **http://localhost:8080**

### Scripts de lancement

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

## 📧 Configuration Email (Mailjet)

L'application utilise Mailjet pour l'envoi d'emails. Configurez vos clés dans `app.py` :

```python
MAILJET_USERNAME = 'votre_api_key'
MAILJET_PASSWORD = 'votre_api_secret'
MAILJET_FROM_EMAIL = 'votre@email.com'
ADMIN_EMAIL = 'admin@email.com'
```

## 🗄️ Base de Données

L'application utilise **SQLite** (aucune configuration nécessaire). La base de données est créée automatiquement au premier lancement.

### Tables :
- `client` - Informations des clients
- `nageur` - Informations des maîtres-nageurs  
- `selection` - Réservations effectuées

## 🎯 Utilisation

### 1. Page d'Accueil
Visitez http://localhost:8080 et choisissez votre profil :
- **Client** : Trouver un maître-nageur
- **Maître-Nageur** : S'inscrire pour proposer vos services

### 2. Parcours Client
1. Inscription avec vos coordonnées
2. Sélection de votre département
3. Choix d'un maître-nageur disponible
4. Paiement des frais de dossier (2€ - mode démo)
5. Réception d'un email avec les coordonnées du coach

### 3. Parcours Maître-Nageur
1. Inscription avec profil complet
2. Upload d'une photo
3. Définition des tarifs et disponibilités
4. Validation et mise en ligne du profil

### 4. Administration
- URL : http://localhost:8080/admin/login
- Username : `admin`
- Password : `admin123`

⚠️ **Pensez à changer ces identifiants en production !**

## 📁 Structure du Projet

```
coach/
├── app.py                      # Application Flask principale
├── requirements.txt            # Dépendances Python
├── .gitignore                  # Fichiers à ignorer
├── start.sh / start.bat        # Scripts de lancement
│
├── instance/                   # Base de données (auto-créée)
│   └── aquacoach.db
│
├── templates/                  # Templates HTML
│   ├── index.html
│   ├── inscription_client.html
│   ├── inscription_nageur.html
│   ├── choix_nageur.html
│   ├── confirmation_paiement.html
│   ├── success.html
│   ├── admin.html
│   └── admin_login.html
│
└── static/                     # Fichiers statiques
    ├── css/
    │   └── style.css
    ├── images/
    └── uploads/               # Photos uploadées
```

## 🔧 Configuration

### Changer le Port
Dans `app.py` (dernière ligne) :
```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Changez 8080
```

### Mode Production
Pour déployer en production :
1. Changez `secret_key` dans `app.py`
2. Désactivez `debug=True`
3. Utilisez un serveur WSGI (Gunicorn, uWSGI)
4. Configurez HTTPS
5. Utilisez PostgreSQL/MySQL au lieu de SQLite
6. Implémentez un vrai système de paiement

## 🛡️ Sécurité

**Important pour la production :**
- ⚠️ Changez la clé secrète Flask
- ⚠️ Modifiez les identifiants admin
- ⚠️ Activez HTTPS
- ⚠️ Configurez un vrai système de paiement
- ⚠️ Ajoutez une protection CSRF
- ⚠️ Validez et sanitisez toutes les entrées utilisateur

## 📝 Mode Démo

La version actuelle inclut :
- ✅ Paiement **simulé** (pas de vraie transaction)
- ✅ Emails **fonctionnels** (via Mailjet configuré)
- ✅ Base de données SQLite locale
- ✅ Authentification admin basique

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier si le port est utilisé
lsof -i :8080
# Tuer le processus si nécessaire
kill -9 <PID>
```

### Erreur de base de données
```bash
# Supprimer et recréer la base
rm instance/aquacoach.db
python app.py
```

### Problème d'upload de photos
```bash
# Créer le dossier et donner les permissions
mkdir -p static/uploads
chmod 755 static/uploads
```

## 📖 Documentation Complète

- `QUICKSTART.md` - Guide de démarrage rapide
- `STRIPE_CONFIG.md` - Configuration Stripe (si besoin)
- `REPARATION_TERMINEE.md` - Notes de réparation du code

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## 📄 Licence

Ce projet est fourni tel quel pour usage personnel et éducatif.

## 🙏 Support

Pour toute question :
- Consultez les logs dans le terminal
- Vérifiez la documentation dans le dossier du projet
- Créez une issue sur GitHub

---

**🌊 Développé avec Flask et ❤️ pour connecter les passionnés de natation !**

---

## 📊 Statistiques du Projet

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
