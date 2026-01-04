#!/bin/bash

# ============================================
# Script de déploiement AquaCoach pour o2switch
# ============================================

echo "🌊 =========================================="
echo "   DÉPLOIEMENT AQUACOACH"
echo "========================================== 🌊"
echo ""

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Pull des dernières modifications depuis GitHub
echo "📥 Récupération des dernières modifications..."
git pull origin main
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Git pull réussi${NC}"
else
    echo -e "${RED}❌ Erreur lors du git pull${NC}"
    exit 1
fi
echo ""

# 2. Installation/mise à jour des dépendances
echo "📦 Installation des dépendances Python..."
pip3 install --user -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dépendances installées${NC}"
else
    echo -e "${YELLOW}⚠️ Attention : Erreur lors de l'installation des dépendances${NC}"
fi
echo ""

# 3. Vérifier/créer le dossier instance
echo "📁 Vérification du dossier instance..."
if [ ! -d "instance" ]; then
    mkdir -p instance
    echo -e "${GREEN}✅ Dossier instance créé${NC}"
else
    echo -e "${GREEN}✅ Dossier instance existe${NC}"
fi
echo ""

# 4. Appliquer les migrations de base de données
echo "🗄️ Application des migrations..."
python3 -c "from app import init_db; init_db()"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations appliquées${NC}"
else
    echo -e "${YELLOW}⚠️ Attention : Erreur lors des migrations${NC}"
fi
echo ""

# 5. Vérifier et corriger les permissions
echo "🔐 Configuration des permissions..."

# Permissions sur le dossier instance
chmod 755 instance/ 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Permissions sur instance/ : 755${NC}"
fi

# Permissions sur la base de données (si elle existe)
if [ -f "instance/aquacoach.db" ]; then
    chmod 664 instance/aquacoach.db
    echo -e "${GREEN}✅ Permissions sur aquacoach.db : 664${NC}"
else
    echo -e "${YELLOW}⚠️ Base de données non trouvée (normal si première installation)${NC}"
fi
echo ""

# 6. Redémarrer Passenger (serveur WSGI)
echo "🔄 Redémarrage de Passenger..."
mkdir -p tmp
touch tmp/restart.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Passenger redémarré${NC}"
else
    echo -e "${YELLOW}⚠️ Impossible de redémarrer Passenger (créer tmp/restart.txt manuellement)${NC}"
fi
echo ""

# 7. Vérifier la configuration .htaccess
echo "⚙️ Vérification de la configuration..."
if [ -f ".htaccess" ]; then
    echo -e "${GREEN}✅ .htaccess présent${NC}"
    
    # Vérifier si l'utilisateur a modifié le fichier
    if grep -q "VOTRE_USER" .htaccess; then
        echo -e "${YELLOW}⚠️ ATTENTION : Modifier VOTRE_USER dans .htaccess${NC}"
    fi
    
    if grep -q "CHANGEZ_MOI" .htaccess; then
        echo -e "${YELLOW}⚠️ ATTENTION : Modifier SECRET_KEY dans .htaccess${NC}"
    fi
else
    echo -e "${RED}❌ .htaccess manquant${NC}"
fi

if [ -f "passenger_wsgi.py" ]; then
    echo -e "${GREEN}✅ passenger_wsgi.py présent${NC}"
else
    echo -e "${RED}❌ passenger_wsgi.py manquant${NC}"
fi
echo ""

# 8. Vérifier que la base n'est pas dans Git
echo "🔍 Vérification Git..."
if git ls-files | grep -q "\.db$"; then
    echo -e "${RED}❌ ATTENTION : Fichiers .db présents dans Git !${NC}"
    echo "   Exécuter : git rm --cached instance/*.db"
else
    echo -e "${GREEN}✅ Aucun fichier .db dans Git${NC}"
fi
echo ""

# 9. Diagnostic des permissions
echo "🔬 Diagnostic des permissions..."
ls -la instance/ 2>/dev/null | head -n 5
echo ""

# 10. Résumé
echo "🌊 =========================================="
echo "   DÉPLOIEMENT TERMINÉ !"
echo "========================================== 🌊"
echo ""
echo -e "${GREEN}✅ Site déployé avec succès !${NC}"
echo ""
echo "📝 Checklist post-déploiement :"
echo "   1. Modifier .htaccess (VOTRE_USER et SECRET_KEY)"
echo "   2. Tester les modifications admin en ligne"
echo "   3. Vérifier les logs : ~/logs/error_log"
echo "   4. Tester les requêtes POST"
echo ""
echo "🔗 Accès : http://votre-domaine.com"
echo "🔑 Admin : http://votre-domaine.com/admin/login"
echo ""


