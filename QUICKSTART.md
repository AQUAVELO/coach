# 🚀 DÉMARRAGE RAPIDE - AquaCoach

## Installation en 3 étapes

### 1️⃣ Installer Python (si pas déjà fait)
- **macOS**: `brew install python3` ou télécharger depuis python.org
- **Windows**: Télécharger depuis python.org
- **Linux**: `sudo apt-get install python3 python3-pip python3-venv`

### 2️⃣ Lancer l'application

**Option A - Script automatique (recommandé):**

**macOS/Linux:**
```bash
cd aquaconnect
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
cd aquaconnect
start.bat
```

**Option B - Manuel:**
```bash
cd aquaconnect

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

### 3️⃣ Ouvrir dans le navigateur

**http://localhost:8080**

## 🎯 Accès Rapide

- **Page d'accueil**: http://localhost:8080
- **Inscription client**: http://localhost:8080/inscription_client
- **Inscription nageur**: http://localhost:8080/inscription_nageur
- **Administration**: http://localhost:8080/admin

## 📊 Données de Test

### Nageurs Pré-enregistrés (Département 06)
1. Léa Martin - 35€/séance - BEESAN
2. Lucas Dubois - 30€/séance - BPJEPS
3. Chloé Bernard - 40€/séance - BEESAN
4. Hugo Petit - 45€/séance - BPJEPS
5. Manon Roux - 38€/séance - BEESAN

### Test du Parcours Complet

**En tant que Client:**
1. Cliquez sur "Trouver un maître nageur"
2. Remplissez le formulaire (département 06 recommandé)
3. Sélectionnez un nageur dans la liste
4. Cliquez sur "Confirmer mon choix"
5. Validez le paiement (simulé)
6. Recevez les coordonnées du nageur

**En tant que Nageur:**
1. Cliquez sur "Vous êtes Maître Nageur"
2. Remplissez votre profil complet
3. Votre profil apparaît sur la page d'accueil

## ⚙️ Configuration

### Changer le Port
Si le port 8080 est déjà utilisé, modifiez dans `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=3000)  # ou autre port
```

### Réinitialiser la Base de Données
```bash
rm instance/aquaconnect.db
python app.py  # Recrée automatiquement avec données de démo
```

## 🐛 Problèmes Courants

**"Port already in use"**
→ Changez le port dans app.py ou tuez le processus:
```bash
# macOS/Linux
lsof -i :8080
kill -9 PID

# Windows
netstat -ano | findstr :8080
taskkill /PID xxxx /F
```

**"ModuleNotFoundError: No module named 'flask'"**
→ Activez l'environnement virtuel et réinstallez:
```bash
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

**L'application ne démarre pas**
→ Vérifiez la version de Python:
```bash
python --version  # Doit être 3.8+
```

## 📁 Structure Essentielle

```
aquaconnect/
├── app.py              # ⚙️ Application principale
├── start.sh/.bat       # 🚀 Scripts de lancement
├── requirements.txt    # 📦 Dépendances
├── instance/           # 💾 Base de données (créée auto)
├── templates/          # 📄 Pages HTML
└── static/            # 🎨 Images et CSS
```

## 🎨 Fonctionnalités

✅ Inscription client et nageur
✅ Recherche par département
✅ Profils détaillés avec photos
✅ Paiement simulé (5€)
✅ Dashboard administrateur
✅ Base de données SQLite intégrée
✅ Interface responsive

## 📝 Notes

- **Paiement**: Simulé dans cette version locale
- **Emails**: Désactivés (pas de serveur SMTP)
- **Base de données**: SQLite (facile, aucune config)
- **Photos**: Stockées dans static/uploads/

## 🔄 Mise à Jour

Pour mettre à jour l'application:
```bash
cd aquaconnect
git pull  # si vous utilisez git
pip install -r requirements.txt --upgrade
```

## 📖 Documentation Complète

Consultez **README.md** pour la documentation complète.

---

**🌊 Profitez d'AquaConnect !**

Si vous avez des questions, consultez le README.md ou les logs dans le terminal.
