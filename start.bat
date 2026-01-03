@echo off
echo.
echo 🌊 Démarrage d'AquaConnect...
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
    echo ✅ Environnement virtuel créé
)

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer/mettre à jour les dépendances
echo 📥 Installation des dépendances...
pip install -r requirements.txt --quiet

echo.
echo ✨ AquaConnect est prêt!
echo 🌐 Ouvrez votre navigateur à l'adresse: http://localhost:8080
echo.
echo 📊 Pages disponibles:
echo    - Accueil: http://localhost:8080
echo    - Admin: http://localhost:8080/admin
echo.
echo ⏹️  Pour arrêter l'application, appuyez sur Ctrl+C
echo.

REM Lancer l'application
python app.py

pause
