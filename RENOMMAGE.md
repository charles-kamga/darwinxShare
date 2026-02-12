# Renommage de l'Application - DarwinxShare

## 🎯 Changement Effectué

L'application a été renommée de **"Kali Share"** vers **"DarwinxShare"** pour refléter son usage universel (pas uniquement sur Kali Linux).

**Signification du nom :** Darwin est le noyau d'iOS/macOS, ce qui fait une référence technique pertinente pour une application de partage PC ↔ iPhone.

---

## 📝 Fichiers Modifiés

### [main.py](file:///home/charles/Documents/Work/Serveur_Pc_Phone/Executable/main.py)

**Changements :**
- Titre de la fenêtre : `DarwinxShare V8 - Desktop Edition`
- En-tête HTML : `<title>DarwinxShare V8 🎬</title>`
- Logo dans l'interface : `<h1>DarwinxShare <span>V8</span></h1>`
- Header Tkinter : `DarwinxShare` (police Impact 24pt)
- Message de bienvenue : `Bienvenue sur DarwinxShare Desktop V8`

---

### [darwinxshare.desktop](file:///home/charles/Documents/Work/Serveur_Pc_Phone/Executable/darwinxshare.desktop)

**Changements :**
- Fichier renommé de `kali-share.desktop` → `darwinxshare.desktop`
- `Name=DarwinxShare`

---

### [build_appimage.sh](file:///home/charles/Documents/Work/Serveur_Pc_Phone/Executable/build_appimage.sh)

**Changements :**
- `APP_NAME="DarwinxShare"`
- Référence au fichier : `cp darwinxshare.desktop build/`
- Nom de l'AppImage générée : `DarwinxShare-8.0-x86_64.AppImage`

---

### [README_APP.md](file:///home/charles/Documents/Work/Serveur_Pc_Phone/Executable/README_APP.md)

**Changements :**
- Titre : `# 📱 DarwinxShare V8 - Guide d'Utilisation`
- Toutes les références aux commandes :
  - `chmod +x DarwinxShare-8.0-x86_64.AppImage`
  - `./DarwinxShare-8.0-x86_64.AppImage`

---

## ✅ Résultat

L'application est maintenant entièrement renommée en **DarwinxShare** :

- ✅ Interface graphique mise à jour
- ✅ Interface web mise à jour
- ✅ Scripts de build mis à jour
- ✅ Documentation mise à jour
- ✅ Fichiers de configuration renommés

**Prêt à utiliser :**
```bash
python3 main.py
```

**Prêt à builder :**
```bash
./build_appimage.sh
# Génère : dist/DarwinxShare-8.0-x86_64.AppImage
```
