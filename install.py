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
import shutil

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

def _download_chunked(url, dest, verified=True, timeout=120):
    """Descarga por chunks con resume, timeout por chunk, y SSL configurable"""
    import ssl
    import urllib.request
    import socket

    tmp = dest + ".tmp"
    ctx = ssl.create_default_context() if verified else ssl._create_unverified_context()
    resume_bytes = 0
    total = 0

    if os.path.exists(tmp):
        resume_bytes = os.path.getsize(tmp)
        if resume_bytes > 0:
            print(f"     🔄 Reanudando desde {resume_bytes/(1024**3):.2f} GB...")

    CHUNK = 1024 * 1024
    max_retries = 5
    attempt = 0

    while attempt <= max_retries:
        try:
            req = urllib.request.Request(url)
            if resume_bytes > 0:
                req.add_header("Range", f"bytes={resume_bytes}-")

            resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
            status = resp.status

            # Si el servidor ignoró el Range (200 en vez de 206), empezar de cero
            if resume_bytes > 0 and status != 206:
                resume_bytes = 0
                tmp = dest + ".tmp"

            cl = resp.headers.get("Content-Length")
            remaining = int(cl) if cl else 0

            if status == 206:
                total = remaining + resume_bytes
            else:
                total = remaining

            total_gb = total / (1024**3)
            mode = "wb" if resume_bytes == 0 else "ab"

            with open(tmp, mode) as f:
                while True:
                    try:
                        chunk = resp.read(CHUNK)
                        if not chunk:
                            break
                        f.write(chunk)
                        resume_bytes += len(chunk)
                        downloaded_gb = resume_bytes / (1024**3)
                        if total > 0:
                            pct = min(100, int(resume_bytes / total * 100))
                            bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
                            print(f"     [{bar}] {downloaded_gb:.1f}/{total_gb:.1f} GB ({pct}%)", end="\r")
                        else:
                            print(f"     Descargados {downloaded_gb:.1f} GB...", end="\r")
                    except socket.timeout:
                        print(f"\n     ⚠️  Timeout en chunk, reintentando... ({attempt+1}/{max_retries})")
                        attempt += 1
                        break
                    except Exception:
                        print(f"\n     ⚠️  Error en chunk, reintentando... ({attempt+1}/{max_retries})")
                        attempt += 1
                        break
                else:
                    if resume_bytes >= total or total == 0:
                        os.replace(tmp, dest)
                        return True
                    continue
        except urllib.request.HTTPError as e:
            if e.code == 416 and resume_bytes > 0:
                os.replace(tmp, dest)
                return True
            return False
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                return False
    return False

def _download_urllib(url, dest, verified=True):
    """Descarga con urllib usando chunked download con resume"""
    try:
        return _download_chunked(url, dest, verified=verified, timeout=120)
    except Exception:
        return False

def _ps_check(result, tmp, dest):
    """Verifica código de retorno + archivo > 1 MB y renombra"""
    if result.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 1024 * 1024:
        os.replace(tmp, dest)
        return True
    if os.path.exists(tmp):
        sz = os.path.getsize(tmp) / (1024**3)
        print(f"     ⚠️  PowerShell terminó con código {result.returncode}, parcial: {sz:.2f} GB")
    return False

def download_with_powershell(url, dest):
    """Descarga usando PowerShell WebClient"""
    try:
        tmp = dest + ".tmp"
        result = subprocess.run([
            'powershell', '-NoProfile', '-Command',
            f'$wc = New-Object System.Net.WebClient; $wc.DownloadFile("{url}", "{tmp}")'
        ], capture_output=True, text=True, timeout=7200)
        return _ps_check(result, tmp, dest)
    except Exception as e:
        print(f"     ⚠️  PowerShell falló: {e}")
        return False

def download_with_powershell_ssl_fallback(url, dest):
    """Descarga con PowerShell ignorando errores SSL"""
    try:
        tmp = dest + ".tmp"
        script = (
            '[Net.ServicePointManager]::SecurityProtocol = '
            '[Net.SecurityProtocolType]::Tls12; '
            '[System.Net.ServicePointManager]::'
            'ServerCertificateValidationCallback = {$true}; '
            f'$wc = New-Object System.Net.WebClient; '
            f'$wc.DownloadFile("{url}", "{tmp}")'
        )
        result = subprocess.run(['powershell', '-NoProfile', '-Command', script],
                                capture_output=True, text=True, timeout=7200)
        return _ps_check(result, tmp, dest)
    except Exception as e:
        print(f"     ⚠️  PowerShell SSL falló: {e}")
        return False

def download_with_bits(url, dest):
    """Descarga usando BITS (Background Intelligent Transfer Service)"""
    try:
        tmp = dest + ".tmp"
        result = subprocess.run([
            'powershell', '-NoProfile', '-Command',
            f'Start-BitsTransfer -Source "{url}" -Destination "{tmp}" -Priority High'
        ], capture_output=True, text=True, timeout=7200)
        return _ps_check(result, tmp, dest)
    except Exception as e:
        print(f"     ⚠️  BITS falló: {e}")
        return False

