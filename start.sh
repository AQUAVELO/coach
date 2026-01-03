#!/bin/bash

echo "🌊 Démarrage d'AquaConnect..."
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer/mettre à jour les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt --quiet

echo ""
echo "✨ AquaConnect est prêt!"
echo "🌐 Ouvrez votre navigateur à l'adresse: http://localhost:8080"
echo ""
echo "📊 Pages disponibles:"
echo "   - Accueil: http://localhost:8080"
echo "   - Admin: http://localhost:8080/admin"
echo ""
echo "⏹️  Pour arrêter l'application, appuyez sur Ctrl+C"
echo ""

# Lancer l'application
python app.py
