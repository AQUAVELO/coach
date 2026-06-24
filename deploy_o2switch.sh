#!/bin/bash

# 🚀 Script de déploiement AquaCoach sur o2switch
# Usage: ./deploy_o2switch.sh
# Assurez-vous d'être connecté en SSH sur votre serveur o2switch

echo "🌊 =========================================="
echo "   DÉPLOIEMENT AQUACOACH SUR O2SWITCH"
echo "========================================== 🌊"
echo ""

# Configuration
APP_DIR=~/www/natation
PYTHON_BIN=/usr/bin/python3.10

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier que nous sommes dans le bon répertoire
log_info "Vérification du répertoire..."
if [ ! -f "$APP_DIR/app.py" ]; then
    log_error "Le fichier app.py n'existe pas dans $APP_DIR"
    log_error "Vérifiez que le chemin APP_DIR est correct dans le script"
    exit 1
fi
log_success "Répertoire correct : $APP_DIR"
echo ""

# Étape 1 : Sauvegarde de la base de données
log_info "ÉTAPE 1/8 : Sauvegarde de la base de données..."
cd "$APP_DIR" || exit
if [ -f "instance/aquacoach.db" ]; then
    BACKUP_FILE="instance/aquacoach_backup_$(date +%Y%m%d_%H%M%S).db"
    cp instance/aquacoach.db "$BACKUP_FILE"
    log_success "Base de données sauvegardée : $BACKUP_FILE"
else
    log_warning "Aucune base de données à sauvegarder"
fi
echo ""

# Étape 2 : Pull des modifications depuis GitHub
log_info "ÉTAPE 2/8 : Récupération des dernières modifications depuis GitHub..."
git pull origin main
if [ $? -eq 0 ]; then
    log_success "Modifications récupérées avec succès"
else
    log_error "Erreur lors du git pull"
    log_warning "Vérifiez votre connexion et vos permissions GitHub"
    exit 1
fi
echo ""

# Étape 3 : Installation/Mise à jour des dépendances Python
log_info "ÉTAPE 3/8 : Installation des dépendances Python..."
$PYTHON_BIN -m pip install -r requirements.txt --user --upgrade
if [ $? -eq 0 ]; then
    log_success "Dépendances installées"
else
    log_warning "Erreur lors de l'installation des dépendances (peut être normal si déjà installées)"
fi
echo ""

# Étape 4 : Création des dossiers nécessaires
log_info "ÉTAPE 4/8 : Vérification de la structure des dossiers..."
mkdir -p static/images
mkdir -p static/uploads
mkdir -p instance
mkdir -p tmp
log_success "Dossiers créés/vérifiés"
echo ""

# Étape 5 : Configuration des permissions
log_info "ÉTAPE 5/8 : Configuration des permissions..."
chmod 755 static/images
chmod 755 static/uploads
chmod 755 instance
if [ -f "instance/aquacoach.db" ]; then
    chmod 664 instance/aquacoach.db
fi
log_success "Permissions configurées"
echo ""

# Étape 6 : Application des migrations de base de données
log_info "ÉTAPE 6/8 : Application des migrations de base de données..."
$PYTHON_BIN -c "from app import init_db; init_db()" 2>&1
if [ $? -eq 0 ]; then
    log_success "Migrations appliquées avec succès"
else
    log_error "Erreur lors des migrations"
    log_warning "Vérifiez les logs ci-dessus pour plus de détails"
fi
echo ""

# Étape 7 : Vérification des fichiers critiques
log_info "ÉTAPE 7/8 : Vérification des fichiers critiques..."
FILES_OK=true

if [ -f "static/images/default-swimmer.svg" ]; then
    log_success "Image par défaut présente"
else
    log_error "Image par défaut manquante : static/images/default-swimmer.svg"
    FILES_OK=false
fi

if [ -f "templates/confirmation_inscription_nageur.html" ]; then
    log_success "Template confirmation inscription présent"
else
    log_error "Template manquant : confirmation_inscription_nageur.html"
    FILES_OK=false
fi

if [ -f "templates/edit_nageur.html" ]; then
    log_success "Template edit nageur présent"
else
    log_error "Template manquant : edit_nageur.html"
    FILES_OK=false
fi

if [ "$FILES_OK" = false ]; then
    log_error "Certains fichiers sont manquants. Déploiement incomplet !"
    exit 1
fi
echo ""

# Étape 8 : Redémarrage de l'application Passenger
log_info "ÉTAPE 8/8 : Redémarrage de l'application..."
mkdir -p tmp
touch tmp/restart.txt
log_success "Application redémarrée (Passenger)"
echo ""

# Résumé
echo "🎉 =========================================="
echo "   DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !"
echo "========================================== 🎉"
echo ""
log_success "AquaCoach a été déployé sur o2switch"
echo ""
echo "📋 PROCHAINES ÉTAPES :"
echo "   1. Testez votre site dans le navigateur"
echo "   2. Vérifiez l'affichage des photos"
echo "   3. Testez l'inscription d'un nageur"
echo "   4. Testez la modification de photo depuis l'admin"
echo "   5. Vérifiez l'envoi des emails"
echo ""
echo "📊 Informations utiles :"
echo "   - Logs d'erreur : tail -f ~/logs/error_log"
echo "   - Backups BDD : $APP_DIR/instance/aquacoach_backup_*.db"
echo "   - Redémarrer : touch $APP_DIR/tmp/restart.txt"
echo ""
log_info "En cas de problème, consultez DEPLOIEMENT_MAINTENANT.md"
echo ""

