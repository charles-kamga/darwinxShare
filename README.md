# DarwinxShare 🗂️📱 — v1.8.2 Pro

**DarwinxShare** est une application desktop hybride (Python/Flask/CustomTkinter) ultra-optimisée pour le partage de fichiers entre Linux et iOS via Wi-Fi. Elle transforme votre PC en un serveur de fichiers élégant, accessible instantanément par n'importe quel iPhone ou iPad, sans câble et sans installation tierce.

---

## 🚀 Nouveautés de la Version 1.8.2 Pro
- **Packaging Robuste** : Exécutable unifié (One-File) incluant toutes les dépendances (Pillow, CustomTkinter).
- **Stabilité Serveur Plus** : Gestion intelligente du port 8000 avec vérification de disponibilité au démarrage et shutdown synchrone pour éviter les conflits réseau.
- **Build Automatisé** : Script de build optimisé utilisant l'environnement virtuel garantissant une compilation fidèle.

---

## 🌟 Fonctionnalités Clés

### 📱 Expérience Mobile Native
- **6 Thèmes au choix** : iOS (Sombre/Clair), iOS 18 Bento (style Dynamic Island), macOS Finder, Cyberpunk et Classique.
- **Fluidité Totale** : Upload avec barre de progression AJAX et navigation préchargée (TTL 5s).

### 🎬 Streaming & Transferts
- **Streaming Safari** : Support du protocole HTTP 206 pour une lecture fluide des vidéos sans téléchargement complet.
- **Téléchargement Massif** : Génération d'archives ZIP à la volée pour les dossiers.
- **Compatibilité iOS** : Headers forcés pour garantir la sauvegarde des fichiers dans l'application "Fichiers" d'Apple.

### 🔒 Sécurité & Performance
- **Basic Auth** : Accès protégé par identifiants configurables.
- **Active Defense** : Bannissement automatique des IPs suspectes après 10 tentatives échouées.
- **Turbo Mode** : Compression Gzip des données (-80% de bande passante) et cache mémoire intelligent.

---

## 🛠️ Installation & Build

### Pour les utilisateurs (Linux)
Récupérez l'AppImage ou le paquet `.deb` dans la section [Releases](https://github.com/charles-kamga/darwinxShare/releases) :
```bash
chmod +x DarwinxShare-v1.8.2-x86_64.AppImage
./DarwinxShare-v1.8.2-x86_64.AppImage
```

### Pour les développeurs
1. Clonez le projet :
   ```bash
   git clone https://github.com/charles-kamga/darwinxShare.git
   cd darwinxshare
   ```
2. Installez les dépendances via le venv :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install customtkinter qrcode Pillow flask werkzeug darkdetect
   ```
3. Compilez votre propre version :
   ```bash
   ./build_all.sh
   ```

---

## 💻 Utilisation
1. **Configurez** votre dossier source et vos identifiants dans l'onglet `CONFIG`.
2. **Activez** le partage (WiFi ou Hotspot) depuis le `DASHBOARD`.
3. **Scannez** le QR Code avec votre iPhone.
4. **Gérez** vos fichiers comme un pro !

---

*Développé avec ❤️ par Charles Kamga pour la communauté Linux.*
