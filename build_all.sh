#!/bin/bash
set -e

APP_NAME="darwinxshare"
VERSION="1.8.2"
ARCH=$(uname -m)
if [ "$ARCH" == "x86_64" ]; then DEB_ARCH="amd64"; else DEB_ARCH=$ARCH; fi

echo "--- 🛠️ Début du Build DarwinxShare v$VERSION ---"

# 1. Nettoyage
echo "🧹 Nettoyage des dossiers de build..."
rm -rf build dist AppDir

# 2. PyInstaller (Utilisation du venv et du fichier .spec)
echo "📦 Compilation avec PyInstaller via darwinxshare.spec..."
./venv/bin/pyinstaller --noconfirm darwinxshare.spec

# 3. Préparation du Paquet DEB
echo "📦 Création du paquet .deb..."
DEB_DIR="dist/${APP_NAME}_${VERSION}_${DEB_ARCH}"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"

# Fichier control
cat <<EOT > "$DEB_DIR/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $DEB_ARCH
Maintainer: Charles Kamga
Description: DarwinxShare Pro - Partage de fichiers PC/Mobile ultra-rapide (v$VERSION)
EOT

# Copie des fichiers
cp "dist/$APP_NAME" "$DEB_DIR/usr/bin/"
cp "darwinxshare.desktop" "$DEB_DIR/usr/share/applications/"
cp "static/logo.png" "$DEB_DIR/usr/share/icons/hicolor/256x256/apps/darwinxshare.png"

# Build du .deb
dpkg-deb --build "$DEB_DIR"

# 4. Préparation de l'AppImage
echo "💎 Préparation de l'AppImage..."
mkdir -p AppDir/usr/bin
cp "dist/$APP_NAME" AppDir/usr/bin/
cp "static/logo.png" AppDir/darwinxshare.png
cp "darwinxshare.desktop" AppDir/
ln -sf usr/bin/$APP_NAME AppDir/AppRun

# Tentative de build AppImage
if [ -f "./appimagetool" ]; then
    echo "🚀 Génération de l'AppImage via appimagetool local..."
    # On rend l'outil exécutable au cas où
    chmod +x ./appimagetool
    ARCH=x86_64 ./appimagetool AppDir "dist/DarwinxShare-v$VERSION-$ARCH.AppImage"
elif command -v appimagetool >/dev/null 2>&1; then
    echo "🚀 Génération de l'AppImage via appimagetool système..."
    ARCH=x86_64 appimagetool AppDir "dist/DarwinxShare-v$VERSION-$ARCH.AppImage"
else
    echo "⚠️ appimagetool non trouvé. L'AppImage n'a pas pu être générée."
fi

echo "--- ✅ Build terminé avec succès ! ---"
ls -lh dist/*.deb 2>/dev/null || true
ls -lh dist/*.AppImage 2>/dev/null || true
