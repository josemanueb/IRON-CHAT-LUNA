#!/usr/bin/env python3
# ============================================================
#  INSTALADOR DE IRON CHAT - LUNA v2.0 (Python)
#  Funciona en Windows y Linux
#  Muestra todo el output de pip para detectar errores
#  Creado por: ⚡ JMbirner ⚡
# ============================================================

import os
import sys
import subprocess
import urllib.request
import platform

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def log(msg, ok=True):
    icon = "✅" if ok else "❌"
    print(f"  {icon} {msg}")

def section(title):
    print(f"\n{title}")

def pip_install(pip, packages, label=None):
    if isinstance(packages, str):
        packages = [packages]
    label = label or packages[0]
    print(f"  ⏳ Instalando {label}...")
    result = subprocess.run([pip, "install"] + packages)
    if result.returncode == 0:
        log(f"{label} instalado")
        return True
    else:
        log(f"Error instalando {label}", False)
        return False

def verify_import(venv_dir, module_name):
    python_exe = os.path.join(venv_dir, "Scripts", "python.exe") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "python")
    result = subprocess.run([python_exe, "-c", f"import {module_name}; print('OK')"], capture_output=True, text=True)
    return result.returncode == 0

# ============================================================

def main():
    fatal_error = False

    print("╔══════════════════════════════════════╗")
    print("║   INSTALADOR IRON CHAT - LUNA v2.0   ║")
    if platform.system() == "Windows":
        print("║   PARA WINDOWS                       ║")
    else:
        print("║   PARA LINUX                         ║")
    print("╚══════════════════════════════════════╝")
    print(f"\n📂 Directorio: {SCRIPT_DIR}")

    # === 1. PYTHON ===
    section("🔍 Python")
    log(f"Python {sys.version.split()[0]}")

    # === 2. ENTORNO VIRTUAL ===
    section("🔧 Entorno virtual")
    venv_dir = os.path.join(SCRIPT_DIR, "venv")
    if not os.path.exists(venv_dir):
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        log("Entorno virtual creado")
    else:
        log("Entorno virtual ya existe")

    # === 3. DEPENDENCIAS ===
    section("📦 Dependencias Python")
    pip = os.path.join(venv_dir, "Scripts", "pip.exe") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "pip")

    subprocess.run([pip, "install", "--upgrade", "pip"])

    # 3a. llama-cpp-python (CRITICO) - con reintento
    print("  ⏳ Instalando llama-cpp-python...")
    result = subprocess.run([pip, "install", "llama-cpp-python"])
    if result.returncode != 0:
        print("  ⚠️ Reintentando con --no-cache-dir...")
        result = subprocess.run([pip, "install", "--no-cache-dir", "llama-cpp-python"])
    if result.returncode == 0:
        log("llama-cpp-python instalado")
        if not verify_import(venv_dir, "llama_cpp"):
            log("llama-cpp-python no se pudo importar. Reintentando...", False)
            result = subprocess.run([pip, "install", "--force-reinstall", "--no-cache-dir", "llama-cpp-python"])
    else:
        log("Error CRITICO: no se pudo instalar llama-cpp-python", False)
        fatal_error = True

    # 3b. Otras dependencias
    deps = ["Pillow"]
    if platform.system() == "Windows":
        deps.append("pyttsx3")
    else:
        deps.append("pygame")
    if not pip_install(pip, deps, ", ".join(deps)):
        print("  ⚠️ Error instalando dependencias secundarias.")
        print("     Puedes instalarlas manualmente después.")

    # 3c. Verificar que lo crítico se pueda importar
    if not fatal_error:
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "python")
        test = subprocess.run([python_exe, "-c", "import llama_cpp; print('✅ llama_cpp importado OK')"], capture_output=True, text=True)
        if test.returncode == 0:
            print(f"     {test.stdout.strip()}")
        else:
            txt = (test.stderr or "").split("\n")[-1].strip()
            log(f"Error importando llama_cpp: {txt}", False)
            fatal_error = True

    # 3d. Resumen de dependencias
    if fatal_error:
        print("\n  ❌ FALLO CRÍTICO: llama-cpp-python no se instaló correctamente.")
        print("  🔧 Posibles soluciones:")
        print("     1. Asegúrate de tener Microsoft Visual C++ Redistributable:")
        print("        https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("     2. Prueba instalarlo manualmente:")
        print(f"        {pip} install llama-cpp-python")
        print("     3. Si sigue fallando, descarga el .whl desde:")
        print("        https://github.com/abetlen/llama-cpp-python/releases")
        print()
        input("\nPresiona Enter para salir...")
        sys.exit(1)

    # === 4. MODELO DE IA ===
    section("🤖 Modelo de IA")
    model_dir = os.path.join(SCRIPT_DIR, "models")
    model_path = os.path.join(model_dir, "Llama-3.2-3B-Instruct-Q4_0.gguf")
    os.makedirs(model_dir, exist_ok=True)

    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / (1024**3)
        log(f"Modelo ya existe: {size:.2f} GB")
        if size < 1.0:
            print("     ⚠️ El archivo parece muy pequeño, puede estar corrupto.")
            print("     Elimínalo y vuelve a ejecutar el instalador.")
    else:
        model_url = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_0.gguf"
        print("  ⏳ Descargando modelo (2 GB, puede tomar varios minutos)...")
        print("     ⚠️  NO CIERRES ESTA VENTANA hasta que termine!")
        print("     Si la descarga falla, te daré instrucciones.")
        print()
        try:
            from urllib.request import urlretrieve
            import socket
            socket.setdefaulttimeout(1800)  # 30 minutos
            def report(block, block_size, total):
                if total > 0:
                    downloaded = block * block_size / (1024**3)
                    total_gb = total / (1024**3)
                    pct = min(100, int(downloaded / total_gb * 100))
                    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
                    print(f"     [{bar}] {downloaded:.1f}/{total_gb:.1f} GB ({pct}%)", end="\r")
            urlretrieve(model_url, model_path + ".tmp", reporthook=report)
            os.replace(model_path + ".tmp", model_path)
            size = os.path.getsize(model_path) / (1024**3)
            print(f"\r     ✅ Modelo descargado: {size:.2f} GB".ljust(70))
        except Exception as e:
            print(f"\r     ❌ Error descargando modelo: {e}".ljust(70))
            print()
            print("  ╔══════════════════════════════════════════════╗")
            print("  ║   DESCARGA MANUAL REQUERIDA                ║")
            print("  ╚══════════════════════════════════════════════╝")
            print()
            print("  1. Abre este enlace en tu navegador:")
            print(f"     {model_url}")
            print()
            print("  2. Espera a que descargue (~2 GB)")
            print()
            print(f"  3. Copia el archivo descargado AQUÍ:")
            print(f"     {model_dir}")
            print(f"     El nombre debe ser: Llama-3.2-3B-Instruct-Q4_0.gguf")
            print()
            print("  4. Una vez colocado, ejecuta install.bat otra vez")
            print()
            input("     Presiona Enter cuando hayas colocado el modelo...")
            # Re-verificar
            if os.path.exists(model_path):
                size = os.path.getsize(model_path) / (1024**3)
                if size > 1.0:
                    log(f"Modelo encontrado: {size:.2f} GB")
                else:
                    log("El archivo parece corrupto (muy pequeño)", False)
                    input("Presiona Enter para continuar...")
            else:
                log("Modelo no encontrado. Puedes continuar sin IA", False)
                input("Presiona Enter para continuar...")

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
        try:
            import win32com.client
            ws = win32com.client.Dispatch("WScript.Shell")
            desktop = ws.SpecialFolders("Desktop")
            link_path = os.path.join(desktop, "IRON CHAT - LUNA.lnk")
            shortcut = ws.CreateShortcut(link_path)
            shortcut.TargetPath = os.path.join(SCRIPT_DIR, "iron-chat.bat")
            shortcut.WorkingDirectory = SCRIPT_DIR
            shortcut.Description = "Chatbot Inteligente con LUNA - Entrenadora Personal"
            icon_path = os.path.join(SCRIPT_DIR, "robot-icon.ico")
            if os.path.exists(icon_path):
                shortcut.IconLocation = icon_path
            shortcut.Save()
            log("Acceso directo creado en el escritorio")
        except Exception as e:
            log(f"No se pudo crear acceso directo: {e}", False)
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
        with open(bat_path, "w") as f:
            f.write('@echo off\ncd /d "%~dp0"\ncall venv\\Scripts\\activate.bat\npython main.py\npause\n')
        log("run.bat creado")

    # === 8. RESUMEN ===
    print("\n╔══════════════════════════════════════╗")
    print("║   INSTALACIÓN COMPLETADA            ║")
    print("╚══════════════════════════════════════╝")
    print("\n  🚀 Ejecutar:")
    if platform.system() == "Windows":
        print("     - Doble clic en 'IRON CHAT - LUNA' del escritorio")
        print("     - O doble clic en 'run.bat'")
        print("     - O doble clic en 'iron-chat.bat'")
    else:
        print("     - Doble clic en 'IRON CHAT - LUNA' del escritorio")
        print("     - O en terminal:")
        print(f"        cd {SCRIPT_DIR}")
        print(f"        source venv/bin/activate")
        print(f"        python3 main.py")
    print("\n  ⚡ JMbirner ⚡\n")

    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
