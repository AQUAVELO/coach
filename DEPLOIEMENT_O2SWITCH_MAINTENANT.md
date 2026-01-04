# 🚀 DÉPLOIEMENT SUR O2SWITCH - À FAIRE MAINTENANT

## ⏱️ Temps estimé : 10-15 minutes

---

## 📋 ÉTAPE 1 : Connexion SSH à o2switch

Ouvrez un terminal et connectez-vous à votre serveur o2switch :

```bash
ssh votre-utilisateur@votredomaine.com
```

**Remplacez :**
- `votre-utilisateur` par votre nom d'utilisateur o2switch
- `votredomaine.com` par votre domaine

**Exemple :**
```bash
ssh aquavelo@aquavelo.fr
```

---

## 📥 ÉTAPE 2 : Aller dans le dossier du site

```bash
cd www/natation
# ou si le chemin est différent :
cd public_html/natation
```

---

## 🔄 ÉTAPE 3 : Pull des dernières modifications depuis GitHub

```bash
git pull origin main
```

**✅ Vous devriez voir :**
```
From https://github.com/AQUAVELO/coach
 * branch            main       -> FETCH_HEAD
Updating xxxxx..76f34d1
Fast-forward
 .htaccess                        | 70 +++++++++++++++++++
 FIX_ADMIN_O2SWITCH.md           | 250 ++++++++++++++++++++++
 PRODUCTION_O2SWITCH.md          | 300 +++++++++++++++++++++++
 ACTIONS_A_FAIRE_SUR_O2SWITCH.md | 240 ++++++++++++++++++++
 app.py                          | 150 +++++++++++++
 templates/admin.html            | 200 +++++++++++-----
 templates/edit_client.html      | 80 +++++++
 templates/edit_nageur.html      | 100 +++++++++
 passenger_wsgi.py               | 15 ++++
 deploy.sh                       | 100 +++++++++
 13 files changed, 1422 insertions(+), 100 deletions(-)
```

**⚠️ Si vous voyez "Already up to date"** : C'est normal, ça veut dire que tout est déjà à jour.

---

## ⚙️ ÉTAPE 4 : Modifier le fichier .htaccess

### 4.1 Ouvrir le fichier

```bash
nano .htaccess
```

### 4.2 Trouver votre nom d'utilisateur o2switch

Si vous ne le connaissez pas :
```bash
whoami
```

### 4.3 Modifications à faire dans .htaccess

**Cherchez les lignes suivantes et modifiez-les :**

#### a) Remplacer `VOTRE_USER`

**AVANT :**
```apache
PassengerAppRoot /home/VOTRE_USER/www/natation
PassengerAppLogFile /home/VOTRE_USER/logs/passenger_aquacoach.log
```

**APRÈS (exemple si votre user est "aquavelo"):**
```apache
PassengerAppRoot /home/aquavelo/www/natation
PassengerAppLogFile /home/aquavelo/logs/passenger_aquacoach.log
```

#### b) Remplacer `SECRET_KEY`

**AVANT :**
```apache
SetEnv SECRET_KEY "CHANGEZ_MOI_PAR_UNE_CLE_SECRETE_TRES_LONGUE_ET_ALEATOIRE"
```

**APRÈS (utilisez cette clé ou générez-en une) :**
```apache
SetEnv SECRET_KEY "e8f3c9b2a5d6f1e4c8b7a3d9f2e6c5b8a1d4f7e9c3b6a2d5f8e1c4b7a9d3f6e2c5b8a4d7f1e6c9b3a5d2f8e4c7b1a9d6f3e2c8b5a1d4f7e9c6b3a2d5f8e1c4b7a9"
```

### 4.4 Sauvegarder et quitter

- Appuyez sur `Ctrl + X`
- Tapez `Y` (pour Yes)
- Appuyez sur `Enter`

---

## 🗄️ ÉTAPE 5 : Vérifier la base de données

### 5.1 Sauvegarder l'ancienne base (sécurité)

