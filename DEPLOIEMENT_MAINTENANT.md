# 🚀 DÉPLOIEMENT SUR O2SWITCH - GUIDE COMPLET

**Date :** 4 Janvier 2026  
**Version :** AquaCoach v2.5  
**Statut :** ✅ Prêt pour déploiement

---

## 📋 RÉSUMÉ DES MODIFICATIONS À DÉPLOYER

### ✨ Nouvelles fonctionnalités :
1. ✅ **Page de confirmation inscription nageur** - Design moderne et rassurant
2. ✅ **Correction affichage photos** - Chemin corrigé + image par défaut SVG
3. ✅ **Modification photos depuis admin** - Upload, suppression, prévisualisation
4. ✅ **Emails inscription nageur** - Confirmation nageur + notification admin
5. ✅ **Emails confirmation paiement** - Client + Admin avec détails complets

### 🎨 Améliorations visuelles :
- Image par défaut SVG professionnelle pour nageurs sans photo
- Prévisualisation temps réel des photos dans l'admin
- Design cohérent et moderne partout
- Affichage département, diplôme et tarif sur page d'accueil

### 🔧 Corrections techniques :
- Chemin photos : `static/images/` → `static/uploads/`
- Gestion automatique suppression anciennes photos
- Migration base de données automatique (colonnes manquantes)
- Validation uploads (taille, format)

---

## 🎯 ÉTAPES DE DÉPLOIEMENT SUR O2SWITCH

### 📍 ÉTAPE 1 : Connexion SSH

```bash
# Connectez-vous à votre serveur o2switch via SSH
ssh votre_user@votre_domaine.com

# Ou utilisez le terminal dans cPanel
```

---

### 📍 ÉTAPE 2 : Aller dans le répertoire du site

```bash
cd ~/www/natation
# ou le chemin où vous avez installé AquaCoach
```

---

### 📍 ÉTAPE 3 : Pull des dernières modifications

```bash
# Récupérer toutes les nouvelles modifications depuis GitHub
git pull origin main
```

**Résultat attendu :**
```
remote: Enumerating objects: XX, done.
remote: Counting objects: 100% (XX/XX), done.
Updating abc1234..730015a
Fast-forward
 app.py                                    | 116 ++++++++++++++++++++++++
 templates/edit_nageur.html                | 89 ++++++++++++++++++
 templates/index.html                      | 12 +--
 templates/choix_nageur.html               | 14 +--
 templates/confirmation_inscription_nageur.html | 245 +++++++++++++++++++++++
 static/images/default-swimmer.svg         | 38 +++++++
 6 files changed, 498 insertions(+), 16 deletions(-)
```

---

### 📍 ÉTAPE 4 : Vérifier les dépendances Python

```bash
# Vérifier que tous les packages sont installés
/usr/bin/python3.10 -m pip install -r requirements.txt --user
```

**Packages nécessaires :**
- Flask
- mailjet_rest (ou smtplib pour Mailjet)
- werkzeug
- secrets
- smtplib (inclus par défaut)

---

### 📍 ÉTAPE 5 : Vérifier la structure des dossiers

```bash
# Créer le dossier images s'il n'existe pas
mkdir -p static/images
mkdir -p static/uploads

# Vérifier les permissions
chmod 755 static/images
chmod 755 static/uploads
chmod 755 instance
chmod 664 instance/aquacoach.db
```

---

### 📍 ÉTAPE 6 : Appliquer les migrations de base de données

```bash
# Lancer Python pour exécuter les migrations
/usr/bin/python3.10 -c "from app import init_db; init_db()"
```

**Ce que fait cette commande :**
- ✅ Ajoute les colonnes manquantes (`diplome`, `presentation`, `disponibilites`, `tarif`, `photo`)
- ✅ Crée les tables si elles n'existent pas
- ✅ Ne touche pas aux données existantes

