import os
import socket
import mimetypes
import shutil
import tempfile
import argparse
from functools import wraps
from flask import Flask, request, send_from_directory, render_template_string, Response, send_file
from werkzeug.utils import secure_filename

# --- CONFIGURATION ---
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 0  # Pas de limite d'upload

# Variables par défaut (seront écrasées dans le terminal)
ROOT_DIR = os.path.expanduser("~/Downloads")
AUTH_USER = "admin"
AUTH_PASS = "admin"

# --- HTML / CSS / JS (Version Streaming V6) ---
HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Kali Share V7 🎬</title>
<style>
:root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --accent: #0ea5e9; --border: #334155; }
* { box-sizing: border-box; }
body { margin: 0; padding: 20px; background: var(--bg); color: var(--text); font-family: -apple-system, sans-serif; padding-bottom: 120px; }
a { text-decoration: none; color: inherit; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 15px; }
h1 { margin: 0; font-size: 1.4rem; color: var(--accent); }
.nav-bar { display: flex; gap: 8px; margin-bottom: 15px; flex-wrap: wrap; }
.nav-btn { background: var(--card); border: 1px solid var(--border); padding: 8px 12px; border-radius: 6px; font-size: 0.9rem; }
.search-box { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: white; margin-bottom: 20px; font-size: 16px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
.card { background: var(--card); padding: 15px; border-radius: 12px; text-align: center; border: 1px solid var(--border); display: block; position: relative; cursor: pointer; transition: 0.2s; }
.card:active { transform: scale(0.95); background: #334155; }
.card-icon { font-size: 2.5rem; display: block; margin-bottom: 5px; }
.card-name { font-size: 0.85rem; font-weight: 500; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.card-meta { font-size: 0.75rem; color: #94a3b8; margin-top: 4px; }
.zip-btn { position: absolute; top: 5px; right: 5px; font-size: 0.8rem; background: rgba(0,0,0,0.5); border-radius: 50%; width: 25px; height: 25px; line-height: 25px; }
.upload-zone { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(15,23,42,0.95); padding: 15px; border-top: 1px solid var(--border); backdrop-filter: blur(10px); z-index: 10; display: flex; flex-direction: column; gap: 10px; }
.upload-btn { background: var(--accent); color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; width: 100%; font-size: 1rem; }
input[type="file"] { background: var(--card); color: white; padding: 10px; border-radius: 8px; width: 100%; }
/* VIDEO PLAYER MODAL */
.modal { display: none; position: fixed; z-index: 999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.95); align-items: center; justify-content: center; flex-direction: column; }
.modal-content { max-width: 100%; max-height: 80%; width: auto; }
.close { position: absolute; top: 15px; right: 25px; color: #f1f1f1; font-size: 35px; font-weight: bold; cursor: pointer; z-index: 1000; }
.dl-link { color: var(--accent); margin-top: 20px; font-size: 1rem; text-decoration: underline; }
.msg { padding: 10px; margin-bottom: 15px; border-radius: 8px; text-align: center; }
.msg.ok { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid #22c55e; }
.msg.err { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid #ef4444; }
</style>
<script>
function filterFiles() {
    let input = document.getElementById('search').value.toLowerCase();
    document.querySelectorAll('.card').forEach(card => {
        let name = card.querySelector('.card-name').innerText.toLowerCase();
        card.style.display = name.includes(input) ? "block" : "none";
    });
}
function loading() {
    let btn = document.getElementById('upBtn');
    if(document.getElementById('fileIn').files.length > 0) {
        btn.innerText = "Envoi... ⏳"; btn.style.opacity = "0.7";
    }
}
function openPlayer(url, name) {
    var modal = document.getElementById("videoModal");
    var vid = document.getElementById("videoPlayer");
    var dl = document.getElementById("videoDl");
    vid.src = url;
    dl.href = url.replace("/view/", "/download/");
    dl.innerText = "Télécharger " + name;
    modal.style.display = "flex";
    vid.play();
}
function closePlayer() {
    var modal = document.getElementById("videoModal");
    var vid = document.getElementById("videoPlayer");
    vid.pause();
    vid.src = "";
    modal.style.display = "none";
}
</script>
</head>
<body>
<header>
    <h1>Kali Share <span style="font-size:0.7em">V7</span></h1>
    <div style="font-size:0.8rem; color:#4ade80">● {{ user }}</div>
</header>
{% if msg %}<div class="msg {{ type }}">{{ msg }}</div>{% endif %}
<div class="nav-bar">
    {% if parent is not none %}
    <a href="/?path={{ parent }}" class="nav-btn">⬅️ Retour</a>
    {% endif %}
    <span class="nav-btn" style="color:#94a3b8; background:transparent; border:none;">📂 /{{ path }}</span>
</div>
<input type="text" id="search" class="search-box" onkeyup="filterFiles()" placeholder="Rechercher...">
<div id="videoModal" class="modal">
    <span class="close" onclick="closePlayer()">&times; Fermer</span>
    <video id="videoPlayer" class="modal-content" controls playsinline controlsList="nodownload"></video>
    <a id="videoDl" href="#" class="dl-link" download>Télécharger la vidéo</a>
</div>
<div class="grid">
    {% for item in items %}
      {% if item.is_dir %}
      <a href="/?path={{ item.path }}" class="card">
         <span class="card-icon">📁</span>
         <div class="card-name">{{ item.name }}</div>
         <div class="card-meta">{{ item.count }} éléments</div>
         <object><a href="/zip/{{ item.path }}" class="zip-btn" title="Zip">⬇️</a></object>
      </a>
      {% elif item.is_video %}
      <div onclick="openPlayer('/view/{{ item.path }}', '{{ item.name }}')" class="card">
         <span class="card-icon">{{ item.icon }}</span>
         <div class="card-name">{{ item.name }}</div>
         <div class="card-meta">🎬 Lire • {{ item.size }}</div>
      </div>
      {% else %}
      <a href="/download/{{ item.path }}" class="card">
         <span class="card-icon">{{ item.icon }}</span>
         <div class="card-name">{{ item.name }}</div>
         <div class="card-meta">{{ item.size }}</div>
      </a>
      {% endif %}
    {% endfor %}
</div>
<div class="upload-zone">
  <form method="POST" enctype="multipart/form-data" onsubmit="loading()">
    <input type="file" name="file" multiple id="fileIn">
    <input type="hidden" name="path" value="{{ path }}">
    <button type="submit" class="upload-btn" id="upBtn">Envoyer Fichier</button>
  </form>
</div>
</body>
</html>
"""

# --- BACKEND ---
def check_auth(username, password):
    return username == AUTH_USER and password == AUTH_PASS

def authenticate():
    return Response('Login Required', 401, {'WWW-Authenticate': 'Basic realm="Login"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(('8.8.8.8', 80)); IP = s.getsockname()[0]
    except: IP = '127.0.0.1'
    finally: s.close()
    return IP

def safe_join(base, rel_path):
    if not rel_path: return base
    rel_path = os.path.normpath(rel_path).strip(os.sep)
    full = os.path.abspath(os.path.join(base, rel_path))
    if not full.startswith(base): return base
    return full

def get_file_info(filename):
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    icon = '📄'
    is_video = False
    if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']: icon = '🖼️'
    elif ext in ['mp4', 'mov', 'mkv', 'avi', 'webm']: icon = '🎬'; is_video = True
    elif ext in ['mp3', 'wav', 'flac']: icon = '🎵'
    elif ext in ['zip', 'rar', '7z', 'tar', 'gz']: icon = '📦'
    elif ext in ['pdf']: icon = '📕'
    elif ext in ['py', 'c', 'cpp', 'html', 'js']: icon = '🧑‍💻'
    return icon, is_video

def readable_size(size):
    for unit in ['o', 'Ko', 'Mo', 'Go']:
        if size < 1024: return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} To"

# --- ROUTES ---
@app.route("/", methods=["GET", "POST"])
@requires_auth
def index():
    rel_path = request.args.get("path", "")
    curr_dir = safe_join(ROOT_DIR, rel_path)
    msg, mtype = None, ""

    if request.method == "POST":
        post_path = request.form.get("path", "")
        up_dir = safe_join(ROOT_DIR, post_path)
        files = request.files.getlist("file")
        c = 0
        for f in files:
            if f.filename:
                fn = secure_filename(f.filename) or "temp"
                try: 
                    f.save(os.path.join(up_dir, fn))
                    c += 1
                except: pass
        if c: msg=f"✅ {c} fichier(s) reçu(s)"; mtype="ok"; rel_path=post_path; curr_dir=up_dir
        else: msg="❌ Erreur envoi"; mtype="err"

    items = []
    if os.path.exists(curr_dir):
        raw = os.listdir(curr_dir)
        dirs, files = [], []
        for n in raw:
            if n.startswith('.'): continue
            full = os.path.join(curr_dir, n)
            path_rel = os.path.join(rel_path, n)
            if os.path.isdir(full):
                try: count = len(os.listdir(full))
                except: count = "?"
                dirs.append({'name':n, 'path':path_rel, 'is_dir':True, 'count':count})
            else:
                icon, is_vid = get_file_info(n)
                size = readable_size(os.path.getsize(full))
                files.append({'name':n, 'path':path_rel, 'is_dir':False, 'size':size, 'icon':icon, 'is_video':is_vid})
        dirs.sort(key=lambda x: x['name'].lower()); files.sort(key=lambda x: x['name'].lower())
        items = dirs + files

    p = os.path.dirname(rel_path) if rel_path else None
    return render_template_string(HTML, items=items, path=rel_path, parent=p, msg=msg, type=mtype, user=AUTH_USER)

@app.route("/download/<path:filename>")
@requires_auth
def download(filename):
    full = safe_join(ROOT_DIR, filename)
    return send_from_directory(os.path.dirname(full), os.path.basename(full), as_attachment=True)

@app.route("/view/<path:filename>")
@requires_auth
def view(filename):
    full = safe_join(ROOT_DIR, filename)
    return send_from_directory(os.path.dirname(full), os.path.basename(full), as_attachment=False)

@app.route("/zip/<path:dirname>")
@requires_auth
def download_zip(dirname):
    full = safe_join(ROOT_DIR, dirname)
    name = os.path.basename(full) + ".zip"
    try:
        tmp = tempfile.mkdtemp()
        path = shutil.make_archive(os.path.join(tmp, name), 'zip', full)
        return send_file(path, as_attachment=True, download_name=name)
    except: return "Error", 500

# --- MAIN BLOCK AVEC TON DESIGN DEMANDÉ ---
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    print(f"{GREEN}┌──────────────────────────────────────────┐{RESET}")
    print(f"{GREEN}│           KALI SHARE SERVER V7           │{RESET}")
    print(f"{GREEN}└──────────────────────────────────────────┘{RESET}\n")
    
    print(f" {BOLD}[?] Configuration de la session :{RESET}")

    try:
        # Demande Nom (admin par défaut)
        u_input = input(f" 👤 Nom d'utilisateur [admin] : ").strip()
        AUTH_USER = u_input if u_input else "admin"

        # Demande MDP (VISIBLE, utilisation de input et non getpass)
        p_input = input(f" 🔑 Mot de passe [1234]      : ").strip()
        AUTH_PASS = p_input if p_input else "1234"
    except KeyboardInterrupt:
        print("\n\n❌ Annulé.")
        exit()

    local_ip = get_ip()
    port = 8000

    print("\n" + "-"*44)
    print(f" {GREEN}🚀 SERVEUR EN LIGNE !{RESET}")
    print(f" {BOLD}📱 Sur ton téléphone/PC, ouvre :{RESET}")
    print(f"    {CYAN}http://{local_ip}:{port}{RESET}")
    print("-" * 44)
    print(f" 📂 Dossier partagé : {ROOT_DIR}")
    # J'affiche ici le mot de passe EN CLAIR dans le résumé comme tu l'as configuré
    print(f" 👤 Login           : {AUTH_USER} / {AUTH_PASS}")
    print(f" 🛑 STOP            : CTRL + C")
    print("-" * 44 + "\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