```bash
cp instance/aquacoach.db instance/aquacoach.db.backup.$(date +%Y%m%d_%H%M)
```

### 5.2 Vérifier les colonnes actuelles

```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('instance/aquacoach.db')
cursor = conn.execute('PRAGMA table_info(nageur)')
columns = [row[1] for row in cursor.fetchall()]
print('📊 Colonnes actuelles de la table nageur:')
for col in columns:
    print(f'   ✓ {col}')

missing = []
if 'disponibilites' not in columns:
    missing.append('disponibilites')
if 'presentation' not in columns:
    missing.append('presentation')
if 'diplome' not in columns:
    missing.append('diplome')

if missing:
    print(f'\n⚠️  Colonnes manquantes: {", ".join(missing)}')
    print('   → Migration nécessaire (étape suivante)')
else:
    print('\n✅ Toutes les colonnes sont présentes !')
conn.close()
EOF
```

---

## 🔧 ÉTAPE 6 : Appliquer la migration de base de données

```bash
python3 -c "from app import init_db; init_db()"
```

**✅ Vous devriez voir :**
```
✅ Colonne 'disponibilites' ajoutée à la table nageur
✅ Colonne 'presentation' ajoutée à la table nageur
✅ Colonne 'diplome' ajoutée à la table nageur
```

**Si vous voyez "AttributeError" ou "ModuleNotFoundError"**, installez les dépendances :
```bash
pip3 install --user -r requirements.txt
python3 -c "from app import init_db; init_db()"
```

---

## 🔐 ÉTAPE 7 : Configurer les permissions (CRUCIAL !)

```bash
# Permissions sur le dossier instance
chmod 755 instance/

# Permissions sur la base de données
chmod 664 instance/aquacoach.db

# Vérifier que c'est bien appliqué
ls -la instance/
```

**✅ Résultat attendu :**
```
drwxr-xr-x  2 aquavelo aquavelo  4096 Jan  4 18:00 .
drwxr-xr-x 15 aquavelo aquavelo  4096 Jan  4 18:00 ..
-rw-rw-r--  1 aquavelo aquavelo 12288 Jan  4 18:00 aquacoach.db
```

**Les lignes importantes :**
- `drwxr-xr-x` pour le dossier instance (755)
- `-rw-rw-r--` pour aquacoach.db (664)

---

## 🔄 ÉTAPE 8 : Redémarrer Passenger (le serveur web)

```bash
mkdir -p tmp
touch tmp/restart.txt
```

**✅ Pas de message = succès !**

Attendez **30 secondes** pour que Passenger redémarre complètement.

---

## 🧪 ÉTAPE 9 : TESTER EN LIGNE !

### Test 1 : Page d'accueil
Ouvrez votre navigateur et allez sur :
```
http://votredomaine.com
```

**✅ Doit afficher** : La page d'accueil AquaCoach avec le fond piscine

---

### Test 2 : Page admin
```
http://votredomaine.com/admin/login
```

**Connectez-vous :**
- Nom d'utilisateur : `admin`
- Mot de passe : `admin123`

**✅ Doit afficher** : Le tableau de bord administrateur

---

### Test 3 : Modification d'un client (LE TEST IMPORTANT !)

1. Dans le tableau de bord admin, **cliquez sur le bouton bleu "✏️ Modifier"** d'un client
2. **Changez le prénom** (par exemple de "Claude" à "Jean")
3. Cliquez sur **"💾 Enregistrer les modifications"**
4. **Vérifiez** que vous revenez sur le tableau admin
5. **VÉRIFIEZ** que le prénom a bien changé dans le tableau

**✅ Si le prénom a changé = SUCCÈS !** 🎉

---

### Test 4 : Modification d'un maître-nageur

1. Scrollez jusqu'à la section "🏊‍♂️ Liste des Maîtres-Nageurs"
2. Cliquez sur **"✏️ Modifier"** pour un maître-nageur
3. **Changez le tarif** (par exemple de 35 à 40)
4. Cliquez sur **"💾 Enregistrer les modifications"**
5. **Vérifiez** que le nouveau tarif apparaît dans le tableau