def download_model_auto(url, dest, label="Modelo"):
    """Intenta descargar con múltiples métodos y resume automático"""
    tmp = dest + ".tmp"
    if os.path.exists(tmp) and os.path.getsize(tmp) < 1024 * 1024:
        os.remove(tmp)

    if platform.system() == "Windows":
        methods = [
            ("PowerShell WebClient", lambda: download_with_powershell(url, dest)),
            ("PowerShell (sin verificar SSL)", lambda: download_with_powershell_ssl_fallback(url, dest)),
            ("BITS (Background Transfer)", lambda: download_with_bits(url, dest)),
            ("urllib (SSL verificado)", lambda: _download_urllib(url, dest, verified=True)),
            ("urllib (SSL no verificado)", lambda: _download_urllib(url, dest, verified=False)),
        ]
    else:
        methods = [
            ("urllib (SSL verificado + resume)", lambda: _download_urllib(url, dest, verified=True)),
            ("urllib (SSL no verificado + resume)", lambda: _download_urllib(url, dest, verified=False)),
        ]

    for name, method in methods:
        print(f"     🔄 Intentando: {name}...")
        try:
            if method():
                if os.path.exists(dest) and os.path.getsize(dest) >= (1024**3):
                    size = os.path.getsize(dest) / (1024**3)
                    print(f"\r     ✅ {label} descargado: {size:.2f} GB".ljust(70))
                    return True
                elif os.path.exists(dest) and os.path.getsize(dest) > 0:
                    log(f"{label} descargado pero parece pequeño ({os.path.getsize(dest)/(1024**3):.2f} GB)", False)
        except Exception as e:
            print(f"     ⚠️  Falló: {e}")

    # Si llegamos aquí y hay un .tmp, renombrar por si sirve
    if os.path.exists(tmp) and not os.path.exists(dest):
        shutil.move(tmp, dest)
        size = os.path.getsize(dest) / (1024**3)
        if size >= 1.0:
            log(f"{label} recuperado desde descarga parcial: {size:.2f} GB")
            return True
    return False

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
        deps.extend(["pyttsx3", "pywin32"])
    else:
        deps.extend(["pygame", "piper-tts"])
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
        print()

        if not download_model_auto(model_url, model_path):
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
            if os.path.exists(model_path):
                size = os.path.getsize(model_path) / (1024**3)
                if size >= 1.0:
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

        voice_ok = False

        for url, dest, label in [
            (voice_url, voice_path, "Voz"),
            (voice_json_url, voice_path + ".json", "Config")
        ]:
            ok = (_download_urllib(url, dest, verified=True) or
                  _download_urllib(url, dest, verified=False) or
                  download_with_powershell(url, dest) or
                  download_with_powershell_ssl_fallback(url, dest) or
                  download_with_bits(url, dest))
            if ok:
                log(f"{label} descargada")
                voice_ok = True
            else:
                log(f"No se pudo descargar {label}", False)

        if not voice_ok:
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
        shortcut_ok = False
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        link_path = os.path.join(desktop, "IRON CHAT - LUNA.lnk")

        # Método 1: VBS (no necesita pywin32, funciona siempre)
        try:
            vbs_path = os.path.join(SCRIPT_DIR, "crear_acceso_windows.vbs")
            if os.path.exists(vbs_path):
                result = subprocess.run(["cscript", "//nologo", vbs_path],
                                        cwd=SCRIPT_DIR, capture_output=True, timeout=30)
                if result.returncode == 0 and os.path.exists(link_path):
                    log("Acceso directo creado (VBS)")
                    shortcut_ok = True
        except Exception as e:
            log(f"VBS falló: {e}", False)

        # Método 2: PowerShell COM
        if not shortcut_ok:
            try:
                ps_script = f'''
$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$link = "$desktop\\IRON CHAT - LUNA.lnk"
$sc = $ws.CreateShortcut($link)
$sc.TargetPath = "{os.path.join(SCRIPT_DIR, 'iron-chat.bat')}"
$sc.WorkingDirectory = "{SCRIPT_DIR}"
$sc.Description = "Chatbot Inteligente con LUNA - Entrenadora Personal"
$icon = "{os.path.join(SCRIPT_DIR, 'robot-icon.ico')}"
if (Test-Path $icon) {{ $sc.IconLocation = "$icon, 0" }}
$sc.Save()
'''
                subprocess.run(['powershell', '-NoProfile', '-Command', ps_script],
                               check=True, capture_output=True, timeout=30)
                if os.path.exists(link_path):
                    log("Acceso directo creado (PowerShell COM)")
                    shortcut_ok = True
            except Exception as e:
                log(f"PowerShell COM falló: {e}", False)

        # Método 3: Copia de .bat al escritorio
        if not shortcut_ok:
            for fname in ["iron-chat.bat", "run.bat"]:
                src = os.path.join(SCRIPT_DIR, fname)
                if os.path.exists(src):
                    try:
                        shutil.copy2(src, os.path.join(desktop, "IRON CHAT - LUNA.bat"))
                        log("Acceso directo creado (copia .bat en escritorio)")
                        shortcut_ok = True
                        break
                    except:
                        pass

        if not shortcut_ok:
            log("Crea el acceso manual: clic derecho en iron-chat.bat → Enviar a Escritorio", False)
    else:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop):
            alt = os.path.join(os.path.expanduser("~"), "Escritorio")
            if os.path.exists(alt):
                desktop = alt
        os.makedirs(desktop, exist_ok=True)
        desktop_file = os.path.join(desktop, "IRON-CHAT-LUNA.desktop")
        python_path = os.path.join(venv_dir, "bin", "python3")
        icon_path = os.path.join(SCRIPT_DIR, "robot-icon.png")
        if not os.path.exists(icon_path):
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
        apps_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
        os.makedirs(apps_dir, exist_ok=True)
        shutil.copy2(desktop_file, os.path.join(apps_dir, "IRON-CHAT-LUNA.desktop"))
        log("Acceso directo registrado en aplicaciones")

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
        print("     - Menú de aplicaciones → IRON CHAT - LUNA")
        print("     - O doble clic en el icono del escritorio")
        print("     - O en terminal:")
        print(f"        cd {SCRIPT_DIR}")
        print(f"        source venv/bin/activate")
        print(f"        python3 main.py")
    print("\n  ⚡ JMbirner ⚡\n")

    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
