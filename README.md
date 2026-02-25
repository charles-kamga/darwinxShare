# DarwinxShare 🗂️📱

**DarwinxShare** est une application desktop hybride (Python/Flask/CustomTkinter) conçue pour répondre à un problème concret : l'absence d'une solution simple pour gérer un iPhone depuis Linux. Elle permet de partager et transférer des fichiers entre un PC Linux et un iPhone via le Wi-Fi, sans câble et sans installation sur le téléphone.

---

## 🌟 Fonctionnalités

### 📱 Interface Mobile Optimisée
- **6 thèmes visuels** sélectionnables depuis l'interface PC :
  - `iOS (Sombre)` *(par défaut)* — style iOS natif en mode nuit
  - `iOS (Clair)` — style iOS natif lumineux
  - `iOS 18 Bento` — grille style Dynamic Island (principalement pour PC)
  - `macOS (Plastique)` — fenêtre façon Finder macOS
  - `Cyberpunk` — interface terminal hacker
  - `Classique` — UI originale épurée

### 🚀 Transferts de Fichiers
- **Upload depuis l'iPhone** → barre de progression en temps réel intégrée dans le bouton (AJAX, pas de rechargement)
- **Téléchargement de fichiers** → bouton dédié sur chaque carte (vidéos, images, audio, documents)
- **Téléchargement de dossiers** → archive ZIP générée à la volée
- **Téléchargement forcé** → headers `Content-Disposition: attachment` + `application/octet-stream` pour garantir la sauvegarde sur iOS

### 🎬 Streaming Vidéo & Audio (Safari iOS)
- Support complet des requêtes **HTTP 206 Partial Content** (Range headers)
- Avance rapide / retour en arrière fonctionnels dans Safari
- Chunks de **4 MB** pour un streaming fluide sur WiFi local

### 🔒 Sécurité
- **Authentification HTTP Basic** avec identifiants configurables
- **Bannissement d'IP automatique** : après 3 échecs de connexion en moins de 5 minutes, l'adresse IP est temporairement bloquée

### 📊 Traçabilité
- **Journal d'accès** (`~/darwinx_access.log`) : chaque accès, upload et tentative échouée est enregistré
- **Onglet LOGS** dans l'interface PC : visualisation en direct du journal, avec boutons Rafraîchir et Vider

### ⚡ Performance
- **Compression Gzip** automatique des réponses HTML (–80% de données transférées)
- **Cache mémoire** du listing de dossier (TTL 5s) — évite les lectures disque répétées
- **Prefetch navigateur** : les dossiers sont préchargés au survol pour une navigation quasi-instantanée

---

## 🚀 Installation & Lancement

### Méthode 1 : AppImage (Recommandée)
Compatible avec toutes les distributions Linux sans gestion de dépendances.

```bash
chmod +x DarwinxShare-x86_64.AppImage
./DarwinxShare-x86_64.AppImage
```

### Méthode 2 : Depuis les Sources

**Prérequis** : `python3` et `pip`

```bash
git clone https://github.com/VOTRE_NOM/darwinxshare.git
cd darwinxshare
python3 -m venv venv
source venv/bin/activate
pip install customtkinter qrcode Pillow werkzeug flask
python3 main.py
```

---

## 💻 Guide d'Utilisation

1. **CONFIG** — Choisissez le dossier à partager, définissez identifiant/mot de passe, sélectionnez le thème visuel.
2. **DASHBOARD** — Cliquez sur **ACTIVER LE PARTAGE**. Un QR Code s'affiche.
3. **Sur l'iPhone** — Scannez le QR code, ouvrez dans **Safari**, entrez les identifiants.
4. **Navigation** — Parcourez les fichiers, lisez les vidéos directement ou téléchargez-les via le bouton dédié.
5. **LOGS** — Consultez l'historique des accès depuis l'onglet 📜 LOGS de l'interface PC.

---

## 🤝 Contribuer

DarwinxShare est **open-source** et vise à devenir la référence de transfert fichiers Linux ↔ iPhone.

Les contributions sont les bienvenues : nouveaux thèmes, optimisations réseau, support de nouvelles plateformes mobiles, miniatures d'images, playlists audio...

Ouvrez une *Issue* ou soumettez une *Pull Request* !

---

*Développé avec ❤️ pour la communauté Linux.*