**✅ Si le tarif a changé = SUCCÈS !** 🎉

---

## 🔍 ÉTAPE 10 : Vérifier les logs (si problème)

```bash
# Voir les 50 dernières lignes des logs
tail -n 50 ~/logs/error_log

# Ou voir les logs en temps réel
tail -f ~/logs/error_log
# (Ctrl+C pour arrêter)
```

---

## ❌ EN CAS DE PROBLÈME

### Problème 1 : "Internal Server Error" sur la page d'accueil

**Solution :**
```bash
# Vérifier les logs
tail -n 100 ~/logs/error_log

# Vérifier que passenger_wsgi.py existe
ls -la passenger_wsgi.py

# Redémarrer
touch tmp/restart.txt
```

---

### Problème 2 : "sqlite3.OperationalError: no such column: disponibilites"

**Solution :**
```bash
python3 -c "from app import init_db; init_db()"
touch tmp/restart.txt
```

---

### Problème 3 : "attempt to write a readonly database"

**Solution :**
```bash
chmod 755 instance/
chmod 664 instance/aquacoach.db
touch tmp/restart.txt
```

---

### Problème 4 : Les modifications ne sont pas sauvegardées

**Vérifier que .db n'est pas dans Git :**
```bash
git ls-files | grep "\.db$"
```

**Si des fichiers apparaissent**, faites :
```bash
git rm --cached instance/*.db
git commit -m "🗑️ Retrait base de données"
git push origin main
```

---

## 🎯 CHECKLIST FINALE

Cochez chaque étape :

- [ ] Connexion SSH réussie
- [ ] `cd www/natation` effectué
- [ ] `git pull origin main` effectué
- [ ] `.htaccess` modifié (VOTRE_USER et SECRET_KEY)
- [ ] Base de données sauvegardée
- [ ] Migration appliquée : `python3 -c "from app import init_db; init_db()"`
- [ ] Permissions : `chmod 755 instance/ && chmod 664 instance/aquacoach.db`
- [ ] Passenger redémarré : `touch tmp/restart.txt`
- [ ] **TEST 1** : Page d'accueil fonctionne ✅
- [ ] **TEST 2** : Page admin accessible ✅
- [ ] **TEST 3** : Modification client fonctionne ✅
- [ ] **TEST 4** : Modification nageur fonctionne ✅

---

## 🎉 FÉLICITATIONS !

Si tous les tests passent, votre site est **100% opérationnel** avec :

✨ **Nouvelles fonctionnalités :**
- ✏️ Modification complète des clients
- ✏️ Modification complète des maîtres-nageurs
- 🗑️ Suppression avec confirmation
- 📊 Interface admin améliorée

🔒 **Sécurité renforcée :**
- 🚫 Base de données hors de Git
- 🔐 Configuration Passenger sécurisée
- 🛡️ Permissions correctes

---

## 🚀 DÉPLOIEMENTS FUTURS

Pour les prochaines mises à jour, utilisez simplement le script automatique :

```bash
cd ~/www/natation
./deploy.sh
```

Ce script fait tout automatiquement :
- Pull depuis GitHub
- Installation des dépendances
- Migration de la base
- Configuration des permissions
- Redémarrage de Passenger

---

## 📞 BESOIN D'AIDE ?

Si vous rencontrez un problème :

1. **Logs d'erreur** : Envoyez-moi `tail -n 100 ~/logs/error_log`
2. **Permissions** : Envoyez-moi `ls -la instance/`
3. **Git** : Envoyez-moi `git ls-files | grep "\.db$"`

**Support o2switch :**
- 📧 Email : support@o2switch.fr
- 🎫 Ticket : Via l'espace client
- 💬 Forum : https://forum.o2switch.fr/

---

**🌊 Bon déploiement ! N'hésitez pas si vous avez des questions ! 🚀**

