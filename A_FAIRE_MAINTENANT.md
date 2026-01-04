# 🚀 DÉPLOIEMENT RAPIDE - À FAIRE MAINTENANT

**Date :** 4 Janvier 2026  
**Statut :** ✅ Toutes les modifications sont sur GitHub - Prêt à déployer !

---

## 🎯 MÉTHODE RAPIDE (RECOMMANDÉE)

### Sur votre serveur o2switch (via SSH ou terminal cPanel) :

```bash
# 1. Aller dans le répertoire
cd ~/www/natation

# 2. Lancer le script automatique
./deploy_o2switch.sh
```

**C'est tout ! Le script fait tout automatiquement en 8 étapes.**

---

## 📋 OU MÉTHODE MANUELLE

Si le script ne fonctionne pas, suivez ces étapes :

### 1. Pull GitHub
```bash
cd ~/www/natation
git pull origin main
```

### 2. Migrations BDD
```bash
/usr/bin/python3.10 -c "from app import init_db; init_db()"
```

### 3. Permissions
```bash
chmod 755 static/images static/uploads instance
chmod 664 instance/aquacoach.db
```

### 4. Redémarrer
```bash
mkdir -p tmp
touch tmp/restart.txt
```

---

## ✅ CE QUI VA ÊTRE DÉPLOYÉ

### Nouvelles fonctionnalités :
1. 📸 **Modification photos nageurs depuis admin** (upload, suppression, preview)
2. 🎉 **Page confirmation inscription nageur** (design moderne)
3. 📧 **Emails inscription nageur** (nageur + admin)
4. 🖼️ **Image par défaut SVG** pour nageurs sans photo
5. ✨ **Affichage photos corrigé** sur toute la plateforme

### Commits déployés :
- `394ee65` - Système d'email inscription nageur
- `bfc8cff` - Correction affichage photos + image par défaut
- `730015a` - Modification photos nageurs depuis admin
- `74229b9` - Guide et script de déploiement

---

## 🧪 TESTS À FAIRE APRÈS DÉPLOIEMENT

### 1. Page d'accueil
- ✅ Voir que les photos des nageurs s'affichent
- ✅ Voir l'image par défaut pour nageurs sans photo

### 2. Inscription nageur
- Aller sur : `votre-site.com/inscription_nageur`
- Remplir le formulaire avec une photo
- ✅ Voir la belle page de confirmation
- ✅ Recevoir l'email de bienvenue

### 3. Admin - Modification photo
- Se connecter à l'admin
- Modifier un nageur
- ✅ Voir la photo actuelle
- ✅ Uploader une nouvelle photo
- ✅ Voir la prévisualisation
- ✅ Enregistrer et vérifier

---

## ❓ EN CAS DE PROBLÈME

### Photos ne s'affichent pas ?
```bash
chmod -R 755 static/uploads static/images
```

### Erreur "column does not exist" ?
```bash
/usr/bin/python3.10 -c "from app import init_db; init_db()"
```

### Page 500 ?
```bash
tail -50 ~/logs/error_log
```

---

## 📞 AIDE COMPLÈTE

Pour plus de détails, consultez :
- **DEPLOIEMENT_MAINTENANT.md** - Guide complet avec toutes les solutions
- **README.md** - Configuration générale du site

---

## 🎉 RÉSUMÉ

✅ **Toutes les modifications sont sur GitHub**  
✅ **Script de déploiement automatique prêt**  
✅ **Documentation complète disponible**  
✅ **Prêt à déployer en production !**

**Il suffit de lancer : `./deploy_o2switch.sh`**

---

**Bon déploiement ! 🚀**

