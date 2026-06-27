import tkinter as tk
from tkinter import messagebox, ttk
import threading
from datetime import datetime
import os
import glob
import json
import re
import logging
import platform as _platform
import subprocess
from audio import Audio
from PIL import Image, ImageTk
from ai_module import GPT4AllAI
from tts_module import TTS
from face_animation import AnimatedFace
from ascii_art import ASCIIArt
from sounds import Sounds
from progress_tracker import ProgressTracker

# === LOGGING ===
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iron_chat.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logging.info("🚀 IRON CHAT iniciado")

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IRON CHAT - Gym Assistant")
        self.root.geometry("850x650")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        self.tts_enabled = True
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.historial_file = os.path.join(self.project_dir, "historial.json")
        self.music_playing = False
        self.mensajes_count = 0
        self.animacion_dots = 0
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_job = None
        self._sending = False
        self.progress = ProgressTracker(os.path.join(self.project_dir, "progreso.db"))
        self.init_ui()
        self.ai = None
        self.ai_loaded = False
        threading.Thread(target=self.load_ai, daemon=True).start()
        self.root.bind("<Control-l>", lambda e: self.clear_chat())
        self.root.bind("<Control-d>", lambda e: self.export_chat())
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())
        self.actualizar_reloj()

    def _find_image(self, *names):
        for name in names:
            path = os.path.join(self.project_dir, name)
            if os.path.exists(path):
                return path
        for ext in ['*.jpeg', '*.jpg', '*.png']:
            files = glob.glob(os.path.join(self.project_dir, ext))
            if files:
                return files[0]
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
        self.contador_label.config(text=f"💬 {self.mensajes_count} msgs")

    def aplicar_tema(self):
        c = self.colores[self.tema_actual]

        self.root.configure(bg=c["bg"])
        self.header.configure(bg=c["bg"])
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
        self.input_field.configure(bg=c["input_bg"], fg=c["fg"], insertbackground=c["fg"])
        self.send_button.configure(bg=c["naranja"])
        self.status_bar.configure(bg=c["chat_bg"])
        self.status_label.configure(bg=c["chat_bg"])
        self.contador_label.configure(bg=c["chat_bg"], fg=c["acento"])
        self.right_panel.configure(bg=c["bg"])
        self.tools_frame.configure(bg=c["bg"])
        self.tools_title.configure(bg=c["bg"], fg=c["acento"])
        self.btn_frame.configure(bg=c["bg"])

        btn_bg = c["btn_bg"]
        self.btn_clear.configure(bg=btn_bg)
        self.btn_export.configure(bg=btn_bg)
        self.btn_info.configure(bg=btn_bg)
        self.btn_notes.configure(bg=btn_bg)
        self.btn_routine.configure(bg=btn_bg)
        self.btn_progress.configure(bg=btn_bg)
        self.btn_ayuda.configure(bg=btn_bg)
        self.btn_credits.configure(bg=btn_bg)
        self.btn_music_folder.configure(bg=btn_bg)
        self.timer_frame.configure(bg=c["bg"])
        self.timer_label.configure(bg=c["bg"], fg=c["acento"])
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

        try:
            self.face.canvas.configure(bg=c["face_bg"])
        except Exception:
            pass

        self.btn_theme.config(text=c["nombre"], bg=c["btn_bg"])

    def init_ui(self):
        # === 1. HEADER ===
        self.header = tk.Frame(self.root, bg="#1a1a2e", height=60)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        self.title_label = tk.Label(self.header, text="💪  IRON CHAT  🏋️", font=("Helvetica", 22, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.title_label.pack(side=tk.LEFT, padx=15, pady=10)
        self.subtitle = tk.Label(self.header, text="GYM ASSISTANT PRO", font=("Helvetica", 9, "bold"), bg="#1a1a2e", fg="#FF6B35")
        self.subtitle.pack(side=tk.LEFT, padx=5, pady=15)
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
        self.chat_area = tk.Text(self.text_frame, font=("Consolas", 12), bg="#0d0d1a", fg="#ECF0F1", insertbackground="#ECF0F1", wrap=tk.WORD, relief=tk.FLAT, bd=0, padx=5, pady=5)
        self.chat_area.tag_config("user_msg", background="#1a3a5e", lmargin1=10, lmargin2=10, rmargin=10, spacing1=3, spacing3=3)
        self.chat_area.tag_config("ai_msg", background="#1a3a2e", lmargin1=10, lmargin2=10, rmargin=10, spacing1=3, spacing3=3)
        self.chat_area.tag_config("system_msg", background="#0d0d1a", spacing1=2, spacing3=2)
        self.chat_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.chat_area.yview, bg="#34495E", troughcolor="#1a1a2e")
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.chat_area.config(yscrollcommand=self.scrollbar.set)

        # Input
        self.input_frame = tk.Frame(self.overlay, bg="#0d0d1a", height=35)
        self.input_frame.place(relx=0.02, rely=0.83, relwidth=0.96)
        self.input_frame.pack_propagate(False)
        self.input_field = tk.Entry(self.input_frame, font=("Consolas", 12), bg="#1a1a2e", fg="#ECF0F1", insertbackground="#ECF0F1", relief=tk.FLAT, bd=0)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", lambda e: self.send_message())
        self.input_field.bind("<Control-Return>", lambda e: self.send_message())
        self.input_field.bind("<Control-l>", lambda e: self.clear_chat())
        self.send_button = tk.Button(self.input_frame, text="ENVIAR", font=("Helvetica", 10, "bold"), bg="#FF6B35", fg="white", command=self.send_message, relief=tk.FLAT, padx=12, pady=2, bd=0)
        self.send_button.pack(side=tk.RIGHT)

        # Status bar
        self.status_bar = tk.Frame(self.overlay, bg="#0d0d1a", height=25)
        self.status_bar.place(relx=0.02, rely=0.93, relwidth=0.96)
        self.status_label = tk.Label(self.status_bar, text=">> CARGANDO MODELO...", font=("Helvetica", 9, "bold"), bg="#0d0d1a", fg="#FFD700", anchor='w')
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.contador_label = tk.Label(self.status_bar, text="💬 0 msgs", font=("Helvetica", 8, "bold"), bg="#0d0d1a", fg="#FFD700")
        self.contador_label.pack(side=tk.RIGHT, padx=(5, 0))
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='indeterminate', length=80)
        self.progress_bar.pack(side=tk.RIGHT, padx=(0, 5))
        self.progress_bar.start()

        # === 4. RIGHT PANEL (DERECHA) ===
        self.right_panel = tk.Frame(self.main_container, bg="#1a1a2e", width=350)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.right_panel.pack_propagate(False)

        # Cara animada
        self.face = AnimatedFace(self.right_panel, x=35, y=10, size=280, project_dir=self.project_dir)

        # Tools
        self.tools_frame = tk.Frame(self.right_panel, bg="#1a1a2e", height=280)
        self.tools_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10))
        self.tools_frame.pack_propagate(False)
        self.tools_title = tk.Label(self.tools_frame, text="⚙️ HERRAMIENTAS", font=("Helvetica", 11, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.tools_title.pack(pady=(5, 8))
        self.btn_frame = tk.Frame(self.tools_frame, bg="#1a1a2e")
        self.btn_frame.pack(expand=True)

        # Botones
        self.btn_clear = tk.Button(self.btn_frame, text="🗑️ LIMPIAR", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.clear_chat, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_clear.grid(row=0, column=0, padx=5, pady=3)
        self.btn_tts = tk.Button(self.btn_frame, text="🔊 TTS: ON", font=("Helvetica", 9, "bold"), bg="#27AE60", fg="white", command=self.toggle_tts, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_tts.grid(row=0, column=1, padx=5, pady=3)
        self.btn_export = tk.Button(self.btn_frame, text="📤 EXPORTAR", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.export_chat, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_export.grid(row=1, column=0, padx=5, pady=3)
        self.btn_info = tk.Button(self.btn_frame, text="ℹ️ INFO", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.show_info, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_info.grid(row=1, column=1, padx=5, pady=3)
        self.btn_theme = tk.Button(self.btn_frame, text="🌙 MODO OSCURO", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.toggle_theme, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_theme.grid(row=2, column=0, padx=5, pady=3)
        self.btn_notes = tk.Button(self.btn_frame, text="📝 NOTAS", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.open_notes, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_notes.grid(row=2, column=1, padx=5, pady=3)
        self.btn_music = tk.Button(self.btn_frame, text="🎵 MÚSICA OFF", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.toggle_music, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_music.grid(row=3, column=0, padx=5, pady=3)
        self.btn_music_folder = tk.Button(self.btn_frame, text="📂 MP3", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.open_music_folder, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_music_folder.grid(row=3, column=1, padx=5, pady=3)
        self.btn_routine = tk.Button(self.btn_frame, text="🏋️ RUTINA", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.show_routines, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_routine.grid(row=4, column=0, padx=5, pady=3)
        self.btn_progress = tk.Button(self.btn_frame, text="📊 PROGRESO", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.show_progress, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_progress.grid(row=4, column=1, padx=5, pady=3)
        self.btn_ayuda = tk.Button(self.btn_frame, text="❓ AYUDA", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.show_help, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_ayuda.grid(row=5, column=0, padx=5, pady=3)
        self.btn_credits = tk.Button(self.btn_frame, text="🏆 CRÉDITOS", font=("Helvetica", 9, "bold"), bg="#2C3E50", fg="white", command=self.show_credits, relief=tk.FLAT, width=12, height=1, bd=0)
        self.btn_credits.grid(row=5, column=1, padx=5, pady=3)

        # === 5. COLORES ===
        self.tema_actual = 0
        self.colores = [
            {
                "nombre": "🌙 Oscuro",
                "bg": "#1a1a2e", "fg": "#ECF0F1", "chat_bg": "#0d0d1a",
                "btn_bg": "#2C3E50", "acento": "#FFD700", "naranja": "#FF6B35",
                "input_bg": "#1a1a2e", "scroll": "#34495E", "face_bg": "#2C3E50"
            },
            {
                "nombre": "☀️ Claro",
                "bg": "#F5F5F5", "fg": "#2C3E50", "chat_bg": "#FFFFFF",
                "btn_bg": "#2980B9", "acento": "#E67E22", "naranja": "#E74C3C",
                "input_bg": "#FFFFFF", "scroll": "#BDC3C7", "face_bg": "#2980B9"
            },
            {
                "nombre": "🌿 Naturaleza",
                "bg": "#1a2e1a", "fg": "#E8F5E9", "chat_bg": "#0d1a0d",
                "btn_bg": "#2E7D32", "acento": "#A5D6A7", "naranja": "#FF8A65",
                "input_bg": "#1a2e1a", "scroll": "#388E3C", "face_bg": "#2E7D32"
            },
        ]

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
        self.timer_label = tk.Label(self.timer_frame, text="⏱️ 00:00", font=("Helvetica", 10, "bold"), bg="#1a1a2e", fg="#FFD700")
        self.timer_label.pack(side=tk.RIGHT, padx=5)
        timer_btn_frame = tk.Frame(self.timer_frame, bg="#1a1a2e")
        timer_btn_frame.pack(side=tk.LEFT)
        self.timer_buttons = []
        for secs, label in [(30, "30s"), (60, "60s"), (90, "90s"), (120, "120s")]:
            btn = tk.Button(timer_btn_frame, text=label, font=("Helvetica", 8, "bold"), bg="#2C3E50", fg="white",
                           command=lambda s=secs: self.timer_start(s), relief=tk.FLAT, width=4, height=1, bd=0)
            btn.pack(side=tk.LEFT, padx=2)
            self.timer_buttons.append(btn)
        tk.Button(timer_btn_frame, text="⏱️", font=("Helvetica", 8, "bold"), bg="#8E44AD", fg="white",
                 command=self.timer_custom, relief=tk.FLAT, width=3, height=1, bd=0).pack(side=tk.LEFT, padx=2)
        tk.Button(timer_btn_frame, text="⏹", font=("Helvetica", 8, "bold"), bg="#E74C3C", fg="white",
                 command=self.timer_stop, relief=tk.FLAT, width=3, height=1, bd=0).pack(side=tk.LEFT, padx=2)

        # === 8. CREDITOS ===
        self.credit_frame = tk.Frame(self.right_panel, bg="#1a1a2e", height=30)
        self.credit_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.credit_frame.pack_propagate(False)
        self.credit_label = tk.Label(self.credit_frame, text="⚡ JMbirner ⚡", font=("Helvetica", 9, "bold"), bg="#1a1a2e", fg="#FF6B35")
        self.credit_label.pack(expand=True)

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
            self.add_message("system", "📂 HISTORIAL CARGADO ({0} mensajes)".format(len(self.chat_history)))
        else:
            self.add_message("system", "💪 BIENVENIDO A IRON CHAT!")
            self.add_message("system", ">> CARGANDO MODELO, ESPERA UN MOMENTO...")

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
        self.add_message("system", "🗑️ CHAT LIMPIADO")

    def toggle_tts(self):
        self.tts_enabled = not self.tts_enabled
        if self.tts_enabled:
            self.btn_tts.config(text="🔊 TTS: ON", bg="#27AE60")
            self.add_message("system", "🔊 TTS ACTIVADO")
        else:
            if hasattr(self, 'tts'):
                self.tts.stop()
                self.face.set_speaking(False)
            self.btn_tts.config(text="🔇 TTS: OFF", bg="#E74C3C")
            self.add_message("system", "🔇 TTS DESACTIVADO")

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

    def toggle_theme(self):
        self.tema_actual = (self.tema_actual + 1) % len(self.colores)
        self.aplicar_tema()
        self.add_message("system", f"{self.colores[self.tema_actual]['nombre']} ACTIVADO")

    def animar_escribiendo(self):
        """Animación de puntitos mientras escribe"""
        dots = [".  ", ".. ", "...", " ..", "  .", "   "]
        self.animacion_dots = (self.animacion_dots + 1) % len(dots)
        try:
            self.status_label.config(text=f">> LUNA ESTÁ ESCRIBIENDO{dots[self.animacion_dots]}")
            if self.ai_loaded and self.status_label.cget("text").startswith(">> LUNA"):
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

    def show_info(self):
        info = ("💪 IRON CHAT v2.0\n\n"
                "🤖 MODELO: Llama 3.2 3B\n"
                "🔊 TTS: Piper real + pyttsx3\n"
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
                    self.btn_music.config(text="🎵 MÚSICA ON", bg="#27AE60")
                    self.add_message("system", f"🎵 REPRODUCIENDO: {os.path.basename(mp3s[0])}")
                else:
                    self.music_playing = False
                    self.add_message("system", "⚠️ No hay musica en la carpeta 'musica/'")
                    self.btn_music.config(text="🎵 MÚSICA OFF", bg="#2C3E50")
            except Exception as e:
                self.music_playing = False
                self.add_message("system", f"❌ ERROR: {e}")
                self.btn_music.config(text="🎵 MÚSICA OFF", bg="#2C3E50")
        else:
            Audio.stop_music()
            self.btn_music.config(text="🎵 MÚSICA OFF", bg="#2C3E50")
            self.add_message("system", "🎵 MUSICA DESACTIVADA")

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
            self.root.after(0, lambda: self.on_ai_error(error_msg))

    def on_ai_loaded(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        if self.ai and getattr(self.ai, 'is_offline', False):
            self.status_label.config(text=">> MODO OFFLINE - RESPUESTAS LIMITADAS", fg="#FF6B35")
            self.add_message("system", "⚠️ MODO OFFLINE: El modelo de IA no está disponible.")
            self.add_message("system", "📥 Ejecuta install.bat o install.py para descargar el modelo.")
            self.add_message("system", "💬 Mientras tanto, LUNA responde con conocimientos básicos.")
            logging.info("Modelo en modo offline")
        else:
            self.status_label.config(text=">> MODELO CARGADO - LISTO!", fg="#27AE60")
            self.add_message("system", "✅ MODELO CARGADO! PUEDES EMPEZAR A CHATEAR.")
            logging.info("Modelo listo!")

    def on_ai_error(self, error):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_label.config(text=">> ERROR: " + error, fg="#E74C3C")
        self.add_message("system", "❌ ERROR AL CARGAR EL MODELO: " + error)
        logging.error(f"Error modelo: {error}")
        messagebox.showerror("ERROR", "NO SE PUDO CARGAR EL MODELO:\n" + error)

    def _get_conversation_context(self, max_exchanges=5):
        exchanges = []
        for msg in reversed(self.chat_history):
            msg = msg.strip()
            if msg.startswith("[") and "TÚ:" in msg:
                text = msg.split("TÚ:", 1)[1].strip()
                exchanges.append(("user", text))
            elif msg.startswith("[") and "IRON:" in msg:
                text = msg.split("IRON:", 1)[1].strip()
                exchanges.append(("assistant", text))
            if len(exchanges) >= max_exchanges * 2:
                break
        exchanges.reverse()
        return exchanges

    def add_message(self, sender, message):
        self.chat_area.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        if sender == "user":
            formatted = f"[{timestamp}] 🏋️ TÚ: {message}\n"
            tag = "user_msg"
        elif sender == "ai":
            formatted = f"[{timestamp}] 💪 IRON: {message}\n"
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
            stats = f"📊 ESTADISTICAS:\nMensajes: {self.mensajes_count}\nTTS: {'ON' if self.tts_enabled else 'OFF'}\nTema: {tema_nombre}\nModelo: {'CARGADO' if self.ai_loaded else 'CARGANDO'}"
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
            messagebox.showwarning("ESPERA", "EL MODELO AUN SE ESTA CARGANDO...")
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
        self.send_button.config(state=tk.DISABLED)
        try:
            Sounds.play_chat()
        except Exception:
            pass
        self.add_message("user", user_input)
        self.mensajes_count += 1
        self.actualizar_contador()
        self.status_label.config(text=">> LUNA ESTÁ ESCRIBIENDO...", fg="#FFD700")
        self.animar_escribiendo()
        threading.Thread(target=self.get_response, args=(user_input,), daemon=True).start()

    def get_response(self, user_input):
        try:
            self.root.after(0, lambda: self.status_label.config(text=">> PENSANDO...", fg="#3498DB"))
            history = self._get_conversation_context(5)
            response = self.ai.get_response(user_input, history=history)
            self.root.after(0, lambda r=response: self._on_response(r))
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error en get_response: {error_msg}")
            self.root.after(0, lambda: self.add_message("system", "❌ ERROR: " + error_msg))
            self.root.after(0, lambda: self.status_label.config(text=">> ERROR", fg="#E74C3C"))

    def _on_response(self, response):
        self.add_message("ai", response)
        Sounds.play_notification()
        self.speak_response(response)

    def _finish_sending(self):
        self._sending = False
        self.send_button.config(state=tk.NORMAL)

    def speak_response(self, response):
        texto_limpio = re.sub(r"[^\w\s,;:.!?¡¿áéíóúüñÁÉÍÓÚÜÑ]", " ", response)
        texto_limpio = re.sub(r"\s+", " ", texto_limpio).strip()
        if not self.tts_enabled:
            self.status_label.config(text=">> LISTO", fg="#27AE60")
            self._finish_sending()
            return
        self.face.set_speaking(True)
        self.status_label.config(text=">> HABLANDO...", fg="#FF6B35")
        self.tts.speak(texto_limpio if texto_limpio else response, on_finish=lambda: self.root.after(0, self.on_tts_finish))

    def on_tts_finish(self):
        self.face.set_speaking(False)
        self.status_label.config(text=">> LISTO", fg="#27AE60")
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
        entry = tk.Entry(dialog, font=("Consolas", 14), bg="#1a1a2e", fg="#ECF0F1", insertbackground="#ECF0F1", relief=tk.FLAT, width=10, justify=tk.CENTER)
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
        dialog.bind("<Return>", lambda e: start_custom())

    def timer_start(self, seconds):
        if self.timer_running:
            self.timer_stop()
        self.timer_running = True
        self.timer_remaining = seconds
        self.timer_label.config(text=f"⏱️ {seconds//60:02d}:{seconds%60:02d}")
        self.timer_tick()

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
        import time
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
            entry = tk.Entry(form, font=("Consolas", 10), bg="#1a1a2e", fg="#ECF0F1", insertbackground="#ECF0F1", relief=tk.FLAT, width=10)
            entry.grid(row=row, column=1, padx=10, pady=3)
            fields[key] = entry
            row += 1
        tk.Label(form, text="Notas", font=("Helvetica", 10), bg="#1a1a2e", fg="#ECF0F1").grid(row=row, column=0, sticky="w", pady=3)
        notes_entry = tk.Entry(form, font=("Consolas", 10), bg="#1a1a2e", fg="#ECF0F1", insertbackground="#ECF0F1", relief=tk.FLAT, width=10)
        notes_entry.grid(row=row, column=1, padx=10, pady=3)

        def save():
            vals = {}
            for key, entry in fields.items():
                v = entry.get().strip()
                vals[key] = float(v) if v else None
            self.progress.add_entry(**vals, notes=notes_entry.get().strip())
            self.add_message("system", "📊 MEDICIÓN GUARDADA!")
            dialog.destroy()

        btn_save = tk.Button(dialog, text="💾 GUARDAR", font=("Helvetica", 11, "bold"), bg="#27AE60", fg="white",
                            command=save, relief=tk.FLAT, width=20, bd=0)
        btn_save.pack(pady=15)

    def _view_progress(self, parent):
        entries = self.progress.get_entries()
        dialog = tk.Toplevel(parent)
        dialog.title("📈 HISTORIAL")
        dialog.geometry("650x450")
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)
        tk.Label(dialog, text="📈 HISTORIAL DE PROGRESO", font=("Helvetica", 12, "bold"), bg="#1a1a2e", fg="#FFD700").pack(pady=10)
        text_frame = tk.Frame(dialog, bg="#0d0d1a")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        text_area = tk.Text(text_frame, font=("Consolas", 10), bg="#0d0d1a", fg="#ECF0F1", wrap=tk.NONE, relief=tk.FLAT, bd=0)
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
                if pv is not None and v is not None and pv is not None:
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
        credits = (
            "╔════════════════════════════════╗\n"
            "║    IRON CHAT - LUNA v2.0       ║\n"
            "╠════════════════════════════════╣\n"
            "║ 👨\u200d💻 CREADOR: ⚡ JMbirner ⚡     ║\n"
            "║ 🤖 ASISTENTE: UOS AI           ║\n"
            "╠════════════════════════════════╣\n"
            "║ 🏋\ufe0f Fitness + Nutricion + IA   ║\n"
            "║ 🎨 ASCII Art + TTS + Animacion ║\n"
            "╠════════════════════════════════╣\n"
            "║  A100--80G--NVIDIA tesla Deep  ║\n"
            "║  CPU Intel corei7-14700k       ║\n"
            "║        ¡SIN AVX! 🐉🔥           ║\n"
            "╚════════════════════════════════╝"
        )
        messagebox.showinfo("🏆 CREDITOS", credits)

def main():
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
