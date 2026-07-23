import tkinter as tk
from tkinter import messagebox
import threading
import time
from datetime import datetime
import os
import json
import re
import logging
import platform as _platform
import subprocess
import sys as _sys
import urllib.request
import concurrent.futures
from audio import Audio
from PIL import Image, ImageTk
from ai_module import GPT4AllAI
from tts_module import TTS
from face_animation import AnimatedFace
from sounds import Sounds
from progress_tracker import ProgressTracker
from hash_utils import sha256_file, verify_file
from themes import COLORES
import glob
import lang

try:
    import ttkbootstrap as tb
    _HAS_TTB = True
except ImportError:
    import tkinter.ttk as ttk
    _HAS_TTB = False

if _HAS_TTB:
    ttk = tb
    THEME_NAME = "darkly"
else:
    from tkinter import ttk

# === LOGGING ===
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iron_chat.log")
try:
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
except Exception:
    print("⚠ No se pudo crear iron_chat.log, se usará salida estándar")
logging.info("🚀 IRON CHAT iniciado")

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title(lang.tr("window_title"))
        self.root.geometry("850x650")
        self.root.minsize(850, 650)
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        self.tts_enabled = True
        self.lang = "es"
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.historial_file = os.path.join(self.project_dir, "historial.json")
        self.music_playing = False
        self.mensajes_count = 0
        self.animacion_dots = 0
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_job = None
        self._sending = False
        self._sending_timeout = None
        self._stream_start_index = "1.0"
        self.FONT_MONO = ("Consolas", 12) if _platform.system() == "Windows" else ("monospace", 12)
        self.FONT_MONO_SM = ("Consolas", 10) if _platform.system() == "Windows" else ("monospace", 10)
        self.FONT_MONO_LG = ("Consolas", 14) if _platform.system() == "Windows" else ("monospace", 14)
        try:
            self.progress = ProgressTracker(os.path.join(self.project_dir, "progreso.db"))
        except Exception:
            logging.warning("No se pudo inicializar ProgressTracker, progreso deshabilitado")
            self.progress = None
        self.init_ui()
        self.ai = None
        self.ai_loaded = False
        threading.Thread(target=self._verificar_integridad, daemon=True).start()
        threading.Thread(target=self.load_ai, daemon=True).start()
        self.root.bind("<Control-l>", lambda e: self.clear_chat())
        self.root.bind("<Control-d>", lambda e: self.export_chat())
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())
        self.actualizar_reloj()

    def _verificar_integridad(self):
        try:
            from hash_utils import verify_project_integrity
            icon, msg = verify_project_integrity(self.project_dir)
            logging.info(f"Integridad: {icon} {msg}")
            if icon == "❌":
                self.root.after(0, lambda: self.add_message("system", f"🚨 {msg}"))
                self.root.after(0, lambda: self.add_message("system", "🚨 ¡Ejecutá 'python3 generar_firma.py' para regenerar la firma!"))
            elif icon == "⚠️":
                self.root.after(0, lambda: self.add_message("system", f"⚠️ {msg}"))
        except Exception as e:
            logging.warning(f"No se pudo verificar integridad: {e}")

    def _find_image(self, *names):
        for name in names:
            path = os.path.join(self.project_dir, name)
            if os.path.exists(path):
                return path
        return None

    def cargar_historial(self):
        if os.path.exists(self.historial_file):
            try:
                with open(self.historial_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                logging.warning(f"Error cargando historial: {e}")
        return []

    def guardar_historial(self):
        try:
            with open(self.historial_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.warning(f"Error guardando historial: {e}")

    def actualizar_reloj(self):
        try:
            hora = datetime.now().strftime("%H:%M:%S")
            self.reloj_label.config(text=hora)
            self.root.after(1000, self.actualizar_reloj)
        except Exception:
            pass

    def actualizar_contador(self):
        self.contador_label.config(text=lang.tr_format("msg_count", count=self.mensajes_count))

    def aplicar_tema(self):
        c = self.colores[self.tema_actual]

        self.root.configure(bg=c["bg"])
        self.header.configure(bg=c["bg"])
        self.header_sep.configure(bg=c["naranja"])
        self.title_label.configure(bg=c["bg"], fg=c["acento"])
        self.subtitle.configure(bg=c["bg"], fg=c["naranja"])
        self.reloj_label.configure(bg=c["bg"], fg=c["fg"])
        self.main_container.configure(bg=c["bg"])
        self.chat_panel.configure(bg=c["bg"])
        self.canvas.configure(bg=c["bg"])
        self.overlay.configure(bg=c["chat_bg"])
        self.text_frame.configure(bg=c["chat_bg"])
        self.chat_area.configure(bg=c["chat_bg"], fg=c["fg"], insertbackground=c["fg"])

        if self.tema_actual == 0:
            self.chat_area.tag_config("user_msg", background="#1a3a5e")
            self.chat_area.tag_config("ai_msg", background="#1a3a2e")
            self.chat_area.tag_config("system_msg", background=c["chat_bg"])
        elif self.tema_actual == 1:
            self.chat_area.tag_config("user_msg", background="#D6EAF8")
            self.chat_area.tag_config("ai_msg", background="#D5F5E3")
            self.chat_area.tag_config("system_msg", background=c["chat_bg"])
        else:
            self.chat_area.tag_config("user_msg", background="#1a3a2e")
            self.chat_area.tag_config("ai_msg", background="#1a2e1a")
            self.chat_area.tag_config("system_msg", background=c["chat_bg"])

        self.scrollbar.configure(bg=c["scroll"], troughcolor=c["bg"])
        self.input_frame.configure(bg=c["chat_bg"])
        self.input_sep.configure(bg=c["scroll"])
        self.input_field.configure(bg=c["input_bg"], fg=c["fg"], insertbackground=c["fg"])
        if not _HAS_TTB:
            self.send_button.configure(bg=c["naranja"])
        self.status_bar.configure(bg=c["chat_bg"])
        self.status_label.configure(bg=c["chat_bg"])
        self.contador_label.configure(bg=c["chat_bg"], fg=c["acento"])
        self.right_panel.configure(bg=c["bg"])
        self.tools_frame.configure(bg=c["bg"])
        self.tools_sep.configure(bg=c["scroll"])
        self.tools_title.configure(bg=c["bg"], fg=c["acento"])
        self.menu_frame.configure(bg=c["bg"])
        if not _HAS_TTB:
            self.menubtn.configure(bg=c["btn_bg"])
        btn_bg = c["btn_bg"]
        self.timer_frame.configure(bg=c["bg"])
        self.timer_label.configure(bg=c["bg"], fg=c["acento"])
        if not _HAS_TTB:
            for btn in self.timer_buttons:
                btn.configure(bg=btn_bg)

        self.vol_frame.configure(bg=c["bg"])
        self.vol_label.configure(bg=c["bg"], fg=c["fg"])
        self.vol_slider.configure(bg=c["btn_bg"], fg=c["acento"], troughcolor=c["bg"])
        self.vol_num_label.configure(bg=c["bg"], fg=c["acento"])
        self.vol_label_music.configure(bg=c["bg"], fg=c["fg"])
        self.vol_music_slider.configure(bg=c["btn_bg"], fg=c["acento"], troughcolor=c["bg"])
        self.vol_music_num_label.configure(bg=c["bg"], fg=c["acento"])
        self.vol_label_speed.configure(bg=c["bg"], fg=c["fg"])
        self.vol_speed_slider.configure(bg=c["btn_bg"], fg=c["acento"], troughcolor=c["bg"])
        self.vol_speed_num_label.configure(bg=c["bg"], fg=c["acento"])
        self.credit_frame.configure(bg=c["bg"])
        self.credit_label.configure(bg=c["bg"], fg=c["naranja"])
        if hasattr(self, 'jmb_label') and self.jmb_label:
            self.jmb_label.configure(bg=c["bg"])

        try:
            self.face.canvas.configure(bg=c["face_bg"])
        except Exception:
            pass

    def init_ui(self):
        # === 1. HEADER ===
        self.header = tk.Frame(self.root, bg="#1a1a2e", height=60)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        # Separator line at bottom of header
        self.header_sep = tk.Frame(self.header, height=2, bg="#FF6B35")
        self.header_sep.place(relx=0, rely=1.0, relwidth=1)
        self.title_label = tk.Label(self.header, text=lang.tr("header_title"), font=("Helvetica", 20, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.title_label.pack(side=tk.LEFT, padx=(15, 5), pady=10)
        self.subtitle = tk.Label(self.header, text=lang.tr("header_subtitle"), font=("Helvetica", 8, "bold"), bg="#1a1a2e", fg="#FF6B35")
        self.subtitle.pack(side=tk.LEFT, padx=(0, 5), pady=15)
        self.reloj_label = tk.Label(self.header, text="", font=("Helvetica", 10, "bold"), bg="#1a1a2e", fg="#ECF0F1")
        self.reloj_label.pack(side=tk.RIGHT, padx=15, pady=10)

        # === 2. MAIN CONTAINER ===
        self.main_container = tk.Frame(self.root, bg="#1a1a2e")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # === 3. CHAT PANEL (IZQUIERDA) ===
        self.chat_panel = tk.Frame(self.main_container, bg="#1a1a2e")
        self.chat_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.canvas = tk.Canvas(self.chat_panel, highlightthickness=0, bd=0, bg="#1a1a2e")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Fondo de imagen (con fallback si no existe)
        bg_image_path = self._find_image("gymp.jpeg", "gym.jpg", "fondo.jpeg", "bg.jpeg", "background.jpeg")
        self.bg_photo = None
        self.canvas_has_bg = False
        if bg_image_path:
            try:
                bg_img = Image.open(bg_image_path)
                bg_img = bg_img.resize((450, 500), Image.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.bg_image = self.bg_photo
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor='nw', tags="bg")
                self.canvas_has_bg = True

                def resize_bg(event, img_path=bg_image_path):
                    try:
                        self.canvas.delete("bg")
                        if os.path.exists(img_path):
                            new_img = Image.open(img_path)
                            new_img = new_img.resize((event.width, event.height), Image.LANCZOS)
                            self.canvas.bg_image = ImageTk.PhotoImage(new_img)
                            self.canvas.create_image(0, 0, image=self.canvas.bg_image, anchor='nw', tags="bg")
                    except Exception:
                        pass

                self.canvas.bind("<Configure>", resize_bg)
            except Exception as e:
                logging.warning(f"Error al cargar fondo: {e}")
                self.canvas_has_bg = False

        # Overlay del chat
        self.overlay = tk.Frame(self.canvas, bg="#0d0d1a", bd=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.text_frame = tk.Frame(self.overlay, bg="#0d0d1a", bd=0)
        self.text_frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.78)

        # Área de texto del chat
        self.chat_area = tk.Text(self.text_frame, font=self.FONT_MONO, bg="#0d0d1a", fg="#ECF0F1", insertbackground="#ECF0F1", wrap=tk.WORD, relief=tk.FLAT, bd=0, padx=8, pady=8)
        self.chat_area.tag_config("user_msg", background="#1a3a5e", foreground="#FFFFFF", lmargin1=10, lmargin2=10, rmargin=10, spacing1=4, spacing3=4)
        self.chat_area.tag_config("ai_msg", background="#1a3a2e", foreground="#E8F5E9", lmargin1=10, lmargin2=10, rmargin=10, spacing1=4, spacing3=4)
        self.chat_area.tag_config("system_msg", background="#0d0d1a", foreground="#7F8C8D", spacing1=2, spacing3=2)
        self.chat_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.chat_area.yview, bg="#34495E", troughcolor="#1a1a2e")
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.chat_area.config(yscrollcommand=self.scrollbar.set)

        # Input
        self.input_frame = tk.Frame(self.overlay, bg="#0d0d1a", height=40)
        self.input_frame.place(relx=0.02, rely=0.83, relwidth=0.96)
        self.input_frame.pack_propagate(False)
        self.input_sep = tk.Frame(self.input_frame, height=1, bg="#2C3E50")
        self.input_sep.pack(side=tk.TOP, fill=tk.X)
        self.input_field = tk.Entry(self.input_frame, font=self.FONT_MONO, bg="#1a1a2e", fg="#ECF0F1", insertbackground="#ECF0F1", relief=tk.SUNKEN, bd=1)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", lambda e: self.send_message() or "break")
        self.input_field.bind("<Control-Return>", lambda e: self.send_message() or "break")
        self.input_field.bind("<Control-l>", lambda e: self.clear_chat() or "break")
        if _HAS_TTB:
            self.send_button = tb.Button(self.input_frame, text=lang.tr("btn_send"), style="warning.TButton", command=self.send_message)
        else:
            self.send_button = tk.Button(self.input_frame, text=lang.tr("btn_send"), font=("Helvetica", 10, "bold"), bg="#FF6B35", fg="white", command=self.send_message, relief=tk.FLAT, padx=12, pady=2, bd=0)
        self.send_button.pack(side=tk.RIGHT)

        # Status bar
        self.status_bar = tk.Frame(self.overlay, bg="#0d0d1a", height=26)
        self.status_bar.place(relx=0.02, rely=0.93, relwidth=0.96)
        self.status_label = tk.Label(self.status_bar, text=lang.tr("status_loading"), font=("Helvetica", 9, "bold"), bg="#0d0d1a", fg="#FFD700", anchor='w')
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.contador_label = tk.Label(self.status_bar, text=lang.tr_format("msg_count", count=0), font=("Helvetica", 8, "bold"), bg="#0d0d1a", fg="#FFD700")
        self.contador_label.pack(side=tk.RIGHT, padx=(5, 0))
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='indeterminate', length=80)
        self.progress_bar.pack(side=tk.RIGHT, padx=(0, 5))
        self.progress_bar.start()
        self.dl_dialog = None
        self.dl_progress_bar = None
        self.dl_pct_label = None

        # === 4. RIGHT PANEL (DERECHA) ===
        self.right_panel = tk.Frame(self.main_container, bg="#1a1a2e", width=350)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.right_panel.pack_propagate(False)

        # Cara animada
        self.face = AnimatedFace(self.right_panel, x=35, y=10, size=280, project_dir=self.project_dir)

        # Tools — menú compacto
        self.tools_frame = tk.Frame(self.right_panel, bg="#1a1a2e", height=145)
        self.tools_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10))
        self.tools_frame.pack_propagate(False)
        self.tools_sep = tk.Frame(self.tools_frame, height=1, bg="#2C3E50")
        self.tools_sep.pack(side=tk.TOP, fill=tk.X)
        self.tools_title = tk.Label(self.tools_frame, text="⚙️ MENÚ", font=("Helvetica", 11, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.tools_title.pack(pady=(5, 5))
        self.menu_frame = tk.Frame(self.tools_frame, bg="#1a1a2e")
        self.menu_frame.pack(expand=True)

        self.menu_bar = tk.Menu(self.menu_frame, tearoff=0)
        if _HAS_TTB:
            self.menubtn = tb.Button(self.menu_frame, text=lang.tr("btn_menu"), style="secondary.TButton", command=self._abrir_menu)
        else:
            self.menubtn = tk.Button(self.menu_frame, text=lang.tr("btn_menu"), font=("Helvetica", 11, "bold"), bg="#2C3E50", fg="white", relief=tk.RAISED, bd=2, padx=20, pady=6, cursor="hand2", command=self._abrir_menu)
        self.menubtn.pack()
        self._build_menu()

        # === 5. COLORES ===
        self.tema_actual = 0
        self.colores = COLORES

        # === 6. VOLUMEN ===
        self.vol_frame = tk.Frame(self.tools_frame, bg="#1a1a2e")
        self.vol_frame.pack(fill=tk.X, pady=(5, 0), padx=10)
        self.vol_label = tk.Label(self.vol_frame, text="🔊", font=("Helvetica", 8, "bold"), bg="#1a1a2e", fg="#ECF0F1")
        self.vol_label.pack(side=tk.LEFT, padx=(0, 2))
        self.vol_slider = tk.Scale(self.vol_frame, from_=0, to=100, orient=tk.HORIZONTAL, bg="#2C3E50", fg="#FFD700", troughcolor="#1a1a2e", highlightthickness=0, bd=0, length=70, font=("Helvetica", 8), showvalue=False, command=self.cambiar_volumen)
        self.vol_slider.set(70)
        self.vol_slider.pack(side=tk.LEFT)
        self.vol_num_label = tk.Label(self.vol_frame, text="70%", font=("Helvetica", 7, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.vol_num_label.pack(side=tk.LEFT, padx=(1, 3))
        self.vol_label_music = tk.Label(self.vol_frame, text="🎵", font=("Helvetica", 8, "bold"), bg="#1a1a2e", fg="#ECF0F1")
        self.vol_label_music.pack(side=tk.LEFT, padx=(3, 2))
        self.vol_music_slider = tk.Scale(self.vol_frame, from_=0, to=100, orient=tk.HORIZONTAL, bg="#2C3E50", fg="#FFD700", troughcolor="#1a1a2e", highlightthickness=0, bd=0, length=55, font=("Helvetica", 8), showvalue=False, command=self.cambiar_volumen_musica)
        self.vol_music_slider.set(50)
        self.vol_music_slider.pack(side=tk.LEFT)
        self.vol_music_num_label = tk.Label(self.vol_frame, text="50%", font=("Helvetica", 7, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.vol_music_num_label.pack(side=tk.LEFT, padx=(1, 3))
        self.vol_label_speed = tk.Label(self.vol_frame, text="⚡", font=("Helvetica", 8, "bold"), bg="#1a1a2e", fg="#ECF0F1")
        self.vol_label_speed.pack(side=tk.LEFT, padx=(3, 2))
        self.vol_speed_slider = tk.Scale(self.vol_frame, from_=50, to=200, orient=tk.HORIZONTAL, bg="#2C3E50", fg="#FFD700", troughcolor="#1a1a2e", highlightthickness=0, bd=0, length=55, font=("Helvetica", 8), showvalue=False, command=self.cambiar_velocidad_tts)
        self.vol_speed_slider.set(100)
        self.vol_speed_slider.pack(side=tk.LEFT)
        self.vol_speed_num_label = tk.Label(self.vol_frame, text="1.0x", font=("Helvetica", 7, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.vol_speed_num_label.pack(side=tk.LEFT, padx=(1, 0))

        # === 7. TEMPORIZADOR ===
        self.timer_frame = tk.Frame(self.tools_frame, bg="#1a1a2e")
        self.timer_frame.pack(fill=tk.X, pady=(5, 0), padx=10)
        self.timer_label = tk.Label(self.timer_frame, text="⏱️ 00:00", font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.timer_label.pack(side=tk.RIGHT, padx=5, pady=2)
        timer_btn_frame = tk.Frame(self.timer_frame, bg="#1a1a2e")
        timer_btn_frame.pack(side=tk.LEFT)
        self.timer_buttons = []
        for secs, label in [(30, "30s"), (60, "60s"), (90, "90s"), (120, "120s")]:
            if _HAS_TTB:
                btn = tb.Button(timer_btn_frame, text=label, style="secondary.TButton",
                               command=lambda s=secs: self.timer_start(s), width=4)
            else:
                btn = tk.Button(timer_btn_frame, text=label, font=("Helvetica", 8, "bold"), bg="#2C3E50", fg="white",
                               command=lambda s=secs: self.timer_start(s), relief=tk.FLAT, width=4, height=1, bd=0)
            btn.pack(side=tk.LEFT, padx=2)
            self.timer_buttons.append(btn)
        if _HAS_TTB:
            tb.Button(timer_btn_frame, text="⏱️", style="info.TButton",
                     command=self.timer_custom, width=3).pack(side=tk.LEFT, padx=2)
            tb.Button(timer_btn_frame, text="⏹", style="danger.TButton",
                     command=self.timer_stop, width=3).pack(side=tk.LEFT, padx=2)
        else:
            tk.Button(timer_btn_frame, text="⏱️", font=("Helvetica", 8, "bold"), bg="#8E44AD", fg="white",
                     command=self.timer_custom, relief=tk.FLAT, width=3, height=1, bd=0).pack(side=tk.LEFT, padx=2)
            tk.Button(timer_btn_frame, text="⏹", font=("Helvetica", 8, "bold"), bg="#E74C3C", fg="white",
                     command=self.timer_stop, relief=tk.FLAT, width=3, height=1, bd=0).pack(side=tk.LEFT, padx=2)

        # === 8. CREDITOS ===
        self.credit_frame = tk.Frame(self.right_panel, bg="#1a1a2e", height=30)
        self.credit_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.credit_frame.pack_propagate(False)
        jmb_path = self._find_image("icon-jmb.png", "robot-icon.png")
        self.jmb_photo = None
        self.jmb_label = None
        if jmb_path:
            try:
                jmb_img = Image.open(jmb_path)
                jmb_img = jmb_img.resize((20, 20), Image.LANCZOS)
                self.jmb_photo = ImageTk.PhotoImage(jmb_img)
                self.jmb_label = tk.Label(self.credit_frame, image=self.jmb_photo, bg="#1a1a2e")
                self.jmb_label.pack(side=tk.LEFT, padx=(5, 2))
            except Exception:
                pass
        self.credit_label = tk.Label(self.credit_frame, text="⚡ JMB ⚡", font=("Helvetica", 9, "bold"), bg="#1a1a2e", fg="#FF6B35")
        self.credit_label.pack(side=tk.LEFT)

        # === 9. APLICAR TEMA INICIAL ===
        self.aplicar_tema()

        # === 10. CARGAR HISTORIAL ===
        self.chat_history = self.cargar_historial()
        Sounds.play_startup()
        if self.chat_history:
            self.chat_area.config(state=tk.NORMAL)
            for msg in self.chat_history:
                self.chat_area.insert(tk.END, msg + "\n")
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.see(tk.END)
            self.add_message("system", lang.tr_format("sys_history_loaded", len(self.chat_history)))
        else:
            self.add_message("system", lang.tr("sys_welcome"))
            self.add_message("system", lang.tr("sys_wait_model"))

    # ===================================================================
    # MÉTODOS
    # ===================================================================

    def clear_chat(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_history = []
        self.guardar_historial()
        self.mensajes_count = 0
        self.actualizar_contador()
        self.add_message("system", lang.tr("sys_chat_cleared"))

    def toggle_tts(self):
        self.tts_enabled = not self.tts_enabled
        if self.tts_enabled:
            tts_mode = getattr(self.tts, 'mode', 'none') if hasattr(self, 'tts') and self.tts else 'none'
            if tts_mode in ("none", "offline"):
                self.tts_enabled = False
                self.menu_audio.entryconfig(0, label=lang.tr("menu_tts_off"))
                self.add_message("system", lang.tr("sys_tts_unavailable"))
                return
            self.menu_audio.entryconfig(0, label=lang.tr("menu_tts_on"))
            self.add_message("system", lang.tr("sys_tts_on"))
        else:
            if hasattr(self, 'tts'):
                self.tts.stop()
                self.face.set_speaking(False)
            self.menu_audio.entryconfig(0, label=lang.tr("menu_tts_off"))
            self.add_message("system", lang.tr("sys_tts_off"))

    def cambiar_volumen(self, val):
        vol = int(val) / 100.0
        self.vol_num_label.config(text=f"{int(val)}%")
        if hasattr(self, 'tts'):
            self.tts.set_volume(vol)

    def cambiar_volumen_musica(self, val):
        self.vol_music_num_label.config(text=f"{int(val)}%")
        Audio.set_music_volume(int(val) / 100.0)

    def cambiar_velocidad_tts(self, val):
        speed = int(val)
        display = f"{speed/100:.1f}x"
        self.vol_speed_num_label.config(text=display)
        if hasattr(self, 'tts'):
            self.tts.set_speed(speed)

    def _abrir_menu(self):
        x = self.menubtn.winfo_rootx()
        y = self.menubtn.winfo_rooty() + self.menubtn.winfo_height()
        try:
            self.menu_bar.tk_popup(x, y)
        finally:
            self.menu_bar.grab_release()

    def _build_menu(self):
        m = self.menu_bar
        mkw = dict(tearoff=0)

        sub = tk.Menu(m, **mkw)
        m.add_cascade(label=lang.tr("menu_chat"), menu=sub)
        sub.add_command(label=lang.tr("menu_clear"), command=self.clear_chat)
        sub.add_command(label=lang.tr("menu_export"), command=self.export_chat)

        self.menu_audio = tk.Menu(m, **mkw)
        m.add_cascade(label=lang.tr("menu_audio"), menu=self.menu_audio)
        self.menu_audio.add_command(label=lang.tr("menu_tts_on"), command=self.toggle_tts)
        self.menu_audio.add_command(label=lang.tr("menu_music_off"), command=self.toggle_music)
        self.menu_audio.add_command(label=lang.tr("menu_mp3_folder"), command=self.open_music_folder)

        sub = tk.Menu(m, **mkw)
        m.add_cascade(label=lang.tr("menu_training"), menu=sub)
        sub.add_command(label=lang.tr("menu_notes"), command=self.open_notes)
        sub.add_command(label=lang.tr("menu_routine"), command=self.show_routines)
        sub.add_command(label=lang.tr("menu_progress"), command=self.show_progress)

        self.menu_app = tk.Menu(m, **mkw)
        m.add_cascade(label=lang.tr("menu_app"), menu=self.menu_app)
        self.menu_app.add_command(label=lang.tr("menu_info"), command=self.show_info)
        self.menu_app.add_command(label=lang.tr("theme_dark"), command=self.toggle_theme)
        self.menu_app.add_command(label=lang.tr("menu_help"), command=self.show_help)
        self.menu_app.add_command(label=lang.tr("menu_credits"), command=self.show_credits)

        self.menu_sistema = tk.Menu(m, **mkw)
        m.add_cascade(label=lang.tr("menu_system"), menu=self.menu_sistema)
        self.menu_download_idx = 0
        self.menu_sistema.add_command(label=lang.tr("menu_download_model"), command=self.download_model)
        self.menu_sistema.add_command(label=lang.tr("menu_desktop"), command=self.crear_acceso_escritorio)
        self.menu_sistema.add_command(label=lang.tr("menu_lang"), command=self._toggle_lang)

    def toggle_theme(self):
        self.tema_actual = (self.tema_actual + 1) % len(self.colores)
        self.aplicar_tema()
        theme_names = [lang.tr("theme_dark"), lang.tr("theme_light"), lang.tr("theme_nature")]
        nombre = theme_names[self.tema_actual]
        self.menu_app.entryconfig(1, label=nombre)
        self.add_message("system", lang.tr_format("theme_activated", nombre=nombre))

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "es" else "es"
        lang.LANG = self.lang
        # Update window and header
        self.root.title(lang.tr("window_title"))
        self.title_label.config(text=lang.tr("header_title"))
        self.subtitle.config(text=lang.tr("header_subtitle"))
        # Rebuild menu with new language
        self.menu_bar.destroy()
        self.menu_bar = tk.Menu(self.root, tearoff=0)
        self._build_menu()
        # Update menu button
        if _HAS_TTB and hasattr(self, 'menubtn') and self.menubtn:
            self.menubtn.config(text=lang.tr("btn_menu"))
        elif hasattr(self, 'menubtn') and self.menubtn:
            self.menubtn.config(text=lang.tr("btn_menu"))
        # Update send button
        if _HAS_TTB and hasattr(self, 'send_button') and self.send_button:
            self.send_button.config(text=lang.tr("btn_send"))
        # Update status
        self.status_label.config(text=lang.tr("status_ready_short"))
        # Update msg count
        try:
            self.contador_label.config(text=lang.tr_format("msg_count", count=self.mensajes_count))
        except Exception:
            pass
        # Update theme name in menu
        theme_names = [lang.tr("theme_dark"), lang.tr("theme_light"), lang.tr("theme_nature")]
        self.menu_app.entryconfig(1, label=theme_names[self.tema_actual])
        self.add_message("system", f"🌐 {lang.tr('menu_lang')}")

    def animar_escribiendo(self):
        dots = [".  ", ".. ", "...", " ..", "  .", "   "]
        self.animacion_dots = (self.animacion_dots + 1) % len(dots)
        try:
            label = getattr(self, 'status_label', None)
            if label is None:
                return
            label.config(text=lang.tr("status_writing").replace("...", dots[self.animacion_dots]))
            if self.ai_loaded:
                self.root.after(300, self.animar_escribiendo)
        except Exception:
            pass

    def _abrir_ruta(self, ruta):
        if _platform.system() == "Windows":
            os.startfile(ruta)
        else:
            subprocess.Popen(['xdg-open', ruta])

    def open_music_folder(self):
        """Abre la carpeta de música en el gestor de archivos"""
        try:
            music_path = os.path.join(self.project_dir, "musica")
            if not os.path.exists(music_path):
                os.makedirs(music_path)
            self._abrir_ruta(music_path)
            self.add_message("system", f"📂 CARPETA DE MÚSICA ABIERTA")
            logging.info(f"Carpeta musica abierta: {music_path}")
        except Exception as e:
            self.add_message("system", f"❌ ERROR AL ABRIR CARPETA: {e}")
            logging.error(f"Error abriendo carpeta musica: {e}")

    def export_chat(self):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.join(os.path.expanduser("~"), "Escritorio")
            if not os.path.exists(desktop):
                desktop = self.project_dir
            filename = os.path.join(desktop, f"iron_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("💪 IRON CHAT - HISTORIAL\n")
                f.write("=" * 40 + "\n\n")
                for msg in self.chat_history:
                    f.write(msg + "\n")
            self.add_message("system", f"📤 EXPORTADO AL ESCRITORIO: {os.path.basename(filename)}")
            logging.info(f"Chat exportado: {filename}")
        except Exception as e:
            self.add_message("system", f"❌ ERROR AL EXPORTAR: {e}")
            logging.error(f"Error exportando: {e}")

    def _modelo_nombre(self):
        if hasattr(self, 'ai') and self.ai:
            if getattr(self.ai, 'is_offline', False):
                return "OFFLINE (reglas)"
            if hasattr(self.ai, 'model_name'):
                return self.ai.model_name
            tipo = getattr(self.ai, 'model_type', '')
            if tipo == "qwen":
                return "Qwen 2.5"
            elif tipo == "llama":
                return "Llama 3.2"
        return "—"

    def show_info(self):
        modelo = self._modelo_nombre()
        info = ("💪 IRON CHAT v2.2\n\n"
                f"🤖 MODELO: {modelo}\n"
                "🔊 TTS: espeak-ng (Linux) / pyttsx3 (Windows)\n"
                "🎨 DISEÑO: Gym Style\n"
                "🎨 ASCII ART: 26 dibujos!\n"
                "📝 NOTAS RAPIDAS\n"
                "🎵 MUSICA MOTIVACIONAL\n"
                "📂 CARPETA MP3\n"
                "🌙☀️🌿 3 TEMAS: Oscuro/Claro/Naturaleza\n"
                "⏱️ TEMPORIZADOR + RECORDATORIOS\n"
                "🥗 DIETAS: Volumen/Definición/Saludable\n"
                "📊 PROGRESO CON DELTAS\n\n"
                "⚡ JMbirner ⚡")
        messagebox.showinfo("💪 IRON CHAT", info)

    def show_help(self):
        ayuda = ("❓ COMANDOS RAPIDOS:\n\n"
                 "  /ayuda       - Muestra esta ayuda\n"
                 "  /limpiar     - Limpia el chat\n"
                 "  /tema        - Cambia de tema (3 disponibles)\n"
                 "  /exportar    - Exporta el historial\n"
                 "  /notas       - Abre el bloc de notas\n"
                 "  /musica      - Activa/desactiva musica\n"
                 "  /stats       - Muestra estadisticas\n"
                 "  /dieta       - Plan de dieta (volumen/definicion/saludable)\n"
                 "  /recordatorio <min> '<msg>' - Programa un aviso\n"
                 "  /ejercicio   - Guia rapida de ejercicios\n\n"
                 "⌨️ ATAJOS:\n"
                 "  Enter        - Enviar mensaje\n"
                 "  Ctrl+Enter   - Enviar mensaje\n"
                 "  Ctrl+L       - Limpiar chat\n"
                 "  Ctrl+D       - Exportar historial\n"
                 "  Ctrl+T       - Cambiar tema\n\n"
                 "🎨 DIBUJOS ASCII:\n"
                 "  Escribe 'dibuja una mancuerna' o similar\n"
                 "  🏋️ 26 dibujos disponibles!")
        messagebox.showinfo("❓ AYUDA IRON CHAT", ayuda)

    def open_notes(self):
        try:
            notes_file = os.path.join(self.project_dir, "notas_entreno.txt")
            if not os.path.exists(notes_file):
                with open(notes_file, 'w', encoding='utf-8') as f:
                    f.write("📝 NOTAS DE ENTRENAMIENTO\n")
                    f.write("=" * 30 + "\n\n")
            self._abrir_ruta(notes_file)
            self.add_message("system", "📝 NOTAS ABIERTAS")
        except Exception as e:
            self.add_message("system", f"❌ ERROR AL ABRIR NOTAS: {e}")

    def toggle_music(self):
        self.music_playing = not self.music_playing
        if self.music_playing:
            try:
                music_path = os.path.join(self.project_dir, "musica")
                if not os.path.exists(music_path):
                    os.makedirs(music_path)
                mp3s = glob.glob(os.path.join(music_path, "*.mp3")) + glob.glob(os.path.join(music_path, "*.wav"))
                if mp3s:
                    Audio.play_music(mp3s[0])
                    self.menu_audio.entryconfig(1, label=lang.tr("menu_music_on"))
                    self.add_message("system", lang.tr_format("sys_music_playing", basename=os.path.basename(mp3s[0])))
                else:
                    self.music_playing = False
                    self.add_message("system", lang.tr("sys_no_music"))
                    self.menu_audio.entryconfig(1, label=lang.tr("menu_music_off"))
            except Exception as e:
                self.music_playing = False
                self.add_message("system", lang.tr_format("sys_music_error", e=e))
                self.menu_audio.entryconfig(1, label=lang.tr("menu_music_off"))
        else:
            Audio.stop_music()
            self.menu_audio.entryconfig(1, label=lang.tr("menu_music_off"))
            self.add_message("system", lang.tr("sys_music_off"))

    def load_ai(self):
        try:
            logging.info("Cargando IA...")
            print("Paso 1: Cargando IA...")
            self.ai = GPT4AllAI()
            print("Paso 1 completado")
            logging.info("IA cargada")
            print("Paso 2: Inicializando TTS...")
            self.tts = TTS()
            print("Paso 2 completado")
            logging.info("TTS inicializado")
            self.ai_loaded = True
            self.root.after(0, self.on_ai_loaded)
        except Exception as e:
            error_msg = str(e)
            print("Error: " + error_msg)
            logging.error(f"Error cargando IA: {error_msg}")
            self.ai = None
            try:
                self.tts = TTS()
            except Exception:
                self.tts = None
            self.ai_loaded = True
            self.root.after(0, lambda: self.add_message("system", f"⚠️ Error: {error_msg}. Usando modo offline."))
            self.root.after(0, lambda: self.status_label.config(text=">> MODO OFFLINE", fg="#FF6B35"))
            self.root.after(0, self.on_ai_loaded)

    def on_ai_loaded(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        if not getattr(self, '_dl_in_progress', False):
            self._hide_dl_ui()

        tts_mode = getattr(self.tts, 'mode', 'none') if hasattr(self, 'tts') and self.tts else 'none'
        if tts_mode in ("none", "offline"):
            self.tts_enabled = False
            self.menu_audio.entryconfig(0, label=lang.tr("menu_tts_off"))
            self.add_message("system", lang.tr("sys_tts_auto_off"))

        modelo = self._modelo_nombre()
        modelo_ausente = self.ai is None or getattr(self.ai, 'is_offline', False)
        if modelo_ausente:
            self.status_label.config(text=lang.tr("status_offline_long"), fg="#FF6B35")
            self.add_message("system", lang.tr_format("sys_offline_msg", modelo=modelo))
            model_dir = os.path.join(self.project_dir, "models")
            has_model = os.path.isdir(model_dir) and any(
                f.endswith(".gguf") and os.path.getsize(os.path.join(model_dir, f)) > 1000000
                for f in os.listdir(model_dir))
            if has_model:
                self.add_message("system", lang.tr("sys_model_no_llamacpp"))
            else:
                self.add_message("system", lang.tr("sys_offline_hint"))
            self.menu_sistema.entryconfig(self.menu_download_idx, state='normal')
            logging.info("Modelo en modo offline")
        else:
            self.status_label.config(text=lang.tr_format("status_ready", modelo=modelo), fg="#27AE60")
            self.add_message("system", lang.tr_format("sys_model_loaded", modelo=modelo))
            self.menu_sistema.entryconfig(self.menu_download_idx, state='disabled')
            logging.info("Modelo listo!")

    def _model_downloaded(self):
        self.add_message("system", lang.tr("sys_model_downloaded"))
        self.status_label.config(text=lang.tr("status_reloading"), fg="#FFD700")
        threading.Thread(target=self._reload_ai_after_download, daemon=True).start()

    def _reload_ai_after_download(self):
        try:
            self.ai = GPT4AllAI()
            self.root.after(0, self.on_ai_loaded)
        except Exception as e:
            self.root.after(0, lambda: self.add_message("system", lang.tr_format("sys_model_reload_error", e=e)))
            self.root.after(0, self._hide_dl_ui)

    def _hide_dl_ui(self):
        if self.dl_dialog:
            try:
                self.dl_dialog.destroy()
            except Exception:
                pass
            self.dl_dialog = None
        self.dl_progress_bar = None
        self.dl_pct_label = None
        self.dl_status_label = None

    def _download_model_url(self):
        return getattr(self, '_dl_repo', ""), getattr(self, '_dl_file', "")

    def download_model(self):
        if getattr(self, '_dl_in_progress', False):
            self.add_message("system", "⚠️ Ya hay una descarga en curso")
            return
        model_dir = os.path.join(self.project_dir, "models")
        os.makedirs(model_dir, exist_ok=True)
        MODELS = [
            {
                "label": lang.tr("dl_qwen15"),
                "repo": "MaziyarPanahi/Qwen2.5-1.5B-Instruct-GGUF",
                "file": "Qwen2.5-1.5B-Instruct.Q4_K_M.gguf",
                "size": "~986 MB",
                "name": "Qwen2.5 1.5B",
                "sha256": None,
            },
            {
                "label": lang.tr("dl_tinyllama"),
                "repo": "MaziyarPanahi/TinyLlama-1.1B-Chat-v1.0-GGUF",
                "file": "TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf",
                "size": "~660 MB",
                "name": "TinyLlama 1.1B",
                "sha256": None,
            },
            {
                "label": lang.tr("dl_qwen3b"),
                "repo": "MaziyarPanahi/Qwen2.5-3B-Instruct-GGUF",
                "file": "Qwen2.5-3B-Instruct.Q4_K_M.gguf",
                "size": "~1.93 GB",
                "name": "Qwen2.5 3B",
                "sha256": None,
            },
        ]
        dialog = tk.Toplevel(self.root)
        dialog.title(lang.tr("dl_title"))
        dialog.geometry("520x320")
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        tk.Label(dialog, text=lang.tr("dl_select"), font=("Helvetica", 12, "bold"),
                 bg="#1a1a2e", fg="#FFD700").pack(pady=(15, 10))
        var = tk.IntVar(value=0)
        for i, m in enumerate(MODELS):
            rec = "  " + lang.tr("dl_recommended") if i == 0 else ""
            tk.Radiobutton(dialog, text=m["label"] + rec, variable=var, value=i,
                           font=("Helvetica", 11), bg="#1a1a2e", fg="#ECF0F1",
                           selectcolor="#1a1a2e", activebackground="#1a1a2e",
                           activeforeground="#FFD700", anchor='w').pack(anchor='w', padx=30, pady=4)
        btn_frame = tk.Frame(dialog, bg="#1a1a2e")
        btn_frame.pack(pady=(15, 10))
        def _start_dl():
            idx = var.get()
            sel = MODELS[idx]
            self._dl_repo = sel["repo"]
            self._dl_file = sel["file"]
            self._dl_sha256 = sel.get("sha256")
            dialog.destroy()
            self._do_download(model_dir, sel["name"], sel["size"])
        tk.Button(btn_frame, text=lang.tr("dl_download_btn"), font=("Helvetica", 10, "bold"),
                  bg="#FF6B35", fg="white", relief=tk.FLAT, padx=15, pady=5, command=_start_dl).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=lang.tr("dl_cancel_btn"), font=("Helvetica", 10),
                  bg="#2C3E50", fg="white", relief=tk.FLAT, padx=15, pady=5, command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _do_download(self, model_dir, model_name, model_size):
        repo, name = self._download_model_url()
        path = os.path.join(model_dir, name)
        if os.path.exists(path) and os.path.getsize(path) > 1000000:
            self.add_message("system", lang.tr("sys_model_exists"))
            threading.Thread(target=self._reload_ai_after_download, daemon=True).start()
            return
        self.add_message("system", lang.tr_format("sys_model_downloading", name=model_name, size=model_size))
        self.menu_sistema.entryconfig(self.menu_download_idx, state='disabled')
        self._last_pct = -1
        self._show_dl_ui(model_name)
        download_url = f"https://huggingface.co/{repo}/resolve/main/{name}"
        manual_url = f"https://huggingface.co/{repo}/tree/main"

        def _do():
            import ssl
            success = False
            tmp = path + ".tmp"
            logging.info(f"Iniciando descarga: {download_url}")
            try:
                ctx = ssl.create_default_context()
                req = urllib.request.Request(download_url)
                req.add_header("User-Agent", "IRON-CHAT-LUNA/2.2")
                resp = urllib.request.urlopen(req, context=ctx, timeout=120)
                total = int(resp.headers.get("Content-Length", 0))
                logging.info(f"Content-Length: {total} bytes")
                sent = 0
                chunk_size = 65536
                last_ui_time = time.time()
                ui_interval = 0.5
                with open(tmp, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        sent += len(chunk)
                        now = time.time()
                        if total > 0:
                            pct = int(sent * 100 / total)
                            last = getattr(self, '_last_pct', -1)
                            if pct >= last + 2 or pct == 100:
                                self._last_pct = pct
                                self.root.after(0, lambda p=pct, s=sent, t=total: self._update_dl_ui(p, s, t))
                        elif now - last_ui_time >= ui_interval:
                            last_ui_time = now
                            self.root.after(0, lambda s=sent: self._update_dl_ui(None, s, None))
                resp.close()
                self.root.after(0, lambda s=sent, t=total: self._update_dl_ui(100, s, t))
                sz = os.path.getsize(tmp)
                if sz < 1000000:
                    raise RuntimeError(f"Archivo corrupto: solo {sz} bytes")
                file_hash = sha256_file(tmp)
                logging.info(f"SHA256 del modelo descargado: {file_hash}")
                expected = getattr(self, '_dl_sha256', None)
                if expected and not verify_file(tmp, expected):
                    os.remove(tmp)
                    raise RuntimeError(f"SHA256 no coincide: esperado {expected[:16]}..., obtenido {file_hash[:16]}...")
                for _ in range(3):
                    try:
                        os.replace(tmp, path)
                        break
                    except OSError as e:
                        if _ == 2:
                            raise
                        logging.warning(f"os.replace falló (intento {_+1}/3): {e}")
                        time.sleep(1)
                success = True
                logging.info(f"Descarga completada: {path} ({sz} bytes)")
                self.root.after(0, self._model_downloaded)
            except urllib.error.HTTPError as e:
                logging.error(f"HTTP Error {e.code}: {e.reason}")
                msg = lang.tr("sys_http_error", code=e.code)
                if e.code in (401, 403):
                    msg += lang.tr("sys_access_denied")
                self.root.after(0, lambda m=msg: self.add_message("system", m))
            except urllib.error.URLError as e:
                err = str(e.reason) if hasattr(e, 'reason') else str(e)
                logging.error(f"URL Error: {err}")
                if "certificate" in err.lower() or "ssl" in err.lower():
                    self.root.after(0, lambda: self.add_message("system", lang.tr("sys_ssl_error")))
                elif "timed out" in err.lower():
                    self.root.after(0, lambda: self.add_message("system", lang.tr("sys_timeout_error")))
                else:
                    self.root.after(0, lambda m=err: self.add_message("system", lang.tr("sys_network_error", err=m)))
            except OSError as e:
                self.root.after(0, lambda m=str(e): self.add_message("system", lang.tr("sys_disk_error", e=m)))
            except Exception as e:
                logging.error(f"Download error: {e}")
                self.root.after(0, lambda m=str(e): self.add_message("system", lang.tr("sys_download_error", e=m)))
            finally:
                self._dl_in_progress = False
                self.root.after(0, lambda: self.menu_sistema.entryconfig(
                    self.menu_download_idx, state='normal'))
                if not success:
                    self.root.after(0, self._hide_dl_ui)
                if os.path.exists(tmp):
                    try: os.remove(tmp)
                    except Exception as e: logging.warning(f"No se pudo eliminar {tmp}: {e}")
                if not os.path.exists(path):
                    self.root.after(0, lambda: self.add_message("system",
                        lang.tr_format("sys_download_manual", url=manual_url, model_dir=model_dir)))

        self._dl_in_progress = True
        threading.Thread(target=_do, daemon=True).start()

    def _show_dl_ui(self, model_name=""):
        self.dl_dialog = tk.Toplevel(self.root)
        self.dl_dialog.title(lang.tr("dl_dialog_title"))
        self.dl_dialog.geometry("420x180")
        self.dl_dialog.configure(bg="#1a1a2e")
        self.dl_dialog.resizable(False, False)
        self.dl_dialog.transient(self.root)
        self.dl_dialog.grab_set()
        self.dl_dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        self.dl_dialog.focus_set()
        tk.Label(self.dl_dialog, text=lang.tr_format("dl_downloading", name=model_name or ""),
                 font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#FFD700").pack(pady=(20, 10))
        self.dl_progress_bar = ttk.Progressbar(self.dl_dialog, mode='determinate', length=350)
        self.dl_progress_bar.pack(pady=10)
        self.dl_pct_label = tk.Label(self.dl_dialog, text="0% (0.0/0.0 GB)", font=("Helvetica", 10),
                                     bg="#1a1a2e", fg="#ECF0F1")
        self.dl_pct_label.pack(pady=5)
        self.dl_status_label = tk.Label(self.dl_dialog, text=lang.tr("dl_init"), font=("Helvetica", 9),
                                        bg="#1a1a2e", fg="#7F8C8D")
        self.dl_status_label.pack(pady=5)
        self.status_label.config(text=lang.tr("status_downloading"), fg="#FFD700")
        logging.info(f"Mostrando diálogo de descarga para: {model_name}")

    def _update_dl_ui(self, pct, sent, total):
        if self.dl_progress_bar and self.dl_pct_label:
            if total and total > 0:
                self.dl_progress_bar['value'] = pct
                gb_sent = sent / (1024**3)
                gb_total = total / (1024**3)
                self.dl_pct_label.config(text=f"{pct}% ({gb_sent:.1f}/{gb_total:.1f} GB)")
                if pct == 100:
                    self.dl_status_label.config(text=lang.tr("dl_verifying"))
                    self.dl_pct_label.config(fg="#27AE60")
                else:
                    self.dl_status_label.config(text=lang.tr_format("dl_progress", pct=pct))
            elif pct == 100:
                self.dl_status_label.config(text=lang.tr("dl_verifying"))
                self.dl_pct_label.config(fg="#27AE60")
            else:
                mb_sent = sent / (1024**2)
                self.dl_progress_bar['value'] = 0
                self.dl_pct_label.config(text=f"{mb_sent:.1f} MB")
                self.dl_status_label.config(text=lang.tr("dl_progress_bytes", mb=mb_sent))
            self.root.update_idletasks()

    def _desktop_path(self):
        for folder in ["Desktop", "Escritorio"]:
            p = os.path.join(os.path.expanduser("~"), folder)
            if os.path.exists(p):
                return p
        return None

    def _pythonw_path(self):
        e = getattr(_sys, 'executable', None)
        if e and e.lower().endswith('python.exe'):
            w = e[:-4] + 'w.exe'
            if os.path.exists(w):
                return w
        return e or 'pythonw.exe'

    def crear_acceso_escritorio(self):
        desktop = self._desktop_path()
        if not desktop:
            self.add_message("system", "⚠️ No se encontró la carpeta de escritorio")
            return

        nombre = "IRON CHAT - LUNA"
        main_py = os.path.join(self.project_dir, "main.py")
        icon_png = os.path.join(self.project_dir, "robot-icon.png")
        icon_ico = os.path.join(self.project_dir, "robot-icon.ico")

        if _platform.system() == "Windows":
            target_exe = self._pythonw_path()
            lnk_path = os.path.join(desktop, f"{nombre}.lnk")
            bat_path = os.path.join(desktop, f"{nombre}.bat")

            # .lnk via VBS (funciona sin win32com)
            vbs = os.path.join(self.project_dir, "_crear_lnk_tmp.vbs")
            icono = icon_ico if os.path.exists(icon_ico) else target_exe
            with open(vbs, "w", encoding="utf-8") as f:
                f.write(
                    f'Set o = WScript.CreateObject("WScript.Shell")\n'
                    f'Set s = o.CreateShortcut("{lnk_path}")\n'
                    f's.TargetPath = "{target_exe}"\n'
                    f's.Arguments = "{main_py}"\n'
                    f's.WorkingDirectory = "{self.project_dir}"\n'
                    f's.IconLocation = "{icono}"\n'
                    f's.WindowStyle = 7\n'
                    f's.Description = "{nombre}"\n'
                    f's.Save\n'
                )
            try:
                subprocess.run(["cscript", "/nologo", vbs], capture_output=True, timeout=15)
            except Exception:
                pass
            finally:
                try:
                    os.remove(vbs)
                except Exception:
                    pass

            # .bat de respaldo
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(f'@echo off\nstart "" /B "{target_exe}" "{main_py}"\nexit\n')

            self.add_message("system", "🖥️ Acceso directo creado en el escritorio (.lnk + .bat)")
        else:
            desk_path = os.path.join(desktop, f"{nombre}.desktop")
            icono = icon_png if os.path.exists(icon_png) else ""
            with open(desk_path, "w", encoding="utf-8") as f:
                f.write(
                    "[Desktop Entry]\n"
                    "Type=Application\n"
                    f"Name={nombre}\n"
                    f"Exec=python3 \"{main_py}\"\n"
                    f"Icon={icono}\n"
                    "Terminal=false\n"
                    "Categories=Utility;\n"
                )
            os.chmod(desk_path, 0o755)
            self.add_message("system", "🖥️ Acceso directo creado en el escritorio")

    def _get_conversation_context(self, max_exchanges=5):
        exchanges = []
        user_markers = ("TÚ:", "YOU:")
        assistant_marker = "IRON:"
        history = list(self.chat_history)
        for msg in reversed(history):
            msg_s = msg.strip()
            if msg_s.startswith("["):
                for marker in user_markers:
                    if marker in msg_s:
                        text = msg_s.split(marker, 1)[1].strip()
                        exchanges.append(("user", text))
                        break
                else:
                    if assistant_marker in msg_s:
                        text = msg_s.split(assistant_marker, 1)[1].strip()
                        exchanges.append(("assistant", text))
            if len(exchanges) >= max_exchanges * 2:
                break
        exchanges.reverse()
        return exchanges

    def add_message(self, sender, message, streamed=False):
        self.chat_area.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        if sender == "user":
            formatted = f"[{timestamp}] {lang.tr('user_prefix')}: {message}\n"
            tag = "user_msg"
        elif sender == "ai":
            if streamed:
                self.chat_area.delete(self._stream_start_index, tk.END)
                formatted = f"{message}\n"
                tag = "ai_msg"
            else:
                formatted = f"[{timestamp}] {lang.tr('ai_prefix')}: {message}\n"
                tag = "ai_msg"
        else:
            formatted = f">> {message}\n"
            tag = "system_msg"
        self.chat_area.insert(tk.END, formatted, tag)
        self.chat_history.append(formatted.strip())
        self.guardar_historial()
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def procesar_comando(self, texto):
        cmd = texto.lower().strip()
        if cmd == "/ayuda" or cmd == "/help":
            self.show_help()
            return True
        elif cmd == "/limpiar" or cmd == "/clear":
            self.clear_chat()
            return True
        elif cmd == "/tema" or cmd == "/theme":
            self.toggle_theme()
            return True
        elif cmd == "/exportar" or cmd == "/export":
            self.export_chat()
            return True
        elif cmd == "/notas" or cmd == "/notes":
            self.open_notes()
            return True
        elif cmd == "/musica" or cmd == "/music":
            self.toggle_music()
            return True
        elif cmd == "/stats":
            tema_nombre = self.colores[self.tema_actual]["nombre"]
            modelo = self._modelo_nombre()
            stats = f"📊 ESTADISTICAS:\nMensajes: {self.mensajes_count}\nTTS: {'ON' if self.tts_enabled else 'OFF'}\nTema: {tema_nombre}\nModelo: {modelo}"
            messagebox.showinfo("📊 ESTADISTICAS", stats)
            return True
        elif cmd.startswith("/dieta"):
            parts = cmd.split(maxsplit=1)
            tipo = parts[1] if len(parts) > 1 else ""
            prompt_map = {
                "volumen": "Dame un plan de dieta de volumen para ganar masa muscular. Incluye comidas, cantidades y calorías.",
                "definicion": "Dame un plan de dieta de definición para perder grasa corporal. Incluye comidas, cantidades y calorías.",
                "definición": "Dame un plan de dieta de definición para perder grasa corporal. Incluye comidas, cantidades y calorías.",
                "saludable": "Dame un plan de alimentación saludable y equilibrada para mantener un buen estado físico.",
            }
            if tipo in prompt_map:
                self.input_field.delete(0, tk.END)
                self.input_field.insert(0, prompt_map[tipo])
                self.send_message()
            else:
                ayuda_dieta = ("🥗 DIETAS DISPONIBLES:\n\n"
                              "• /dieta volumen — Para ganar masa muscular\n"
                              "• /dieta definicion — Para perder grasa\n"
                              "• /dieta saludable — Plan equilibrado\n\n"
                              "O pregúntame directamente en el chat.")
                messagebox.showinfo("🥗 DIETA", ayuda_dieta)
            return True
        elif cmd.startswith("/recordatorio") or cmd.startswith("/reminder"):
            parts = cmd.split(maxsplit=2)
            if len(parts) >= 3:
                try:
                    mins = int(parts[1])
                    msg = parts[2]
                    self.add_message("system", f"⏰ RECORDATORIO PROGRAMADO: {msg} en {mins} minuto(s)")
                    threading.Thread(target=self._reminder_thread, args=(mins * 60, msg), daemon=True).start()
                except ValueError:
                    self.add_message("system", "❌ Usa: /recordatorio <minutos> '<mensaje>'")
            else:
                self.add_message("system", "❌ Usa: /recordatorio <minutos> '<mensaje>' (ej: /recordatorio 30 'Beber agua')")
            return True
        elif cmd == "/ejercicio":
            ayuda_ej = ("📚 EJERCICIOS:\n\n"
                        "Pregúntame en el chat:\n"
                        "'cómo se hace sentadilla'\n"
                        "'cómo se hace press banca'\n"
                        "'cómo se hace peso muerto'\n"
                        "'cómo se hace dominada'\n"
                        "'cómo se hace flexión'\n"
                        "'cómo se hace curl de bíceps'")
            messagebox.showinfo("📚 EJERCICIOS", ayuda_ej)
            return True
        return False

    def send_message(self):
        if not self.ai_loaded:
            self.add_message("system", "⏳ Modelo aún cargándose, espera unos segundos...")
            return
        if self._sending:
            return
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        self.input_field.delete(0, tk.END)
        if self.procesar_comando(user_input):
            return
        self._sending = True
        self._last_user_input = user_input
        self.send_button.config(state=tk.DISABLED)
        try:
            Sounds.play_chat()
        except Exception:
            pass
        self.add_message("user", user_input)
        self.mensajes_count += 1
        self.actualizar_contador()
        self.status_label.config(text=lang.tr("status_writing"), fg="#FFD700")
        self.animar_escribiendo()
        threading.Thread(target=self.get_response, args=(user_input,), daemon=True).start()

    def get_response(self, user_input):
        try:
            ai = getattr(self, 'ai', None)
            if ai is None:
                self.root.after(0, lambda: self.add_message("system", lang.tr("sys_model_error", msg="Modelo no disponible")))
                self.root.after(0, self._finish_sending)
                return
            self.root.after(0, lambda: self.status_label.config(text=lang.tr("status_thinking"), fg="#3498DB"))
            history = self._get_conversation_context(5)
            use_stream = hasattr(ai, 'stream_response') and not ai.is_offline
            if use_stream:
                self._stream_response(user_input, history, ai)
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(ai.get_response, user_input, history=history)
                    try:
                        response = future.result(timeout=120)
                        self.root.after(0, lambda r=response: self._on_response(r))
                    except concurrent.futures.TimeoutError:
                        logging.warning("Inferencia agotó timeout de 120s, forzando offline")
                        ai.is_offline = True
                        self.root.after(0, lambda: self.add_message("system", lang.tr("sys_model_too_slow")))
                        self.root.after(0, lambda: self.add_message("system", lang.tr("sys_model_offline_fallback")))
                        self.root.after(0, lambda: self.status_label.config(text=lang.tr("status_offline"), fg="#FF6B35"))
                        self.root.after(0, self._finish_sending)
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error en get_response: {error_msg}")
            self.root.after(0, lambda: self.add_message("system", lang.tr("sys_model_error", msg=error_msg)))
            self.root.after(0, lambda: self.status_label.config(text=lang.tr("status_error"), fg="#E74C3C"))
            self.root.after(0, self._finish_sending)

    def _stream_response(self, user_input, history, ai):
        self.root.after(0, lambda: self._start_stream_ui())
        full_text = ""
        last_update = 0.0
        pending_update = None
        def _schedule_update(t):
            nonlocal pending_update
            if pending_update:
                try:
                    self.root.after_cancel(pending_update)
                except Exception:
                    logging.warning("Error cancelando pending_update")
            pending_update = self.root.after(0, lambda t=t: self._update_stream_ui(t))
        try:
            for partial in ai.stream_response(user_input, history=history):
                full_text = partial
                now = time.time()
                if now - last_update >= 0.05:
                    last_update = now
                    _schedule_update(full_text)
            if pending_update:
                try:
                    self.root.after_cancel(pending_update)
                except Exception:
                    logging.warning("Error cancelando pending_update en stream done")
            final = ai._post_process(full_text.strip()) if hasattr(ai, '_post_process') else full_text.strip()
            self.root.after(0, lambda r=final: self._on_stream_done(r))
        except Exception as e:
            logging.error(f"Error en stream: {e}")
            self.root.after(0, lambda: self.status_label.config(text=lang.tr("status_error"), fg="#E74C3C"))
            self.root.after(0, self._finish_sending)

    def _start_stream_ui(self):
        self.chat_area.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_area.insert(tk.END, f"[{timestamp}] {lang.tr('ai_stream_prefix')}: ")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self._stream_start_index = self.chat_area.index(tk.END + "-1c")
        self.status_label.config(text=lang.tr("status_generating"), fg="#3498DB")

    def _update_stream_ui(self, text):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(self._stream_start_index, tk.END)
        self.chat_area.insert(tk.END, text)
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _recordar_conversacion(self, user_input, response):
        if not hasattr(self.ai, 'recordar'):
            return
        try:
            resumen = f"El usuario preguntó: '{user_input[:80]}' | LUNA respondió sobre: '{response[:80]}'"
            self.ai.recordar(resumen)
        except Exception:
            pass

    def _on_stream_done(self, response):
        self.add_message("ai", response, streamed=True)
        tts_activo = self.tts_enabled and hasattr(self, 'tts') and self.tts and self.tts.mode not in ("none", "offline")
        if not tts_activo:
            Sounds.play_notification()
        self.speak_response(response)
        self._recordar_conversacion(self._last_user_input, response)

    def _on_response(self, response):
        self.add_message("ai", response)
        tts_activo = self.tts_enabled and hasattr(self, 'tts') and self.tts and self.tts.mode not in ("none", "offline")
        if not tts_activo:
            Sounds.play_notification()
        self.speak_response(response)
        self._recordar_conversacion(self._last_user_input, response)

    def _finish_sending(self):
        if not self._sending:
            return
        self._sending = False
        timeout = getattr(self, '_sending_timeout', None)
        if timeout:
            try:
                self.root.after_cancel(timeout)
            except Exception:
                pass
            self._sending_timeout = None
        try:
            self.send_button.config(state=tk.NORMAL)
        except Exception:
            pass

    def speak_response(self, response):
        texto_limpio = re.sub(r"[^\w\s,;:.!?¡¿áéíóúüñÁÉÍÓÚÜÑ]", " ", response)
        texto_limpio = re.sub(r"\s+", " ", texto_limpio).strip()
        if not self.tts_enabled:
            self.status_label.config(text=lang.tr("status_ready_short"), fg="#27AE60")
            self._finish_sending()
            return
        tts = getattr(self, 'tts', None)
        if not tts or not hasattr(tts, 'speak'):
            self._finish_sending()
            return
        self.face.set_speaking(True)
        self.status_label.config(text=lang.tr("status_speaking"), fg="#FF6B35")
        # Safety timeout: unlock sending if TTS hangs for 30s
        def _tts_timeout():
            self._cancel_tts_timeout()
            self.face.set_speaking(False)
            self.status_label.config(text=lang.tr("status_ready_short"), fg="#27AE60")
            self._finish_sending()
        self._tts_timeout_id = self.root.after(30000, _tts_timeout)
        def _on_done():
            self.root.after(0, self._on_tts_done_safe)
        try:
            tts.speak(texto_limpio if texto_limpio else response, on_finish=_on_done)
        except Exception:
            self._cancel_tts_timeout()
            self._finish_sending()

    def _cancel_tts_timeout(self):
        timeout_id = getattr(self, '_tts_timeout_id', None)
        if timeout_id:
            try: self.root.after_cancel(timeout_id)
            except Exception: pass
            self._tts_timeout_id = None

    def _on_tts_done_safe(self):
        self._cancel_tts_timeout()
        self.on_tts_finish()

    def on_tts_finish(self):
        self.face.set_speaking(False)
        self.status_label.config(text=lang.tr("status_ready_short"), fg="#27AE60")
        self._finish_sending()

    # ===================================================================
    # TEMPORIZADOR
    # ===================================================================
    def timer_custom(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("⏱️ TEMPORIZADOR PERSONALIZADO")
        dialog.geometry("300x150")
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        tk.Label(dialog, text="Minutos:", font=("Helvetica", 11, "bold"), bg="#1a1a2e", fg="#FFD700").pack(pady=(15, 5))
        entry = tk.Entry(dialog, font=self.FONT_MONO_LG, bg="#1a1a2e", fg="#ECF0F1", insertbackground="#ECF0F1", relief=tk.FLAT, width=10, justify=tk.CENTER)
        entry.pack(pady=5)
        entry.insert(0, "1")
        entry.select_range(0, tk.END)
        entry.focus()
        def start_custom():
            try:
                mins = int(entry.get().strip())
                if mins > 0 and mins <= 60:
                    self.timer_start(mins * 60)
                    dialog.destroy()
                else:
                    messagebox.showwarning("⏱️", "Introduce entre 1 y 60 minutos.")
            except ValueError:
                messagebox.showwarning("⏱️", "Introduce un número válido.")
        tk.Button(dialog, text="INICIAR", font=("Helvetica", 11, "bold"), bg="#27AE60", fg="white",
                 command=start_custom, relief=tk.FLAT, width=15, bd=0).pack(pady=10)
        dialog.bind("<Return>", lambda e: start_custom() or "break")

    def timer_start(self, seconds):
        if self.timer_running:
            self.timer_stop()
        self.timer_running = True
        self.timer_remaining = seconds
        self.timer_label.config(text=f"⏱️ {seconds//60:02d}:{seconds%60:02d}")
        self.timer_job = self.root.after(1000, self.timer_tick)

    def timer_stop(self):
        self.timer_running = False
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_label.config(text="⏱️ 00:00")

    def timer_tick(self):
        if not self.timer_running:
            return
        self.timer_remaining -= 1
        mins, secs = divmod(max(self.timer_remaining, 0), 60)
        self.timer_label.config(text=f"⏱️ {mins:02d}:{secs:02d}")
        if self.timer_remaining <= 0:
            self.timer_running = False
            self.add_message("system", "⏱️ DESCANSO TERMINADO! A darle! 💪🔥")
            self.root.after(0, lambda: Sounds.play_notification())
        else:
            self.timer_job = self.root.after(1000, self.timer_tick)

    def _reminder_thread(self, seconds, message):
        time.sleep(seconds)
        self.root.after(0, lambda: self.add_message("system", f"⏰ RECORDATORIO: {message}"))
        self.root.after(0, lambda: Sounds.play_notification())

    # ===================================================================
    # RUTINAS RAPIDAS
    # ===================================================================
    def show_routines(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("🏋️ RUTINAS RÁPIDAS")
        dialog.geometry("360x340")
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        tk.Label(dialog, text="¿Qué rutina quieres?", font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#FFD700").pack(pady=10)
        for name, prompt in [
            ("🏋️ PUSH (Empuje)", "Crea una rutina de ejercicios de empuje (push): pecho, hombros y tríceps. Incluye series y repeticiones."),
            ("🏋️ PULL (Tracción)", "Crea una rutina de ejercicios de tracción (pull): espalda y bíceps. Incluye series y repeticiones."),
            ("🦵 PIERNAS", "Crea una rutina de piernas completa: cuádriceps, isquiotibiales, glúteos y gemelos. Incluye series y repeticiones."),
            ("💪 FULL BODY", "Crea una rutina de cuerpo completo con ejercicios compuestos. Incluye series y repeticiones."),
            ("🏃 CARDIO", "Crea una rutina de cardio para quemar grasa: HIIT, trote, bicicleta, cuerda. Incluye tiempos y series."),
            ("🤸 CALISTENIA", "Crea una rutina de calistenia sin pesas: flexiones, dominadas, sentadillas, plancha. Incluye series y repeticiones."),
        ]:
            tk.Button(dialog, text=name, font=("Helvetica", 10, "bold"), bg="#2C3E50", fg="white",
                     command=lambda p=prompt: self._send_routine(p, dialog), relief=tk.FLAT, width=28, bd=0).pack(pady=3)
        tk.Button(dialog, text="CERRAR", font=("Helvetica", 9, "bold"), bg="#E74C3C", fg="white",
                 command=dialog.destroy, relief=tk.FLAT, width=28, bd=0).pack(pady=8)

    def _send_routine(self, prompt, dialog):
        dialog.destroy()
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, prompt)
        self.send_message()

    # ===================================================================
    # PROGRESO SQLITE
    # ===================================================================
    def show_progress(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("📊 PROGRESO")
        dialog.geometry("400x350")
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        tk.Label(dialog, text="📊 SEGUIMIENTO DE PROGRESO", font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#FFD700").pack(pady=10)
        btn_frame = tk.Frame(dialog, bg="#1a1a2e")
        btn_frame.pack(expand=True)
        tk.Button(btn_frame, text="➕ AÑADIR MEDICIÓN", font=("Helvetica", 11, "bold"), bg="#27AE60", fg="white",
                 command=lambda: self._add_progress_ui(dialog), relief=tk.FLAT, width=22, height=2, bd=0).pack(pady=5)
        tk.Button(btn_frame, text="📈 VER HISTORIAL", font=("Helvetica", 11, "bold"), bg="#2980B9", fg="white",
                 command=lambda: self._view_progress(dialog), relief=tk.FLAT, width=22, height=2, bd=0).pack(pady=5)
        tk.Button(btn_frame, text="CERRAR", font=("Helvetica", 9, "bold"), bg="#E74C3C", fg="white",
                 command=dialog.destroy, relief=tk.FLAT, width=22, bd=0).pack(pady=10)

    def _add_progress_ui(self, parent):
        if self.progress is None:
            self.add_message("system", "⚠️ Progreso no disponible (error de base de datos)")
            return
        dialog = tk.Toplevel(parent)
        dialog.title("➕ AÑADIR MEDICIÓN")
        dialog.geometry("320x380")
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        fields = {}
        tk.Label(dialog, text="Nueva Medición", font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#FFD700").pack(pady=10)
        form = tk.Frame(dialog, bg="#1a1a2e")
        form.pack(pady=5)
        labels = {"weight": "Peso (kg)", "bicep": "Bíceps (cm)", "chest": "Pecho (cm)", "waist": "Cintura (cm)", "thigh": "Pierna (cm)"}
        row = 0
        for key, label in labels.items():
            tk.Label(form, text=label, font=("Helvetica", 10), bg="#1a1a2e", fg="#ECF0F1").grid(row=row, column=0, sticky="w", pady=3)
            entry = tk.Entry(form, font=self.FONT_MONO_SM, bg="#1a1a2e", fg="#ECF0F1", insertbackground="#ECF0F1", relief=tk.FLAT, width=10)
            entry.grid(row=row, column=1, padx=10, pady=3)
            fields[key] = entry
            row += 1
        tk.Label(form, text="Notas", font=("Helvetica", 10), bg="#1a1a2e", fg="#ECF0F1").grid(row=row, column=0, sticky="w", pady=3)
        notes_entry = tk.Entry(form, font=self.FONT_MONO_SM, bg="#1a1a2e", fg="#ECF0F1", insertbackground="#ECF0F1", relief=tk.FLAT, width=10)
        notes_entry.grid(row=row, column=1, padx=10, pady=3)

        def save():
            vals = {}
            for key, entry in fields.items():
                v = entry.get().strip()
                try:
                    vals[key] = float(v) if v else None
                except ValueError:
                    self.add_message("system", f"⚠ Valor inválido para {key}, ingresa un número")
                    return
            self.progress.add_entry(**vals, notes=notes_entry.get().strip())
            self.add_message("system", "📊 MEDICIÓN GUARDADA!")
            dialog.destroy()

        btn_save = tk.Button(dialog, text="💾 GUARDAR", font=("Helvetica", 11, "bold"), bg="#27AE60", fg="white",
                            command=save, relief=tk.FLAT, width=20, bd=0)
        btn_save.pack(pady=15)

    def _view_progress(self, parent):
        if self.progress is None:
            self.add_message("system", "⚠️ Progreso no disponible (error de base de datos)")
            return
        entries = self.progress.get_entries()
        dialog = tk.Toplevel(parent)
        dialog.title("📈 HISTORIAL")
        dialog.geometry("650x450")
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        tk.Label(dialog, text="📈 HISTORIAL DE PROGRESO", font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#FFD700").pack(pady=10)
        text_frame = tk.Frame(dialog, bg="#0d0d1a")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        text_area = tk.Text(text_frame, font=self.FONT_MONO_SM, bg="#0d0d1a", fg="#ECF0F1", wrap=tk.NONE, relief=tk.FLAT, bd=0)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = tk.Scrollbar(text_frame, command=text_area.yview, bg="#34495E", troughcolor="#1a1a2e")
        scroll.pack(fill=tk.Y, side=tk.RIGHT)
        text_area.config(yscrollcommand=scroll.set)
        text_area.insert(tk.END, f"{'FECHA':<16} {'PESO':<9} {'BÍCEPS':<9} {'PECHO':<9} {'CINTURA':<9} {'PIERNA':<9}\n")
        text_area.insert(tk.END, "-"*65 + "\n")
        prev = None
        for entry in entries:
            date, weight, bicep, chest, waist, thigh, notes = entry
            def fmt(v, pv):
                s = f"{v:.1f}" if v else "-"
                if v is not None and pv is not None:
                    delta = v - pv
                    if delta > 0:
                        s += f" ▲{delta:.1f}"
                    elif delta < 0:
                        s += f" ▼{abs(delta):.1f}"
                    else:
                        s += f"  ="
                return s.center(9)
            w = fmt(weight, prev[1] if prev else None)
            b = fmt(bicep, prev[2] if prev else None)
            c = fmt(chest, prev[3] if prev else None)
            wa = fmt(waist, prev[4] if prev else None)
            t = fmt(thigh, prev[5] if prev else None)
            text_area.insert(tk.END, f"{date:<16} {w} {b} {c} {wa} {t}\n")
            prev = (date, weight, bicep, chest, waist, thigh, notes)
        text_area.config(state=tk.DISABLED)
        btn_frame = tk.Frame(dialog, bg="#1a1a2e")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="📊 VER ESTADÍSTICAS", font=("Helvetica", 9, "bold"), bg="#2980B9", fg="white",
                 command=lambda: self._show_progress_stats(entries), relief=tk.FLAT, width=18, bd=0).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="CERRAR", font=("Helvetica", 9, "bold"), bg="#E74C3C", fg="white",
                 command=dialog.destroy, relief=tk.FLAT, width=18, bd=0).pack(side=tk.LEFT, padx=5)

    def _show_progress_stats(self, entries):
        if len(entries) < 2:
            messagebox.showinfo("📊 ESTADÍSTICAS", "Necesitas al menos 2 mediciones para ver estadísticas.")
            return
        first = entries[-1]
        last = entries[0]
        fields = [("Peso", 1), ("Bíceps", 2), ("Pecho", 3), ("Cintura", 4), ("Pierna", 5)]
        lines = ["📊 RESUMEN DE PROGRESO\n", "="*35 + "\n"]
        for fname, fidx in fields:
            fv = first[fidx]
            lv = last[fidx]
            if fv is not None and lv is not None:
                delta = lv - fv
                arrow = "▲" if delta > 0 else "▼" if delta < 0 else "="
                lines.append(f"{fname}: {fv:.1f} → {lv:.1f}  {arrow} {abs(delta):.1f}\n")
            elif lv is not None:
                lines.append(f"{fname}: - → {lv:.1f}\n")
        lines.append(f"\nPeríodo: {first[0]} → {last[0]}")
        messagebox.showinfo("📊 ESTADÍSTICAS", "".join(lines))

    def show_credits(self):
        modelo = self._modelo_nombre()
        credits = (
            "╔════════════════════════════════╗\n"
            "║    IRON CHAT - LUNA v2.2       ║\n"
            "╠════════════════════════════════╣\n"
            "║  👨‍💻 CREADOR: ⚡ JMB ⚡         ║\n"
            "╠════════════════════════════════╣\n"
            f"║ 🤖 {modelo:<26}║\n"
            "║ 📝 Python + Tkinter            ║\n"
            "║ 🧠 llama-cpp-python (CPU)      ║\n"
            "╠════════════════════════════════╣\n"
            "║ 🏋️ Fitness + Nutricion + IA    ║\n"
            "║ 🎨 ASCII Art + TTS + Animacion ║\n"
            "║ 🎵 Musica + Temporizador       ║\n"
            "╠════════════════════════════════╣\n"
            "║  💻 Python 3.10+               ║\n"
            "║  🐧 Linux / 🪟 Windows         ║\n"
            "║  🔥 Hecho con dedicacion       ║\n"
            "╚════════════════════════════════╝"
        )
        messagebox.showinfo("🏆 CREDITOS", credits)

def main():
    try:
        if _HAS_TTB:
            root = tb.Window(themename=THEME_NAME)
        else:
            root = tk.Tk()
        app = ChatbotApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        logging.critical("Error de inicio:\n" + err)
        try:
            messagebox.showerror("ERROR", f"Error al iniciar:\n{e}\n\nVer el log: iron_chat.log")
        except Exception:
            print("ERROR:", err)

if __name__ == "__main__":
    main()
