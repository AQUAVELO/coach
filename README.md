# 🌊 AquaCoach - Application Flask

**AquaCoach** est une plateforme qui connecte des clients avec des maîtres-nageurs certifiés dans toute la France.

## 📋 Fonctionnalités

### Pour les Clients
- ✅ Inscription rapide avec département
- 🔍 Recherche de maîtres-nageurs dans votre département
- 👁️ Visualisation des profils détaillés (diplômes, tarifs, disponibilités)
- 💳 Paiement sécurisé (simulé en local)
- 📞 Accès aux coordonnées complètes du nageur

### Pour les Maîtres-Nageurs
- ✅ Inscription avec profil complet
- 📸 Upload de photo de profil
- 💰 Définition de vos tarifs
- 📅 Gestion de vos disponibilités
- 📧 Notification par email lors de sélection

### Administration
- 📊 Dashboard complet avec statistiques
- 👥 Gestion des clients inscrits
- 🏊 Gestion des maîtres-nageurs
- 🤝 Suivi des connexions réalisées

## 🚀 Installation Rapide

### Prérequis
- Python 3.8 ou supérieur

### Installation

```bash
cd aquaconnect

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

L'application sera accessible à : **http://localhost:8080**

### Scripts de lancement automatique

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

## 📁 Structure du Projet

```
aquaconnect/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── start.sh / start.bat  # Scripts de lancement
│
├── instance/             # Base de données SQLite (créée automatiquement)
│   └── aquaconnect.db
│
├── templates/            # Templates HTML
│   ├── index.html
│   ├── inscription_client.html
│   ├── inscription_nageur.html
│   ├── choix_nageur.html
│   ├── confirmation_paiement.html
│   ├── success.html
│   ├── remerciements_nageur.html
│   └── admin.html
│
└── static/               # Fichiers statiques
    ├── images/          # Photos de profil
    ├── css/            # Feuilles de style
    └── uploads/        # Photos uploadées
```

## 💾 Base de Données

L'application utilise **SQLite** pour la base de données locale (pas besoin de configuration MySQL).

### Tables principales:
- **client** - Informations des clients
- **nageur** - Informations des maîtres-nageurs
- **selection** - Connexions client-nageur

La base de données est créée automatiquement au premier lancement avec des données de démonstration.

## 🎯 Utilisation

### 1. Page d'Accueil
- Visitez http://localhost:8080
- Découvrez les maîtres-nageurs disponibles
- Choisissez votre rôle (Client ou Maître-Nageur)

### 2. Inscription Client
- Remplissez le formulaire d'inscription
- Sélectionnez votre département
- Choisissez un maître-nageur dans votre région
- Effectuez le paiement (simulé)
- Recevez les coordonnées complètes

### 3. Inscription Maître-Nageur
- Remplissez votre profil complet
- Ajoutez une photo
- Définissez vos tarifs et disponibilités
- Votre profil sera visible par les clients de votre département

### 4. Administration
- Accédez à http://localhost:8080/admin
- Consultez les statistiques
- Gérez les utilisateurs
- Suivez les connexions réalisées

## 🔧 Configuration

### Personnalisation du Port
Par défaut, l'application tourne sur le port 8080. Pour changer :

```python
# Dans app.py, ligne finale:
app.run(debug=True, host='0.0.0.0', port=VOTRE_PORT)
```

### Données de Démonstration
Au premier lancement, l'application crée automatiquement:
- 5 maîtres-nageurs du département 06
- 5 clients du département 06

Pour désactiver les données de démo, commentez la section correspondante dans `app.py` (fonction `init_db()`).

## 🎨 Personnalisation

### Ajouter des Départements
Les départements sont définis dans `app.py`:
```python
DEPARTEMENTS = ["01", "02", ..., "95", "971", "972", ...]
```

### Modifier le Montant du Paiement
Dans `templates/confirmation_paiement.html`, modifiez la valeur affichée.

### Changer les Couleurs
Toutes les couleurs sont définies en CSS inline dans les templates. Cherchez les codes couleur comme `#42a5f5` pour les modifier.

## 🐛 Dépannage

### L'application ne démarre pas
```bash
# Vérifiez que le port 8080 n'est pas utilisé
lsof -i :8080

# Si occupé, tuez le processus ou changez le port dans app.py
```

### Erreur de base de données
```bash
# Supprimez la base et relancez
rm instance/aquaconnect.db
python app.py
```

### Problèmes d'upload de photos
```bash
# Vérifiez que le dossier existe
mkdir -p static/uploads
chmod 755 static/uploads
```

## 📝 Données de Test

### Nageurs de Démonstration (Département 06)
1. **Léa Martin** - BEESAN - 35€/séance
2. **Lucas Dubois** - BPJEPS - 30€/séance
3. **Chloé Bernard** - BEESAN - 40€/séance
4. **Hugo Petit** - BPJEPS - 45€/séance
5. **Manon Roux** - BEESAN - 38€/séance

### Clients de Démonstration
- Sophie Dupont, Pierre Moreau, Marie Laurent, etc.

## 🔒 Sécurité

**Important pour la production:**
- Changez la `secret_key` dans `app.py`
- Configurez HTTPS
- Ajoutez une vraie intégration PayPal
- Implémentez l'authentification admin
- Utilisez une vraie base de données (PostgreSQL/MySQL)

## 🚧 Limitations de la Version Locale

Cette version est conçue pour un usage local/démo:
- ✅ Paiement PayPal **simulé**
- ✅ Envoi d'emails **désactivé**
- ✅ Base de données **SQLite** (pour facilité d'installation)
- ✅ Pas d'authentification admin

Pour une version production, il faudrait:
- Intégrer réellement PayPal
- Configurer un service d'emails (Mailjet, SendGrid)
- Migrer vers PostgreSQL/MySQL
- Ajouter authentification et gestion des rôles
- Implémenter CSRF protection

## 📧 Support

Pour toute question ou problème, consultez les logs de l'application dans le terminal.

## 📄 Licence

Ce projet est fourni tel quel pour usage personnel et éducatif.

## 🙏 Remerciements

Application développée avec Flask et ❤️ pour connecter les passionnés de natation.

---

**🌊 Bonne baignade avec AquaConnect !**