**Résultat attendu :**
```
✅ Colonne 'diplome' ajoutée à la table nageur (ou déjà existante)
✅ Colonne 'presentation' ajoutée à la table nageur (ou déjà existante)
✅ Colonne 'disponibilites' ajoutée à la table nageur (ou déjà existante)
✅ Colonne 'tarif' ajoutée à la table nageur (ou déjà existante)
✅ Colonne 'photo' ajoutée à la table nageur (ou déjà existante)
```

---

### 📍 ÉTAPE 7 : Vérifier la configuration Mailjet

Assurez-vous que les variables suivantes sont correctes dans `app.py` :

```python
MAILJET_HOST = "in-v3.mailjet.com"
MAILJET_PORT = 587
MAILJET_USERNAME = "VOTRE_API_KEY"  # API Key publique
MAILJET_PASSWORD = "VOTRE_SECRET_KEY"  # API Key secrète
MAILJET_FROM_EMAIL = "contact@aquacoach.fr"  # Email validé
MAILJET_FROM_NAME = "AquaCoach"
ADMIN_EMAIL = "aqua.cannes@gmail.com"
```

**⚠️ IMPORTANT :** Ces clés doivent être vos VRAIES clés Mailjet !

---

### 📍 ÉTAPE 8 : Redémarrer l'application Passenger

```bash
# Créer/toucher le fichier restart.txt pour redémarrer Passenger
mkdir -p tmp
touch tmp/restart.txt
```

**Passenger redémarre automatiquement l'application !**

---

### 📍 ÉTAPE 9 : Vérifier les logs d'erreur (si problème)

```bash
# Voir les logs Apache
tail -f ~/logs/error_log

# Ou dans cPanel : Metrics > Errors
```

---

### 📍 ÉTAPE 10 : Tester le site en ligne

**🌐 Ouvrez votre navigateur et testez :**

1. **Page d'accueil**
   - ✅ Les photos des nageurs s'affichent correctement
   - ✅ L'image par défaut apparaît pour les nageurs sans photo
   - ✅ Le département, diplôme et tarif sont affichés

2. **Inscription nageur**
   - Allez sur `/inscription_nageur`
   - Remplissez le formulaire avec une photo
   - ✅ Vérifiez que la belle page de confirmation s'affiche
   - ✅ Vérifiez que vous recevez l'email de bienvenue
   - ✅ Vérifiez que l'admin reçoit la notification

3. **Admin - Connexion**
   - Allez sur `/admin/login`
   - Connectez-vous avec : `admin` / `AquaCoach2025!`
   - ✅ Accès au tableau de bord

4. **Admin - Modification nageur**
   - Cliquez sur "Modifier" pour un nageur
   - ✅ Vérifiez que la photo actuelle s'affiche
   - ✅ Uploadez une nouvelle photo et vérifiez la prévisualisation
   - ✅ Testez la suppression de photo
   - ✅ Enregistrez et vérifiez que la photo est mise à jour

5. **Inscription client et paiement**
   - Inscrivez un client
   - Choisissez un nageur
   - Effectuez le paiement (mode démo)
   - ✅ Vérifiez que les 2 emails sont envoyés (client + admin)

---

## 🔍 CHECKLIST DE VÉRIFICATION POST-DÉPLOIEMENT

### ✅ Fichiers et dossiers :
- [ ] `static/images/default-swimmer.svg` existe
- [ ] `static/uploads/` existe et est accessible en écriture
- [ ] `instance/aquacoach.db` existe et est accessible en écriture
- [ ] `templates/confirmation_inscription_nageur.html` existe
- [ ] `templates/edit_nageur.html` contient la section photo

### ✅ Fonctionnalités :
- [ ] Photos nageurs s'affichent sur page d'accueil
- [ ] Image par défaut s'affiche pour nageurs sans photo
- [ ] Upload photo fonctionne depuis admin
- [ ] Suppression photo fonctionne depuis admin
- [ ] Page confirmation inscription nageur s'affiche
- [ ] Emails inscription nageur sont envoyés (nageur + admin)
- [ ] Emails confirmation paiement sont envoyés (client + admin)

