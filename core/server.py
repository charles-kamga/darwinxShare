import os
import socket
import tempfile
import shutil
import hmac
import sys
import re
import mimetypes
import time
import logging
import gzip
import io
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, request, send_from_directory, render_template, Response, send_file, abort, after_this_request
from werkzeug.exceptions import RequestEntityTooLarge


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Dossiers explicites pour PyInstaller/AppImage
template_dir = resource_path("templates")
static_dir = resource_path("static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # cache 1h pour assets statiques

# --- COMPRESSION GZIP AUTOMATIQUE ---
@app.after_request
def compress_response(response):
    """Compresse les réponses textuelles en Gzip si le client le supporte."""
    if (response.status_code == 200
            and 'gzip' in request.headers.get('Accept-Encoding', '')
            and response.content_type.startswith(('text/', 'application/json'))
            and not response.direct_passthrough):
        data = response.get_data()
        if len(data) > 500:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6) as f:
                f.write(data)
            response.set_data(buf.getvalue())
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.get_data())
            response.headers.pop('Content-MD5', None)
    return response


# --- CACHE DU LISTING EN MÉMOIRE (TTL = 5 secondes) ---
_dir_cache = {}
_DIR_CACHE_TTL = 5.0

SERVER_CONFIG = {
    "ROOT_DIR": os.path.expanduser("~/Downloads"),
    "AUTH_USER": "admin",
    "AUTH_PASS": "1234",
    "THEME": "index_ios_dark.html"
}

# --- GESTIONNAIRES D'ERREURS ---
@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return render_template(SERVER_CONFIG["THEME"],
                           items=[], path="",
                           msg="❌ Erreur : Le fichier est trop volumineux !",
                           type="err", user=SERVER_CONFIG["AUTH_USER"]), 413

@app.errorhandler(404)
def page_not_found(e):
    return render_template(SERVER_CONFIG["THEME"], items=[], path="",
                           msg="❌ Fichier introuvable.", type="err",
                           user=SERVER_CONFIG["AUTH_USER"]), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template(SERVER_CONFIG["THEME"], items=[], path="",
                           msg="❌ Erreur interne du serveur.", type="err",
                           user=SERVER_CONFIG["AUTH_USER"]), 500


