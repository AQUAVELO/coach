# 🚀 Configuration Production o2switch

## ⚠️ Problème : Les modifications admin ne fonctionnent pas en ligne

### Causes possibles :

1. **Permissions d'écriture sur SQLite** ❌
2. **Base de données dans Git** ❌
3. **Configuration du serveur web** ❌

---

## ✅ Solutions

### 1. **Permissions sur la base de données SQLite**

SQLite a besoin de **permissions d'écriture** sur :
- Le fichier `aquacoach.db`
- Le **répertoire** `instance/` (pour créer les fichiers temporaires `.db-wal` et `.db-shm`)

#### Sur o2switch (via SSH ou File Manager) :

```bash
# Se connecter en SSH à votre serveur o2switch
ssh votre-user@votre-domaine.com

# Aller dans le répertoire du site
cd ~/www/natation  # ou le chemin de votre installation

# Donner les permissions nécessaires
chmod 755 instance/
chmod 664 instance/aquacoach.db

# IMPORTANT : Le propriétaire doit être l'utilisateur du serveur web
# Sur o2switch, c'est généralement votre nom d'utilisateur
chown -R votre-user:votre-user instance/
```

#### Via cPanel File Manager (si pas d'accès SSH) :

1. Aller dans **File Manager** (Gestionnaire de fichiers)
2. Naviguer vers `public_html/natation/instance/`
3. Clic droit sur le dossier `instance/` → **Change Permissions**
4. Mettre **755** (rwxr-xr-x)
5. Clic droit sur `aquacoach.db` → **Change Permissions**
6. Mettre **664** (rw-rw-r--)

---

### 2. **Ne PAS mettre la base de données dans Git**

La base de données **NE DOIT JAMAIS** être synchronisée via GitHub car :
- Elle sera écrasée à chaque `git pull`
- Les données de production seront perdues
- Risque de conflits

#### ✅ Vérifier que `aquacoach.db` est dans `.gitignore` :

```bash
# Vérifier
cat .gitignore | grep "*.db"

# Si pas présent, l'ajouter
echo "*.db" >> .gitignore
echo "instance/*.db" >> .gitignore
```

#### ✅ Retirer la base de données de Git si elle y est :

```bash
git rm --cached instance/aquacoach.db
git commit -m "🗑️ Retrait de la base de données du suivi Git"
git push origin main
```

---

### 3. **Configuration pour o2switch (avec .htaccess)**

Créer ou modifier le fichier `.htaccess` à la racine de votre application :

```apache
# .htaccess pour Flask sur o2switch
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ app.py/$1 [QSA,L]

# Autoriser les requêtes POST
<Limit POST>
    Order allow,deny
    Allow from all
</Limit>

# Protection de la base de données
<Files "*.db">
    Order allow,deny
    Deny from all
</Files>

# Protection des fichiers sensibles
<FilesMatch "^\.">
    Order allow,deny
    Deny from all
</FilesMatch>
```

---

### 4. **Utiliser un serveur WSGI (recommandé pour production)**

Flask en mode `app.run()` n'est pas fait pour la production. Sur o2switch, il faut utiliser **Passenger** (mod_passenger).

#### Créer un fichier `passenger_wsgi.py` :

```python
import sys
import os

# Ajouter le chemin de l'application
sys.path.insert(0, os.path.dirname(__file__))

# Importer l'application Flask
from app import app as application

# o2switch utilise Passenger qui cherche 'application'
# (pas 'app')
```

#### Créer un fichier `.htaccess` pour Passenger :

```apache
PassengerEnabled On
PassengerAppRoot /home/votre-user/www/natation
PassengerPython /usr/bin/python3
PassengerAppLogFile /home/votre-user/logs/passenger.log

# Réécriture d'URL
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,L]
```

---

### 5. **Vérifier les logs d'erreur**

Sur o2switch, les logs sont généralement dans :

```bash
~/logs/error_log
~/logs/passenger.log  # Si vous utilisez Passenger
```

Pour voir les erreurs en temps réel :

```bash
tail -f ~/logs/error_log
```

---

### 6. **Script de déploiement automatique**

Créer un script `deploy.sh` pour faciliter les mises à jour :

```bash
#!/bin/bash
# deploy.sh - Script de déploiement pour o2switch

echo "🚀 Déploiement d'AquaCoach..."

# Pull les dernières modifications
git pull origin main

# Installer/mettre à jour les dépendances
pip3 install --user -r requirements.txt

# Appliquer les migrations (si nécessaire)
python3 -c "from app import init_db; init_db()"

# Vérifier les permissions
chmod 755 instance/
chmod 664 instance/aquacoach.db 2>/dev/null || echo "Base de données non trouvée (normal si première installation)"

# Redémarrer Passenger (si utilisé)
mkdir -p tmp
touch tmp/restart.txt

echo "✅ Déploiement terminé!"
```

Rendre le script exécutable :

```bash
chmod +x deploy.sh
```

---

### 7. **Checklist de déploiement**

- [ ] `.gitignore` contient `*.db` et `instance/*.db`
- [ ] La base de données n'est PAS dans Git
- [ ] Permissions `755` sur le dossier `instance/`
- [ ] Permissions `664` sur `aquacoach.db`
- [ ] Fichier `passenger_wsgi.py` créé
- [ ] Fichier `.htaccess` configuré
- [ ] Dépendances installées : `pip3 install --user -r requirements.txt`
- [ ] Variables d'environnement configurées (si nécessaire)
- [ ] Tests des routes POST en production

---

### 8. **Diagnostic rapide**

Si les modifications ne fonctionnent toujours pas, essayez :

```bash
# Vérifier les permissions
ls -la instance/

# Devrait afficher quelque chose comme :
# drwxr-xr-x  2 user user 4096 Jan  3 17:00 instance/
# -rw-rw-r--  1 user user 8192 Jan  3 17:00 aquacoach.db

# Tester l'écriture dans la base
python3 -c "
import sqlite3
conn = sqlite3.connect('instance/aquacoach.db')
try:
    conn.execute('SELECT 1')
    print('✅ Lecture OK')
    conn.execute('PRAGMA table_info(nageur)')
    print('✅ Écriture OK')
except Exception as e:
    print(f'❌ Erreur: {e}')
conn.close()
"
```

---

### 9. **Alternative : Utiliser PostgreSQL ou MySQL**

Si SQLite continue à poser problème en production, o2switch propose MySQL/MariaDB gratuitement.

#### Modifier `app.py` pour utiliser MySQL :

```python
# Remplacer
DATABASE = os.path.join(app.instance_path, "aquacoach.db")

# Par
import pymysql
DATABASE_URL = "mysql+pymysql://user:password@localhost/aquacoach_db"
```

---

## 📞 Support o2switch

Si le problème persiste :
- **Email** : support@o2switch.fr
- **Ticket** : Via l'espace client o2switch
- **Forum** : https://forum.o2switch.fr/

---

## 🔧 Configuration recommandée pour production

```python
# Dans app.py, ajouter en haut :
import os

# Mode production
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'changez-moi-en-production')
else:
    app.config['DEBUG'] = True
```

Sur o2switch, définir la variable d'environnement via `.htaccess` :

```apache
SetEnv FLASK_ENV production
SetEnv SECRET_KEY votre_clé_secrète_très_longue_et_aléatoire
```

---

**✅ Une fois ces étapes appliquées, les modifications admin devraient fonctionner en production !**