### ✅ Base de données :
- [ ] Colonnes `diplome`, `presentation`, `disponibilites`, `tarif`, `photo` existent
- [ ] Les anciennes données sont préservées
- [ ] Les nouvelles inscriptions fonctionnent

---

## ❌ PROBLÈMES COURANTS ET SOLUTIONS

### Problème 1 : Photos ne s'affichent pas
**Solution :**
```bash
# Vérifier les permissions
chmod -R 755 static/uploads
chmod -R 755 static/images

# Vérifier que les fichiers existent
ls -la static/uploads/
ls -la static/images/
```

### Problème 2 : Erreur "column does not exist"
**Solution :**
```bash
# Relancer les migrations
/usr/bin/python3.10 -c "from app import init_db; init_db()"
```

### Problème 3 : Emails ne partent pas
**Solution :**
1. Vérifiez les clés API Mailjet dans `app.py`
2. Vérifiez que l'email expéditeur est validé dans Mailjet
3. Regardez les logs : `tail -f ~/logs/error_log`
4. Testez avec un simple script Python Mailjet

### Problème 4 : Upload de photo ne fonctionne pas
**Solution :**
```bash
# Vérifier les permissions d'écriture
chmod 755 static/uploads
chown votre_user:votre_user static/uploads

# Vérifier la taille max upload dans .htaccess
# Ajouter si nécessaire :
php_value upload_max_filesize 10M
php_value post_max_size 10M
```

### Problème 5 : Page 500 Internal Server Error
**Solution :**
```bash
# Voir les logs d'erreur
tail -50 ~/logs/error_log

# Vérifier les permissions
chmod 755 instance
chmod 664 instance/aquacoach.db

# Redémarrer Passenger
touch tmp/restart.txt
```

---

## 🔐 SÉCURITÉ POST-DÉPLOIEMENT

### 1. Changez le mot de passe admin
Dans `app.py`, ligne ~770 :
```python
# CHANGEZ CE MOT DE PASSE EN PRODUCTION !
ADMIN_PASSWORD_HASH = generate_password_hash("NOUVEAU_MOT_DE_PASSE_FORT")
```

### 2. Configurez HTTPS (SSL)
Dans cPanel > SSL/TLS > Manage SSL sites
Activez le certificat SSL gratuit Let's Encrypt

### 3. Sauvegardez régulièrement la base de données
```bash
# Créer une sauvegarde
cp instance/aquacoach.db instance/aquacoach_backup_$(date +%Y%m%d).db

# Télécharger via SFTP pour plus de sécurité
```

---

## 📊 STATISTIQUES DU DÉPLOIEMENT

**Commits depuis le dernier déploiement :**
- `394ee65` - 📧 Ajout système d'email pour inscription maître-nageur
- `bfc8cff` - 📸 Correction affichage photos + Ajout image par défaut
- `730015a` - 📸 Ajout modification photos nageurs depuis admin

**Fichiers modifiés :** 6  
**Lignes ajoutées :** 498  
**Nouvelles fonctionnalités :** 5

---

## 🎉 DÉPLOIEMENT TERMINÉ !

Si toutes les étapes se sont bien déroulées, votre site AquaCoach est maintenant à jour en production avec :

✅ Système de modification photos complet  
✅ Emails d'inscription nageur automatiques  
✅ Belle page de confirmation inscription  
✅ Image par défaut pour nageurs sans photo  
✅ Affichage optimisé des photos partout  

**🌐 Votre site est prêt à accueillir vos utilisateurs !**

---

## 📞 SUPPORT

En cas de problème :
1. Consultez les logs : `tail -f ~/logs/error_log`
2. Vérifiez le README.md pour la configuration
3. Testez en local d'abord avec `python3 app.py`
4. Vérifiez que Git est bien à jour : `git status`

**Dernière mise à jour :** 4 Janvier 2026, 15h00

