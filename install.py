#!/usr/bin/env python3
# ============================================================
#  INSTALADOR DE IRON CHAT - LUNA v2.0 (Python)
#  Funciona en Windows y Linux
#  Creado por: ⚡ JMbirner ⚡
# ============================================================

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import platform

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def log(msg, ok=True):
    icon = "✅" if ok else "❌"
    print(f"  {icon} {msg}")

def section(title):
    print(f"\n{title}")

# ============================================================

def main():
    print("╔══════════════════════════════════════╗")
    print("║   INSTALADOR IRON CHAT - LUNA v2.0   ║")
    if platform.system() == "Windows":
        print("║   PARA WINDOWS                       ║")
    else:
        print("║   PARA LINUX                         ║")
    print("╚══════════════════════════════════════╝")
    print(f"\n📂 Directorio: {SCRIPT_DIR}")

    # === 1. VERIFICAR PYTHON (ya estamos en Python) ===
    section("🔍 Python")
    log(f"Python {sys.version.split()[0]}")

    # === 2. CREAR ENTORNO VIRTUAL ===
    section("🔧 Entorno virtual")
    venv_dir = os.path.join(SCRIPT_DIR, "venv")
    if not os.path.exists(venv_dir):
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        log("Entorno virtual creado")
    else:
        log("Entorno virtual ya existe")

    # === 3. INSTALAR DEPENDENCIAS ===
    section("📦 Dependencias Python")
    pip = os.path.join(venv_dir, "Scripts", "pip.exe") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "pip")

    subprocess.run([pip, "install", "--upgrade", "pip"], capture_output=True)

    print("  ⏳ Instalando llama-cpp-python...")
    subprocess.run([pip, "install", "llama-cpp-python"], capture_output=True)
    log("llama-cpp-python instalado")

    deps = ["pygame", "Pillow"]
    if platform.system() == "Windows":
        deps.append("pyttsx3")
    print(f"  ⏳ Instalando {', '.join(deps)}...")
    subprocess.run([pip, "install"] + deps, capture_output=True)
    log(f"{', '.join(deps)} instalados")

    # === 4. MODELO DE IA ===
    section("🤖 Modelo de IA")
    model_dir = os.path.join(SCRIPT_DIR, "models")
    model_path = os.path.join(model_dir, "Llama-3.2-3B-Instruct-Q4_0.gguf")
    os.makedirs(model_dir, exist_ok=True)

    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / (1024**3)
        log(f"Modelo ya existe: {size:.2f} GB")
    else:
        model_url = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_0.gguf"
        print("  ⏳ Descargando modelo (2 GB, puede tomar varios minutos)...")
        print("     No cierres esta ventana!")
        try:
            def report(block, block_size, total):
                if total > 0:
                    downloaded = block * block_size / (1024**3)
                    total_gb = total / (1024**3)
                    print(f"     {downloaded:.1f}/{total_gb:.1f} GB", end="\r")
            urllib.request.urlretrieve(model_url, model_path + ".tmp", reporthook=report)
            os.replace(model_path + ".tmp", model_path)
            size = os.path.getsize(model_path) / (1024**3)
            print(f"\r     ✅ Modelo descargado: {size:.2f} GB")
        except Exception as e:
            print(f"\r     ❌ Error: {e}")
            print("     ⚠️ Descárgalo manualmente desde:")
            print(f"        {model_url}")
            print(f"     ⚠️ Y colócalo en: {model_dir}")

    # === 5. VOZ PIPER ===
    section("🎤 Voz Piper")
    voices_dir = os.path.join(SCRIPT_DIR, "voices")
    voice_path = os.path.join(voices_dir, "es_ES-sharvard-medium.onnx")
    os.makedirs(voices_dir, exist_ok=True)

    if os.path.exists(voice_path):
        log("Voz Piper ya existe")
    else:
        voice_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
        voice_json_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json"
        print("  ⏳ Descargando voz (77 MB)...")
        try:
            urllib.request.urlretrieve(voice_url, voice_path)
            urllib.request.urlretrieve(voice_json_url, voice_path + ".json")
            log("Voz descargada: es_ES-sharvard-medium.onnx")
        except:
            log("No se pudo descargar la voz", False)
            print("     ⚠️ El TTS usará la voz del sistema")

    # === 6. MUSICA ===
    section("🎵 Música")
    music_dir = os.path.join(SCRIPT_DIR, "musica")
    os.makedirs(music_dir, exist_ok=True)
    log("Carpeta musica/ creada (mete tus MP3 ahí)")

    # === 7. ACCESO DIRECTO ===
    section("📌 Acceso directo")
    if platform.system() == "Windows":
        vbs_path = os.path.join(SCRIPT_DIR, "crear_acceso_windows.vbs")
        if os.path.exists(vbs_path):
            try:
                subprocess.run(["cscript", vbs_path], capture_output=True)
                log("Acceso directo creado en el escritorio")
            except:
                log("No se pudo crear acceso directo", False)
        else:
            log("No se pudo crear acceso directo", False)
    else:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        desktop_file = os.path.join(desktop, "IRON-CHAT-LUNA.desktop")
        python_path = os.path.join(venv_dir, "bin", "python3")
        icon_path = os.path.join(SCRIPT_DIR, "robot.jpeg")
        content = f"""[Desktop Entry]
Name=IRON CHAT - LUNA
Comment=Chatbot con IA - Entrenadora personal
Exec={python_path} {os.path.join(SCRIPT_DIR, "main.py")}
Icon={icon_path}
Path={SCRIPT_DIR}
Terminal=false
Type=Application
Categories=Utility;AI;
"""
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(desktop_file, 0o755)
        log("Acceso directo creado en el escritorio")

    # === RUN.BAT ===
    if platform.system() == "Windows":
        bat_path = os.path.join(SCRIPT_DIR, "run.bat")
        python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        with open(bat_path, "w") as f:
            f.write(f'@echo off\ncd /d "{SCRIPT_DIR}"\n"{python_path}" main.py\npause\n')
        log("run.bat creado")

    # === 8. RESUMEN ===
    print("\n╔══════════════════════════════════════╗")
    print("║   INSTALACIÓN COMPLETADA            ║")
    print("╚══════════════════════════════════════╝")
    print("\n  🚀 Ejecutar:")
    if platform.system() == "Windows":
        print("     Doble clic en 'IRON CHAT - LUNA' del escritorio")
        print("     O doble clic en 'run.bat'")
    else:
        print("     Doble clic en 'IRON CHAT - LUNA' del escritorio")
        print("     O en terminal:")
        print(f"        cd {SCRIPT_DIR}")
        print(f"        source venv/bin/activate")
        print(f"        python3 main.py")
    print("\n  ⚡ JMbirner ⚡\n")

    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
