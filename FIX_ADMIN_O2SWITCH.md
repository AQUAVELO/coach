# 🚨 FIX URGENT : Modifications Admin ne fonctionnent pas sur o2switch

## 🎯 Solution rapide (5 minutes)

### Étape 1 : Connexion SSH à o2switch

```bash
ssh votre-user@votredomaine.com
cd www/natation  # ou le chemin de votre site
```

### Étape 2 : Vérifier les permissions actuelles

```bash
ls -la instance/
```

**Résultat attendu :**
```
drwxr-xr-x  2 user user 4096 Jan  3 17:00 .
drwxr-xr-x 10 user user 4096 Jan  3 17:00 ..
-rw-rw-r--  1 user user 8192 Jan  3 17:00 aquacoach.db
```

### Étape 3 : Corriger les permissions ⚡

```bash
# IMPORTANT : Ceci est la cause #1 des problèmes avec SQLite
chmod 755 instance/
chmod 664 instance/aquacoach.db
```

### Étape 4 : Redémarrer l'application

```bash
mkdir -p tmp
touch tmp/restart.txt
```

### Étape 5 : Tester 🧪

Allez sur : `http://votredomaine.com/admin/login`
- Connectez-vous
- Essayez de modifier un client ou un maître-nageur
- Ça devrait fonctionner ! ✅

---

## 🔍 Si ça ne fonctionne toujours pas

### Vérification #1 : La base de données est-elle dans Git ?

```bash
git ls-files | grep "\.db$"
```

**Si des fichiers .db apparaissent**, c'est le problème ! Faites :

```bash
# Retirer la base de Git
git rm --cached instance/aquacoach.db
git commit -m "🗑️ Retrait de la base de données du suivi Git"
git push origin main

# Vérifier que .gitignore contient bien :
echo "*.db" >> .gitignore
echo "instance/*.db" >> .gitignore
```

### Vérification #2 : Logs d'erreur

```bash
# Voir les erreurs récentes
tail -n 50 ~/logs/error_log

# Voir les erreurs en temps réel
tail -f ~/logs/error_log
```

### Vérification #3 : Test d'écriture dans la base

```bash
python3 << EOF
import sqlite3
import os

db_path = 'instance/aquacoach.db'
print(f"📍 Chemin : {os.path.abspath(db_path)}")
print(f"📂 Existe : {os.path.exists(db_path)}")

if os.path.exists(db_path):
    print(f"🔐 Permissions : {oct(os.stat(db_path).st_mode)[-3:]}")
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('SELECT COUNT(*) FROM nageur')
        print("✅ Lecture : OK")
        conn.execute('UPDATE nageur SET nom = nom WHERE 1=0')
        conn.commit()
        print("✅ Écriture : OK")
        conn.close()
    except Exception as e:
        print(f"❌ Erreur : {e}")
else:
    print("❌ Base de données introuvable !")
EOF
```

### Vérification #4 : Configuration du .htaccess

```bash
cat .htaccess | grep -E "(PassengerEnabled|VOTRE_USER)"
```

**Vérifiez que :**
- `PassengerEnabled On` est présent
- `VOTRE_USER` a été remplacé par votre vrai nom d'utilisateur o2switch

---

## 🛠️ Solution alternative : Recréer la base de données

**⚠️ ATTENTION : Ceci supprimera toutes les données !**

```bash
# Sauvegarder l'ancienne base
cp instance/aquacoach.db instance/aquacoach.db.backup

# Supprimer l'ancienne base
rm instance/aquacoach.db

# Recréer avec les bonnes permissions
python3 -c "from app import init_db; init_db()"

# Vérifier les permissions
ls -la instance/aquacoach.db
# Devrait afficher : -rw-rw-r-- 1 user user ...

# Redémarrer
touch tmp/restart.txt
```

---

## 📋 Checklist de diagnostic

Cochez ce qui est OK :

- [ ] Permissions `755` sur le dossier `instance/`
- [ ] Permissions `664` sur le fichier `aquacoach.db`
- [ ] Le fichier `.db` n'est PAS dans Git
- [ ] Le fichier `.htaccess` existe et est configuré
- [ ] Le fichier `passenger_wsgi.py` existe
- [ ] Les requêtes POST sont autorisées dans `.htaccess`
- [ ] Pas d'erreur dans `~/logs/error_log`
- [ ] Le serveur a été redémarré (`touch tmp/restart.txt`)

---

## 💡 Comprendre le problème

**Pourquoi ça fonctionne en local mais pas en production ?**

1. **En local** : Vous êtes l'utilisateur qui a créé la base de données, donc vous avez tous les droits
2. **En production** : Le serveur web (Apache/Passenger) s'exécute avec un utilisateur différent qui peut ne pas avoir les permissions d'écriture

**SQLite a besoin de :**
- Permissions d'écriture sur le **fichier** `.db` (pour modifier les données)
- Permissions d'écriture sur le **dossier** (pour créer les fichiers temporaires `.db-wal` et `.db-shm`)

C'est pourquoi on donne :
- `664` (rw-rw-r--) au fichier → Le groupe peut écrire
- `755` (rwxr-xr-x) au dossier → Tout le monde peut lire et exécuter

---

## 🆘 Support

Si le problème persiste après avoir tout essayé :

1. **Logs complets** : Envoyez le contenu de `~/logs/error_log`
2. **Permissions** : Résultat de `ls -la instance/`
3. **Configuration** : Contenu du `.htaccess`
4. **Support o2switch** : support@o2switch.fr (ils sont très réactifs)

---

## ✅ Déploiement automatique futur

Pour éviter ces problèmes à l'avenir, utilisez le script de déploiement :

```bash
./deploy.sh
```

Ce script vérifie et corrige automatiquement les permissions à chaque déploiement !

