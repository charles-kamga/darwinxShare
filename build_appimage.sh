#!/bin/bash
# Script de build pour créer l'AppImage de Kali Share V8

set -e  # Arrêter en cas d'erreur

echo "╔═══════════════════════════════════════════════════╗"
echo "║   Build AppImage - Kali Share V8                  ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Variables
APP_NAME="DarwinxShare"
APP_VERSION="8.0"
PYTHON_VERSION="3.11"

# Vérifier que python-appimage est installé
if ! command -v python-appimage &> /dev/null; then
    echo "[!] python-appimage n'est pas installé."
    echo "[i] Installation en cours..."
    pip install python-appimage --user
fi

# Créer le dossier de build
echo "[1/5] Préparation de l'environnement..."
rm -rf build dist
mkdir -p build

# Copier les fichiers nécessaires
echo "[2/5] Copie des fichiers..."
cp main.py build/
cp requirements.txt build/
cp icon.png build/
cp darwinxshare.desktop build/

# Créer l'AppImage
echo "[3/5] Génération de l'AppImage..."
cd build

python-appimage build app \
    -l manylinux2014_x86_64 \
    -p ${PYTHON_VERSION} \
    main.py

# Renommer l'AppImage
echo "[4/5] Finalisation..."
cd ..
mkdir -p dist

# Trouver l'AppImage généré et le renommer
GENERATED_APPIMAGE=$(find build -name "*.AppImage" -type f | head -n 1)

if [ -f "$GENERATED_APPIMAGE" ]; then
    mv "$GENERATED_APPIMAGE" "dist/${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
    chmod +x "dist/${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
    
    echo ""
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║   ✓ BUILD RÉUSSI !                                ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo ""
    echo "[✓] AppImage créée : dist/${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
    echo ""
    echo "[i] Pour l'exécuter :"
    echo "    chmod +x dist/${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
    echo "    ./dist/${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
    echo ""
else
    echo "[!] Erreur : AppImage non générée"
    exit 1
fi

# Nettoyage optionnel
echo "[5/5] Nettoyage..."
# Décommenter pour supprimer le dossier build
# rm -rf build

echo "[✓] Terminé !"
