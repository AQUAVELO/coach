# 🎯 ACTIONS À FAIRE SUR O2SWITCH - LISTE COMPLÈTE

## ⚡ Problème résolu !

**Le problème des modifications admin qui ne fonctionnent pas** a deux causes principales :

1. ❌ **Les fichiers .db étaient dans Git** → Ils sont écrasés à chaque `git pull`
2. ❌ **Permissions insuffisantes sur SQLite** → Le serveur web ne peut pas écrire

---

## 📋 ÉTAPES À SUIVRE SUR O2SWITCH (10 minutes)

### 1️⃣ Connexion SSH à o2switch

```bash
ssh votre-user@votredomaine.com
cd www/natation  # ou le chemin de votre site
```

### 2️⃣ Pull des dernières modifications depuis GitHub

```bash
git pull origin main
```

**✅ Vous devriez voir :**
- ✨ Ajout CRUD admin complet + Configuration production o2switch
- 🗑️ Suppression des fichiers .db du suivi Git

### 3️⃣ Modifier le fichier .htaccess

```bash
nano .htaccess
```

**Remplacez :**
- `VOTRE_USER` par votre nom d'utilisateur o2switch (exemple : `aquavelo`)
- `CHANGEZ_MOI_PAR_UNE_CLE_SECRETE_TRES_LONGUE_ET_ALEATOIRE` par une vraie clé secrète

**Exemple de clé secrète :**
```
e8f3c9b2a5d6f1e4c8b7a3d9f2e6c5b8a1d4f7e9c3b6a2d5f8e1c4b7a9d3f6e2
```

**Enregistrer et quitter :**
- `Ctrl + X`
- `Y` (pour Yes)
- `Enter`

### 4️⃣ Sauvegarder l'ancienne base de données (au cas où)

```bash
cp instance/aquacoach.db instance/aquacoach.db.backup.$(date +%Y%m%d)
```

### 5️⃣ Vérifier la structure de la base actuelle

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('instance/aquacoach.db')
cursor = conn.execute('PRAGMA table_info(nageur)')
columns = [row[1] for row in cursor.fetchall()]
print('Colonnes actuelles:', columns)
if 'disponibilites' in columns:
    print('✅ Colonne disponibilites présente')
else:
    print('❌ Colonne disponibilites manquante - migration nécessaire')
conn.close()
"
```

### 6️⃣ Appliquer la migration (ajouter les colonnes manquantes)

```bash
python3 -c "from app import init_db; init_db()"
```

**✅ Vous devriez voir :**
- ✅ Colonne 'disponibilites' ajoutée (si elle manquait)
- ✅ Colonne 'presentation' ajoutée (si elle manquait)
- ✅ Colonne 'diplome' ajoutée (si elle manquait)

### 7️⃣ Configurer les permissions (CRUCIAL !)

```bash
# Permissions sur le dossier
chmod 755 instance/

# Permissions sur la base de données
chmod 664 instance/aquacoach.db

# Vérifier les permissions
ls -la instance/
```

**✅ Résultat attendu :**
```
drwxr-xr-x  2 user user 4096 Jan  3 instance/
-rw-rw-r--  1 user user 8192 Jan  3 aquacoach.db
```

### 8️⃣ Redémarrer Passenger

```bash
mkdir -p tmp
touch tmp/restart.txt
```

### 9️⃣ Tester en ligne ! 🧪

1. Allez sur : `http://votredomaine.com/admin/login`
2. Connectez-vous : `admin` / `admin123`
3. Essayez de **modifier un client** (cliquez sur le bouton bleu "✏️ Modifier")
4. Changez le prénom, cliquez sur "💾 Enregistrer"
5. **Vérifiez que la modification est bien enregistrée** ✅

### 🔟 Vérifier les logs (si problème)

```bash
tail -n 50 ~/logs/error_log
```

---

## 🚀 DÉPLOIEMENT AUTOMATIQUE FUTUR

Pour les prochaines mises à jour, utilisez simplement :

```bash
cd ~/www/natation
./deploy.sh
```

Le script :
- ✅ Pull les modifications depuis GitHub
- ✅ Installe les dépendances
- ✅ Applique les migrations
- ✅ Configure les permissions automatiquement
- ✅ Redémarre Passenger

---

## ✅ CHECKLIST FINALE

Cochez chaque étape accomplie :

- [ ] Connexion SSH réussie
- [ ] `git pull origin main` exécuté
- [ ] Fichier `.htaccess` modifié (VOTRE_USER et SECRET_KEY)
- [ ] Base de données sauvegardée
- [ ] Migration appliquée (`init_db()`)
- [ ] Permissions configurées (`chmod 755` et `chmod 664`)
- [ ] Passenger redémarré (`touch tmp/restart.txt`)
- [ ] Test de modification d'un client ✅
- [ ] Test de modification d'un maître-nageur ✅
- [ ] Aucune erreur dans les logs

---

## 🆘 EN CAS DE PROBLÈME

### Problème : "sqlite3.OperationalError: no such column: disponibilites"

**Solution :** La migration n'a pas été appliquée

```bash
python3 -c "from app import init_db; init_db()"
touch tmp/restart.txt
```

### Problème : "sqlite3.OperationalError: attempt to write a readonly database"

**Solution :** Permissions insuffisantes

```bash
chmod 755 instance/
chmod 664 instance/aquacoach.db
touch tmp/restart.txt
```

### Problème : "Les modifications ne sont pas enregistrées"

**Solution :** La base .db est peut-être encore dans Git localement

Sur votre serveur o2switch :
```bash
git ls-files | grep "\.db$"
# Si des fichiers apparaissent, faites :
git rm --cached instance/*.db
git commit -m "🗑️ Retrait base de données du suivi Git"
```

### Problème : "500 Internal Server Error"

**Solution :** Vérifier les logs

```bash
tail -n 100 ~/logs/error_log
```

---

## 📞 CONTACT SUPPORT

- **Email** : support@o2switch.fr
- **Ticket** : Via l'espace client o2switch
- **Forum** : https://forum.o2switch.fr/

---

## 🎯 RÉSUMÉ DES CHANGEMENTS

### ✨ Nouvelles fonctionnalités
- ✏️ Modification complète des clients (nom, prénom, email, tél, ville, département)
- ✏️ Modification complète des maîtres-nageurs (+ diplôme, présentation, disponibilités, tarif)
- 🗑️ Suppression avec confirmation JavaScript
- 📊 Tableau admin amélioré avec tous les champs visibles

### 🔧 Corrections techniques
- 🗄️ Migration automatique des colonnes manquantes en base de données
- 🚫 Retrait des fichiers .db du suivi Git (cause #1 des problèmes)
- 🔐 Configuration de sécurité pour o2switch

### 📚 Documentation
- 📖 Guide complet de production o2switch
- 🚨 Guide de dépannage rapide (5 min)
- 🤖 Script de déploiement automatique

---

**🌊 Une fois ces étapes accomplies, tout devrait fonctionner parfaitement ! 🎉**

Si vous avez suivi toutes les étapes et que ça ne fonctionne toujours pas, contactez-moi avec :
1. Le résultat de `ls -la instance/`
2. Les dernières lignes de `~/logs/error_log`
3. Le résultat de `git ls-files | grep "\.db$"`

