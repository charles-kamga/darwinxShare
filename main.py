import threading
import sys
import os
import socket
import customtkinter as ctk
import qrcode
from PIL import Image
from werkzeug.serving import make_server
from tkinter import filedialog, messagebox
from core.server import app, SERVER_CONFIG, get_ip, get_all_ips, get_wifi_ip, get_hotspot_ip, resource_path, LOG_FILE
import logging

# Silence Flask logs dans le terminal PC
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class ServerThread(threading.Thread):
    def __init__(self, host, port, app_ref):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.server = None
        self.daemon = True
        self.app_ref = app_ref

    def run(self):
        try:
            self.server = make_server(self.host, self.port, app, threaded=True)
            self.server.serve_forever()
        except Exception as e:
            if self.app_ref:
                self.app_ref.after(0, lambda: self.app_ref.handle_server_crash(str(e)))
        finally:
            if self.server:
                try: self.server.server_close()
                except: pass

    def shutdown(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except: pass


class DarwinxApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DarwinxShare — Admin Console")
        self.geometry("600x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.server_thread = None
        self.server_active = False
        self.password_visible = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        try:
            logo_path = resource_path("static/logo.png")
            if os.path.exists(logo_path):
                pil_img = Image.open(logo_path).resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(50, 50))
                ctk.CTkLabel(self.header_frame, text="", image=self.logo_icon).pack(side="left", padx=(0, 15))
        except: pass

        ctk.CTkLabel(self.header_frame, text="DarwinxShare", font=("Roboto", 32, "bold"), text_color="#3B8ED0").pack(side="left")
        ctk.CTkLabel(self.header_frame, text="v1.8.2 Pro", text_color="gray", font=("Arial", 12)).pack(side="left", padx=10, pady=(15, 0))

        # --- INFO BUTTON ---
        self.btn_info = ctk.CTkButton(self.header_frame, text="ⓘ", width=35, height=35, 
                                      fg_color="transparent", text_color="gray", 
                                      font=("Arial", 22), hover_color="#2C2C2E",
                                      command=self.show_instructions)
        self.btn_info.pack(side="right", pady=(10, 0))

        # --- TABS ---
        self.tabview = ctk.CTkTabview(self, width=540)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))

        self.tab_home = self.tabview.add("DASHBOARD")
        self.tab_config = self.tabview.add("CONFIG")
        self.tab_logs = self.tabview.add("📜 LOGS")

        # === DASHBOARD ===
        self.btn_frame = ctk.CTkFrame(self.tab_home, fg_color="transparent")
        self.btn_frame.pack(pady=20, padx=20, fill="x")
        
        self.btn_wifi = ctk.CTkButton(self.btn_frame, text="PARTAGE WIFI",
                                       fg_color="#27AE60", hover_color="#1E8449",
                                       height=60, font=("Arial", 16, "bold"),
                                       command=lambda: self.toggle_server("wifi"))
        self.btn_wifi.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.btn_hotspot = ctk.CTkButton(self.btn_frame, text="POINT D'ACCÈS",
                                       fg_color="#2980B9", hover_color="#2471A3",
                                       height=60, font=("Arial", 16, "bold"),
                                       command=lambda: self.toggle_server("hotspot"))
        self.btn_hotspot.pack(side="left", fill="x", expand=True)

        self.info_frame = ctk.CTkFrame(self.tab_home)
        self.info_frame.pack(padx=20, pady=5, fill="x")
        self.lbl_status = ctk.CTkLabel(self.info_frame, text="SERVICE: INACTIF 🔴",
                                       text_color="#E74C3C", font=("Courier", 14, "bold"))
        self.lbl_status.pack(pady=5)
        self.lbl_link = ctk.CTkLabel(self.info_frame, text="En attente...", font=("Courier", 16))
        self.lbl_link.pack(pady=(0, 5))

        self.qr_frame = ctk.CTkFrame(self.tab_home, fg_color="transparent")
        self.qr_frame.pack(pady=(40, 20), expand=True)
        self.lbl_qr = ctk.CTkLabel(self.qr_frame, text="")

        # === CONFIG ===
        ctk.CTkLabel(self.tab_config, text="Dossier Source", font=("Arial", 14, "bold")).pack(pady=(30, 5))
        self.btn_folder = ctk.CTkButton(self.tab_config, text=f"📂 {os.path.basename(SERVER_CONFIG['ROOT_DIR'])}",
                                        fg_color="#475569", height=40, command=self.pick_folder)
        self.btn_folder.pack(pady=5, padx=50, fill="x")
        self.lbl_full_path = ctk.CTkLabel(self.tab_config, text=SERVER_CONFIG["ROOT_DIR"],
                                          font=("Arial", 11), text_color="gray")
        self.lbl_full_path.pack()

        ctk.CTkLabel(self.tab_config, text="Identifiants d'accès", font=("Arial", 14, "bold")).pack(pady=(30, 5))
        self.entry_user = ctk.CTkEntry(self.tab_config, placeholder_text="Utilisateur", height=40)
        self.entry_user.insert(0, SERVER_CONFIG["AUTH_USER"])
        self.entry_user.pack(pady=5, padx=50, fill="x")

        self.pass_frame = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        self.pass_frame.pack(pady=5, padx=50, fill="x")
        self.entry_pass = ctk.CTkEntry(self.pass_frame, placeholder_text="Mot de passe", show="*", height=40)
        self.entry_pass.insert(0, SERVER_CONFIG["AUTH_PASS"])
        self.entry_pass.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(self.pass_frame, text="Voir", width=40, height=40, command=self.toggle_pass).pack(side="right", padx=(5, 0))

        # --- THEME SELECTOR ---
        ctk.CTkLabel(self.tab_config, text="Thème de l'interface", font=("Arial", 14, "bold")).pack(pady=(30, 5))

        self.themes_map = {
            "📱 iOS (Sombre)": "index_ios_dark.html",
            "📱 iOS (Clair)": "index_ios_files.html",
            "📱 iOS 18 Bento": "index_ios_bento.html",
            "📱 macOS Finder": "index_macos.html",
            "📱 Cyberpunk": "index_cyberpunk.html",
            "📱 Classique": "index_classic.html",
        }

        self.theme_var = ctk.StringVar(value="📱 iOS (Sombre)")
        SERVER_CONFIG["THEME"] = self.themes_map[self.theme_var.get()]

        self.theme_grid_frame = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        self.theme_grid_frame.pack(pady=5, padx=20, fill="x")
        self.theme_grid_frame.grid_columnconfigure(0, weight=1)
        self.theme_grid_frame.grid_columnconfigure(1, weight=1)

        self.theme_buttons = []
        r, c = 0, 0
        for theme_title in self.themes_map.keys():
            btn_color = "#3B8ED0" if theme_title == self.theme_var.get() else "#475569"
            btn = ctk.CTkButton(self.theme_grid_frame, text=theme_title, fg_color=btn_color,
                                height=35, command=lambda t=theme_title: self.change_theme(t))
            btn.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            self.theme_buttons.append((theme_title, btn))
            c += 1
            if c > 1:
                c = 0; r += 1

        # === LOGS TAB ===
        self.build_logs_tab()

    def change_theme(self, choice):
        self.theme_var.set(choice)
        SERVER_CONFIG["THEME"] = self.themes_map[choice]
        for t_title, t_btn in self.theme_buttons:
            t_btn.configure(fg_color="#3B8ED0" if t_title == choice else "#475569")

    def build_logs_tab(self):
        self.tab_logs.grid_rowconfigure(1, weight=1)
        self.tab_logs.grid_columnconfigure(0, weight=1)

        btn_frame = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        ctk.CTkButton(btn_frame, text="🔄 Rafraîchir", width=120, command=self.refresh_logs).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="🗑️ Vider", width=90, fg_color="#E74C3C",
                      hover_color="#C0392B", command=self.clear_logs).pack(side="left")
        ctk.CTkLabel(btn_frame, text="~/darwinx_access.log", font=("Courier", 11), text_color="gray").pack(side="right")

        self.log_text = ctk.CTkTextbox(self.tab_logs, font=("Courier", 11), state="disabled")
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.refresh_logs()

    def refresh_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log_text.insert("end", content if content.strip() else "--- Aucun accès enregistré ---\n")
                self.log_text.see("end")
            else:
                self.log_text.insert("end", f"--- Démarrez le serveur pour commencer la journalisation ---\n")
        except Exception as e:
            self.log_text.insert("end", f"[ERREUR] {e}\n")
        self.log_text.configure(state="disabled")

    def clear_logs(self):
        if messagebox.askyesno("Confirmer", "Effacer tout l'historique d'accès ?"):
            try:
                open(LOG_FILE, 'w').close()
                self.refresh_logs()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def pick_folder(self):
        d = filedialog.askdirectory(initialdir=SERVER_CONFIG["ROOT_DIR"])
        if d:
            SERVER_CONFIG["ROOT_DIR"] = d
            self.lbl_full_path.configure(text=d)
            self.btn_folder.configure(text=f"📂 {os.path.basename(d)}")

    def toggle_pass(self):
        self.password_visible = not self.password_visible
        self.entry_pass.configure(show="" if self.password_visible else "*")

    def generate_qr_with_logo(self, url):
        try:
            qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

            logo_path = resource_path("static/logo.png")
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                qr_width, qr_height = img_qr.size
                logo_size = int(qr_width * 0.25)
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                bg_size = int(logo_size * 1.2)
                white_bg = Image.new('RGBA', (bg_size, bg_size), 'white')
                logo_x = (bg_size - logo_size) // 2
                white_bg.paste(logo, (logo_x, logo_x), mask=logo)
                pos = ((qr_width - bg_size) // 2, (qr_height - bg_size) // 2)
                img_qr.paste(white_bg, pos, mask=white_bg)

            display_img = ctk.CTkImage(light_image=img_qr, dark_image=img_qr, size=(280, 280))
            self.lbl_qr.configure(image=display_img)
            self.lbl_qr.pack(pady=10)
        except Exception as e:
            print(f"[QR] {e}")

    def handle_server_crash(self, error_msg):
        if self.server_active:
            self.server_active = False
            self.server_thread = None
            self.lbl_status.configure(text="SERVICE: ERREUR 🔴", text_color="#E74C3C")
            self.lbl_link.configure(text="Erreur ou port bloqué")
            self.btn_start.configure(text="ACTIVER LE PARTAGE", fg_color="#27AE60", hover_color="#1E8449")
            self.lbl_qr.pack_forget()
            self._unlock_ui()
            messagebox.showerror("Crash Serveur",
                                 f"Le serveur a rencontré une erreur.\nSi le port 8000 est bloqué, vérifiez UFW.\n\nErreur: {error_msg}")

    def _lock_ui(self):
        self.entry_user.configure(state="disabled")
        self.entry_pass.configure(state="disabled")
        self.btn_folder.configure(state="disabled")
        for _, b in self.theme_buttons: b.configure(state="disabled")

    def _unlock_ui(self):
        self.entry_user.configure(state="normal")
        self.entry_pass.configure(state="normal")
        self.btn_folder.configure(state="normal")
        for _, b in self.theme_buttons: b.configure(state="normal")

    def show_instructions(self):
        msg = (
            "📖 GUIDE D'UTILISATION (v1.8.2) :\n\n"
            "1. Onglet CONFIG : Choisissez votre dossier racine et vos identifiants.\n"
            "2. Mode WIFI : Utilisez-le si PC et iPhone sont sur la même BOX.\n"
            "3. Mode POINT D'ACCÈS : Utilisez-le si vous activez le Hotspot du PC.\n"
            "4. SCAN : Scannez le QR Code qui apparaîtra.\n\n"
            "⚠️ ATTENTION : Pour le mode Point d'accès, veillez à l'activer dans vos paramètres système AVANT de cliquer.\n\n"
            "Par Charles Kamga pour la communauté linux !"
            
        )
        messagebox.showinfo("Instructions DarwinxShare", msg)

    def toggle_server(self, mode=None):
        if not self.server_active:
            SERVER_CONFIG["AUTH_USER"] = self.entry_user.get()
            SERVER_CONFIG["AUTH_PASS"] = self.entry_pass.get()
            
            # Sélection de l'IP selon le mode
            all_ips = get_all_ips()
            if mode == "wifi":
                wifi_ips = [ip for ip in all_ips if ip.startswith("192.168.")]
                if not wifi_ips:
                    messagebox.showwarning("WiFi non détecté", "Aucune interface WiFi (192.168.x.x) n'est active.\nVoulez-vous quand même tenter le démarrage ?")
                ip = get_wifi_ip()
            elif mode == "hotspot":
                hotspot_ips = [ip for ip in all_ips if ip.startswith("10.")]
                if not hotspot_ips:
                    messagebox.showerror("Hotspot Inactif", 
                                       "Le Point d'Accès n'est pas détecté (IP en 10.x.x.x).\n\n"
                                       "Veuillez activer le point d'accès de votre PC pour utiliser cette option.")
                    return
                ip = get_hotspot_ip()
            else:
                ip = get_ip()
                
            port = 8000
            try:
                # Vérification UFW
                import subprocess
                try:
                    ufw_check = subprocess.run(['ufw', 'status'], capture_output=True, text=True, timeout=1)
                    if "active" in ufw_check.stdout.lower():
                        logging.warning("UFW est ACTIF.")
                except: pass

                self.server_thread = ServerThread('0.0.0.0', port, self)
                self.server_thread.start()
                self.server_active = True
                
                all_ips = get_all_ips()
                logging.info(f"SERVEUR DEMARRÉ | Mode: {mode} | IP: {ip}")
                
                url = f"http://{ip}:{port}"
                self.lbl_status.configure(text="SERVICE: ACTIF 🟢", text_color="#2ECC71")
                self.lbl_link.configure(text=url)
                
                # Mise à jour des boutons
                self.btn_wifi.configure(text="ARRÊTER (WIFI)", fg_color="#C0392B", hover_color="#922B21", state="normal")
                self.btn_hotspot.configure(text="ARRÊTER (HOST)", fg_color="#C0392B", hover_color="#922B21", state="normal")
                
                # Désactiver l'autre bouton ? Non, on change les deux en "ARRÊTER"
                # Mais pour être clair, on va désactiver celui qui n'a pas été cliqué
                if mode == "wifi":
                    self.btn_hotspot.configure(state="disabled")
                else:
                    self.btn_wifi.configure(state="disabled")

                self.generate_qr_with_logo(url)
                self._lock_ui()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        else:
            threading.Thread(target=self.server_thread.shutdown, daemon=True).start()
            self.server_active = False
            self.server_thread = None
            self.lbl_status.configure(text="SERVICE: INACTIF 🔴", text_color="#E74C3C")
            self.lbl_link.configure(text="En attente...")
            
            # Reset des boutons
            self.btn_wifi.configure(text="PARTAGE WIFI", fg_color="#27AE60", hover_color="#1E8449", state="normal")
            self.btn_hotspot.configure(text="POINT D'ACCÈS", fg_color="#2980B9", hover_color="#2471A3", state="normal")
            
            self.lbl_qr.pack_forget()
            self._unlock_ui()

    def on_closing(self):
        if self.server_active and self.server_thread:
            self.server_thread.shutdown()
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    # Verrou d'instance unique (port 9999)
    try:
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('127.0.0.1', 9999))
    except socket.error:
        print("[ERREUR] Une instance de DarwinxShare est déjà en cours d'exécution.")
        sys.exit(1)

    app_ui = DarwinxApp()
    app_ui.mainloop()