# --- LOGS D'ACCÈS ---
LOG_FILE = os.path.join(os.path.expanduser("~"), "darwinx_access.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- SÉCURITÉ : BLOCAGE IP ASSOUPLI (Safari peut faire bcp de requêtes) ---
FAILED_LOGINS = {}
BAN_DURATION = 1 * 60   # 1 minute (plus souple)
MAX_FAILS = 10         # 10 tentatives (Safari tape fort à la première connexion)


# --- AUTHENTIFICATION ---
def check_auth(username, password):
    ip = request.remote_addr or "0.0.0.0"
    now = time.time()

    if ip in FAILED_LOGINS:
        entry = FAILED_LOGINS[ip]
        if entry["count"] >= MAX_FAILS:
            elapsed = now - entry["last_fail"]
            if elapsed < BAN_DURATION:
                remaining = int((BAN_DURATION - elapsed) / 60) + 1
                logging.warning(f"IP BANNIE: {ip} | Tentative bloquée | Reste {remaining} min")
                return False
            else:
                del FAILED_LOGINS[ip]

    user_ok = hmac.compare_digest(username, SERVER_CONFIG["AUTH_USER"])
    pass_ok = hmac.compare_digest(password, SERVER_CONFIG["AUTH_PASS"])

    if user_ok and pass_ok:
        if ip in FAILED_LOGINS:
            del FAILED_LOGINS[ip]
        return True
    else:
        if ip not in FAILED_LOGINS:
            FAILED_LOGINS[ip] = {"count": 0, "last_fail": now}
        FAILED_LOGINS[ip]["count"] += 1
        FAILED_LOGINS[ip]["last_fail"] = now
        count = FAILED_LOGINS[ip]["count"]
        logging.warning(f"ECHEC_AUTH: {ip} | Tentative {count}/{MAX_FAILS} | User: '{username}'")
        return False


def authenticate():
    return Response('Connexion requise pour DarwinxShare', 401,
                    {'WWW-Authenticate': 'Basic realm="Login"',
                     'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        ip = request.remote_addr or "0.0.0.0"
        logging.info(f"ACCES: {ip} | {request.method} {request.path} | User: '{auth.username}'")
        
        resp = f(*args, **kwargs)
        # On force la réponse à ne pas être cachée pour éviter les bugs Safari
        if isinstance(resp, Response):
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
        return resp
    return decorated


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def safe_join(base, rel_path):
    if not rel_path:
        return base
    rel_path = os.path.normpath(rel_path).strip(os.sep)
    full = os.path.abspath(os.path.join(base, rel_path))
    if not full.startswith(base):
        abort(403)
    return full


def get_file_info(filename):
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    icon = '📄'
    is_video = False
    if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'heic']:
        icon = '🖼️'
    elif ext in ['mp4', 'mov', 'mkv', 'avi', 'webm']:
        icon = '🎬'
        is_video = True
    elif ext in ['mp3', 'wav', 'flac', 'm4a']:
        icon = '🎵'
    elif ext in ['zip', 'rar', '7z', 'tar', 'gz']:
        icon = '📦'
    elif ext in ['pdf']:
        icon = '📕'
    elif ext in ['py', 'c', 'cpp', 'html', 'js', 'css', 'json']:
        icon = '🧑‍💻'
    return icon, is_video


def readable_size(size):
    for unit in ['o', 'Ko', 'Mo', 'Go']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} To"


@app.route("/", methods=["GET", "POST"])
@requires_auth
def index():
    rel_path = request.args.get("path", "")
    curr_dir = safe_join(SERVER_CONFIG["ROOT_DIR"], rel_path)
    msg, mtype = None, ""

    if request.method == "POST":
        post_path = request.form.get("path", "")
        up_dir = safe_join(SERVER_CONFIG["ROOT_DIR"], post_path)
        files = request.files.getlist("file")
        try:
            c = 0
            for f in files:
                if f.filename:
                    fn = secure_filename(f.filename) or "temp"
                    f.save(os.path.join(up_dir, fn))
                    c += 1
            if c:
                msg = f"✅ {c} fichier(s) transféré(s) !"
                mtype = "ok"
                rel_path = post_path
                curr_dir = up_dir
                # Invalider le cache du dossier
                _dir_cache.pop(curr_dir, None)
            else:
                msg = "⚠️ Aucun fichier sélectionné."
                mtype = "err"
        except Exception as e:
            msg = f"❌ Erreur Upload: {str(e)}"
            mtype = "err"

    items = []
    if os.path.exists(curr_dir):
        now = time.time()
        cache_key = curr_dir
        use_cache = (request.method == "GET" and not msg)

        if use_cache and cache_key in _dir_cache:
            ts, cached_items = _dir_cache[cache_key]
            if now - ts < _DIR_CACHE_TTL:
                items = cached_items
                use_cache = False
            else:
                use_cache = True
        else:
            use_cache = True

        if use_cache:
            try:
                raw = os.listdir(curr_dir)
                dirs, files_list = [], []
                for n in raw:
                    if n.startswith('.'):
                        continue
                    full = os.path.join(curr_dir, n)
                    path_rel = os.path.join(rel_path, n)
                    if os.path.isdir(full):
                        try:
                            count = len(os.listdir(full))
                        except:
                            count = "?"
                        dirs.append({'name': n, 'path': path_rel, 'is_dir': True, 'count': count})
                    else:
                        icon, is_vid = get_file_info(n)
                        size = readable_size(os.path.getsize(full))
                        files_list.append({'name': n, 'path': path_rel, 'is_dir': False,
                                           'size': size, 'icon': icon, 'is_video': is_vid})

                dirs.sort(key=lambda x: x['name'].lower())
                files_list.sort(key=lambda x: x['name'].lower())
                items = dirs + files_list
                _dir_cache[cache_key] = (now, items)
            except Exception:
                pass

    p = os.path.dirname(rel_path) if rel_path else None
    return render_template(SERVER_CONFIG["THEME"], items=items, path=rel_path,
                           parent=p, msg=msg, type=mtype, user=SERVER_CONFIG["AUTH_USER"])


@app.route("/zip/<path:dirname>")
@requires_auth
def download_zip(dirname):
    full = safe_join(SERVER_CONFIG["ROOT_DIR"], dirname)
    name = os.path.basename(full) + ".zip"
    try:
        tmp = tempfile.mkdtemp()
        path = shutil.make_archive(os.path.join(tmp, name), 'zip', full)

        @after_this_request
        def remove_file(response):
            try:
                os.remove(path)
                shutil.rmtree(tmp)
            except:
                pass
            return response

        return send_file(path, as_attachment=True, download_name=name)
    except:
        return abort(500)


@app.route("/download/<path:filename>")
@requires_auth
def download(filename):
    full = safe_join(SERVER_CONFIG["ROOT_DIR"], filename)
    if not os.path.exists(full):
        return abort(404)
    basename = os.path.basename(full)
    directory = os.path.dirname(full)
    response = send_from_directory(directory, basename, as_attachment=True)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename="{basename}"'
    return response


def get_chunk(full_path, byte1=None, byte2=None):
    file_size = os.path.getsize(full_path)
    yield_size = 4 * 1024 * 1024  # 4MB chunks pour streaming WiFi fluide

    if byte1 is None:
        byte1 = 0
    if byte2 is None:
        byte2 = file_size - 1

    length = byte2 - byte1 + 1

    with open(full_path, 'rb') as f:
        f.seek(byte1)
        while length > 0:
            chunk = min(length, yield_size)
            data = f.read(chunk)
            if not data:
                break
            length -= len(data)
            yield data


@app.route("/view/<path:filename>")
@requires_auth
def view(filename):
    full = safe_join(SERVER_CONFIG["ROOT_DIR"], filename)
    if not os.path.exists(full):
        return abort(404)

    file_size = os.path.getsize(full)
    range_header = request.headers.get('Range', None)

    mime_type, _ = mimetypes.guess_type(full)
    if not mime_type:
        mime_type = 'application/octet-stream'

    if not range_header:
        resp = Response(get_chunk(full), 200, mimetype=mime_type, direct_passthrough=True)
        resp.headers.add('Content-Length', str(file_size))
        resp.headers.add('Accept-Ranges', 'bytes')
        return resp

    m = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if m:
        g = m.groups()
        byte1 = int(g[0]) if g[0] else 0
        byte2 = int(g[1]) if g[1] else file_size - 1
    else:
        byte1, byte2 = 0, file_size - 1

    if byte2 >= file_size:
        byte2 = file_size - 1

    length = byte2 - byte1 + 1

    resp = Response(get_chunk(full, byte1, byte2), 206, mimetype=mime_type, direct_passthrough=True)
    resp.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{file_size}')
    resp.headers.add('Content-Length', str(length))
    resp.headers.add('Accept-Ranges', 'bytes')
    return resp
