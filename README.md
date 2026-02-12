# 📱 DarwinxShare V8 - Guide d'Utilisation

Application desktop pour partager facilement des fichiers entre votre PC Linux et votre iPhone via WiFi.

## 🚀 Installation

### Option 1 : Utiliser l'AppImage (Recommandé)

1. **Télécharger l'AppImage** (une fois générée)
   ```bash
   # Rendre l'AppImage exécutable
   chmod +x DarwinxShare-8.0-x86_64.AppImage
   ```

2. **Lancer l'application**
   ```bash
   ./DarwinxShare-8.0-x86_64.AppImage
   ```

### Option 2 : Exécuter depuis les sources

1. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

2. **Lancer l'application**
   ```bash
   python main.py
   ```

## 📖 Utilisation

### 1. Configuration initiale

1. **Lancez l'application** - Une fenêtre graphique s'ouvre
2. **Choisissez le dossier à partager** (par défaut : `~/Downloads`)
   - Cliquez sur "Changer" pour sélectionner un autre dossier
3. **Configurez les identifiants** :
   - Utilisateur : `admin` (modifiable)
   - Mot de passe : `1234` (modifiable)

### 2. Démarrer le serveur

1. Cliquez sur **"Démarrer le Serveur"**
2. Le navigateur s'ouvre automatiquement sur votre PC
3. L'URL réseau s'affiche dans les logs (exemple : `http://192.168.1.10:8000`)

### 3. Connexion depuis l'iPhone

#### Prérequis
- ✅ PC et iPhone connectés au **même réseau WiFi**

#### Étapes
1. Sur votre iPhone, ouvrez **Safari**
2. Entrez l'URL affichée dans les logs (ex: `http://192.168.1.10:8000`)
3. Entrez vos identifiants (utilisateur/mot de passe)
4. Vous accédez à l'interface de partage !

### 4. Fonctionnalités disponibles

#### 📤 Envoyer des fichiers depuis l'iPhone
1. En bas de la page, cliquez sur **"Choisir un fichier"**
2. Sélectionnez une ou plusieurs photos/vidéos/fichiers
3. Cliquez sur **"Envoyer Fichier"**
4. Les fichiers sont transférés vers votre PC !

#### 📥 Télécharger des fichiers depuis le PC
1. Naviguez dans les dossiers
2. Cliquez sur un fichier pour le télécharger
3. Le fichier est sauvegardé dans les téléchargements de Safari

#### 🎬 Lire des vidéos en streaming
1. Cliquez sur une vidéo (MP4, MOV, MKV, etc.)
2. Un lecteur vidéo s'ouvre directement dans le navigateur
3. Pas besoin de télécharger la vidéo complète !

#### 📦 Télécharger un dossier complet
1. Cliquez sur l'icône **⬇️** en haut à droite d'un dossier
2. Le dossier est compressé en ZIP et téléchargé

#### 🔍 Rechercher des fichiers
- Utilisez la barre de recherche en haut de la page
- Filtrage en temps réel

## 🛠️ Générer l'AppImage

Si vous voulez créer votre propre AppImage :

```bash
# Installer python-appimage
pip install python-appimage --user

# Lancer le script de build
./build_appimage.sh
```

L'AppImage sera créée dans le dossier `dist/`.

## 🔧 Dépannage

### Le serveur ne démarre pas
- Vérifiez que le port 8000 n'est pas déjà utilisé
- Essayez de redémarrer l'application

### L'iPhone ne peut pas se connecter
- ✅ Vérifiez que PC et iPhone sont sur le **même WiFi**
- ✅ Vérifiez que le pare-feu ne bloque pas le port 8000
  ```bash
  # Autoriser le port 8000 (UFW)
  sudo ufw allow 8000
  ```
- ✅ Utilisez l'URL réseau (pas 127.0.0.1)

### Les fichiers ne s'uploadent pas
- Vérifiez les permissions du dossier partagé
- Vérifiez l'espace disque disponible

### Vidéo ne se lit pas sur iPhone
- Certains formats peuvent ne pas être supportés par Safari
- Essayez de télécharger la vidéo au lieu de la lire en streaming

## 🔐 Sécurité

⚠️ **Important** :
- Cette application est conçue pour un usage **local** (réseau domestique)
- N'exposez **jamais** ce serveur sur Internet sans sécurité supplémentaire
- Changez les identifiants par défaut
- Le mot de passe est masqué dans l'interface mais visible dans les logs

## 📝 Formats supportés

| Type | Extensions |
|------|-----------|
| 🖼️ Images | png, jpg, jpeg, gif, webp |
| 🎬 Vidéos | mp4, mov, mkv, avi, webm |
| 🎵 Audio | mp3, wav, flac |
| 📦 Archives | zip, rar, 7z, tar, gz |
| 📕 Documents | pdf |
| 🧑‍💻 Code | py, c, cpp, html, js |

## 💡 Astuces

1. **Partage rapide de photos** : Sélectionnez plusieurs photos sur iPhone et uploadez-les en une fois
2. **Streaming de films** : Regardez vos films PC directement sur iPhone sans les télécharger
3. **Backup automatique** : Configurez le dossier partagé vers votre dossier de backup
4. **Accès multi-appareils** : Tous les appareils sur le même WiFi peuvent se connecter simultanément

## 📞 Support

Pour toute question ou problème :
- Vérifiez les logs dans l'application
- Consultez la section Dépannage ci-dessus

---

**Version** : 8.0  
**Compatibilité** : Linux (toutes distributions), iPhone/iPad (Safari)
