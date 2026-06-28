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

    # Verificar carpetas protegidas en Windows
    if platform.system() == "Windows":
        protected = [os.path.expanduser("~\\Desktop"), os.path.expanduser("~\\Downloads"),
                     os.path.expanduser("~\\Documents"), os.path.expanduser("~\\OneDrive")]
        in_protected = any(SCRIPT_DIR.lower().startswith(p.lower()) for p in protected if os.path.exists(p))
        if in_protected:
            print("\n  ⚠️  ATENCIÓN: Estás instalando dentro de una carpeta protegida")
            print("     (Desktop, Downloads, etc.). Windows Defender puede BLOQUEAR")
            print("     la descarga del modelo y la creación del acceso directo.")
            print()
            print("  ✅ Recomendación: Mueve la carpeta a:")
            print("     C:\\IRON-CHAT-LUNA\\")
            print("     y ejecuta install.bat desde allí.")
            print()
            input("     Presiona Enter para continuar de todas formas...")
            print()

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
    def _pip_llama(args):
        return subprocess.run([pip] + args).returncode == 0

    def _check_vcredist():
        """Verifica si el runtime VC++ está instalado en Windows"""
        if platform.system() != "Windows":
            return True
        # Buscar vcruntime140.dll en rutas típicas
        for root in [os.environ.get("SystemRoot", "C:\\Windows"),
                     os.environ.get("WINDIR", "C:\\Windows")]:
            path = os.path.join(root, "System32", "vcruntime140.dll")
            if os.path.exists(path):
                return True
        # También buscar en el directorio del proyecto (extracción directa)
        if os.path.exists(os.path.join(SCRIPT_DIR, "vcruntime140.dll")):
            return True
        return False

    def _install_vcredist():
        """Descarga e instala el VC++ Redistributable"""
        url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
        tmp = os.path.join(SCRIPT_DIR, "vc_redist.x64.exe")
        print("     ⬇️ Descargando Microsoft Visual C++ Redistributable...")
        try:
            urllib.request.urlretrieve(url, tmp)
            # Paso 1: intentar instalación silenciosa
            print("     🛠️ Instalando...")
            result = subprocess.run([tmp, "/install", "/quiet", "/norestart"],
                                    timeout=120, capture_output=True)
            if result.returncode == 0:
                os.unlink(tmp)
                return _check_vcredist()
            # Paso 2: fallback con interfaz
            print("     ⚠️ Modo silencioso falló, intentando con interfaz...")
            result = subprocess.run([tmp, "/install", "/passive", "/norestart"],
                                    timeout=120)
            if result.returncode == 0:
                os.unlink(tmp)
                return _check_vcredist()
            # Paso 3: extraer DLL directo del instalador
            print("     ⚠️ Instalación falló, extrayendo DLL directamente...")
            extract_dir = os.path.join(SCRIPT_DIR, "vc_extract")
            os.makedirs(extract_dir, exist_ok=True)
            subprocess.run([tmp, "/extract", extract_dir], timeout=30,
                           capture_output=True)
            dll_path = _find_vcruntime(extract_dir)
            if dll_path:
                dest = os.path.join(SCRIPT_DIR, "vcruntime140.dll")
                shutil.copy2(dll_path, dest)
                print(f"     ✅ vcruntime140.dll extraído a: {dest}")
                # Agregar directorio actual al PATH del proceso
                os.environ["PATH"] = SCRIPT_DIR + os.pathsep + os.environ.get("PATH", "")
                shutil.rmtree(extract_dir, ignore_errors=True)
                os.unlink(tmp)
                return True
            shutil.rmtree(extract_dir, ignore_errors=True)
            os.unlink(tmp)
            return False
        except Exception as e:
            print(f"     ⚠️ Error con VC++: {e}")
            if os.path.exists(tmp):
                os.unlink(tmp)
            return False

    def _find_vcruntime(search_dir):
        """Busca vcruntime140.dll recursivamente en un directorio"""
        for root, dirs, files in os.walk(search_dir):
            for f in files:
                if f.lower() == "vcruntime140.dll":
                    return os.path.join(root, f)
            # También buscar .cab para extraer
            for f in files:
                if f.lower().endswith(".cab"):
                    cab = os.path.join(root, f)
                    cab_extract = os.path.join(search_dir, "cab_out")
                    os.makedirs(cab_extract, exist_ok=True)
                    try:
                        subprocess.run(["expand", "-R", cab, cab_extract],
                                       timeout=30, capture_output=True)
                        for r2, d2, f2 in os.walk(cab_extract):
                            for ff in f2:
                                if ff.lower() == "vcruntime140.dll":
                                    return os.path.join(r2, ff)
                    except Exception:
                        pass
        return None

    def _download_wheel_direct():
        """Descarga el .whl directamente desde abetlen.github.io"""
        py_ver = f"cp{sys.version_info.major}{sys.version_info.minor}"
        arch = platform.machine().lower()
        if arch in ("amd64", "x86_64"):
            arch = "win_amd64"
        elif arch == "arm64":
            arch = "win_arm64"
        else:
            arch = "win32"
        # Probar varias versiones de llama-cpp-python
        for ver in ["0.3.4", "0.3.3", "0.3.2", "0.3.1", "0.3.0",
                     "0.2.90", "0.2.89", "0.2.88"]:
            url = (f"https://abetlen.github.io/llama-cpp-python/whl/cpu/"
                   f"llama_cpp_python-{ver}-{py_ver}-{py_ver}-{arch}.whl")
            tmp = os.path.join(SCRIPT_DIR, f"llama_{ver}.whl")
            try:
                urllib.request.urlretrieve(url, tmp)
                if os.path.getsize(tmp) > 100000:
                    print(f"     ✅ Wheel {ver} descargado ({os.path.getsize(tmp)/(1024**2):.0f} MB)")
                    return tmp
                os.unlink(tmp)
            except Exception:
                if os.path.exists(tmp):
                    os.unlink(tmp)
        return None

    def _install_llama():
        print("  ⏳ Instalando llama-cpp-python...")

        if platform.system() == "Windows":
            # Paso 1: verificar VC++ Redistributable
            if not _check_vcredist():
                print("     ⚠️ Falta Microsoft Visual C++ Redistributable")
                if _install_vcredist():
                    print("     ✅ VC++ Redistributable instalado")
                else:
                    print("     ⚠️ No se pudo instalar automáticamente.")
                    print("     Descárgalo manualmente de:")
                    print("     https://aka.ms/vs/17/release/vc_redist.x64.exe")
                    input("     Presiona Enter después de instalarlo...")

            # Paso 2: instalar solo con wheels (NUNCA compilar)
            print("     Buscando wheel pre-compilado en PyPI...")
            if _pip_llama(["install", "llama-cpp-python", "--only-binary", ":all:"]):
                return True
            print("     Buscando en abetlen.github.io...")
            if _pip_llama(["install", "llama-cpp-python", "--only-binary", ":all:",
                           "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cpu"]):
                return True
            # Paso 3: descargar el .whl directamente
            print("     Descargando wheel directamente...")
            whl = _download_wheel_direct()
            if whl:
                if _pip_llama(["install", whl]):
                    os.unlink(whl)
                    return True
                try:
                    os.unlink(whl)
                except Exception:
                    pass
            return False

        # Linux: puede compilar si no hay wheel
        if _pip_llama(["install", "llama-cpp-python", "--prefer-binary"]):
            return True
        print("  ⚠️ Reintentando con --no-cache-dir...")
        if _pip_llama(["install", "--no-cache-dir", "--prefer-binary", "llama-cpp-python"]):
            return True
        return False

    result_ok = _install_llama()

    if result_ok:
        log("llama-cpp-python instalado")
        if not verify_import(venv_dir, "llama_cpp"):
            log("No se pudo importar. Forzando reinstall...", False)
            _pip_llama(["install", "--force-reinstall", "--no-cache-dir", "llama-cpp-python"])
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
        py_ver = f"cp{sys.version_info.major}{sys.version_info.minor}"
        arch = platform.machine().lower()
        if arch in ("amd64", "x86_64"):
            arch = "win_amd64"
        elif arch == "arm64":
            arch = "win_arm64"
        else:
            arch = "win32"

        print("\n  ❌ FALLO CRÍTICO: llama-cpp-python no se instaló correctamente.")
        print("  =" * 30)
        print()
        print("  🔧 Esto suele pasar por UNA de estas razones:")
        print()
        print("  1️⃣  Falta el Microsoft Visual C++ Redistributable")
        print("      Descárgalo e instálalo desde:")
        print("      https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("      (solo el runtime, NO necesitas Build Tools)")
        print()
        print("  2️⃣  No hay wheel pre-compilado para tu Python")
        print(f"      Python: {py_ver}, arquitectura: {arch}")
        print("      Prueba a instalar manualmente:")
        wheel_url = (f"https://abetlen.github.io/llama-cpp-python/whl/cpu/"
                     f"llama_cpp_python-0.3.4-{py_ver}-{py_ver}-{arch}.whl")
        print(f"      {pip} install {wheel_url}")
        print()
        print("  3️⃣  Error de conexión")
        print("      Asegúrate de tener internet y vuelve a intentar.")
        print()
        input("\nPresiona Enter para salir...")
        sys.exit(1)

    # === 4. MODELO DE IA ===
    section("🤖 Modelo de IA")
    model_dir = os.path.join(SCRIPT_DIR, "models")
    os.makedirs(model_dir, exist_ok=True)

    # Detectar si ya existe algún modelo
    modelos_existentes = [f for f in os.listdir(model_dir) if f.endswith(".gguf") and os.path.getsize(os.path.join(model_dir, f)) > 1000000]
    if modelos_existentes:
        model_name = modelos_existentes[0]
        model_path = os.path.join(model_dir, model_name)
        size = os.path.getsize(model_path) / (1024**3)
        log(f"Modelo ya existe: {model_name} ({size:.2f} GB)")
        if size < 1.0:
            print("     ⚠️ El archivo parece muy pequeño, puede estar corrupto.")
            print("     Elimínalo y vuelve a ejecutar el instalador.")
    else:
        # Elegir modelo
        print("     Modelos disponibles:")
        print("     1) Qwen 2.5 3B Instruct (RECOMENDADO — Apache 2.0, mejor español)")
        print("     2) Llama 3.2 3B Instruct (Meta, requiere aceptar licencia)")
        choice = input("     Selecciona [1/2] (default 1): ").strip()
        if choice == "2":
            model_name = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
            model_url = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
            print("     ℹ️ Llama 3.2 requiere aceptar licencia de Meta en huggingface.co")
        else:
            model_name = "qwen2.5-3b-instruct-q4_k_m.gguf"
            model_url = "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"

        model_path = os.path.join(model_dir, model_name)
        print(f"  ⏳ Descargando {model_name} (2 GB, puede tomar varios minutos)...")
        print("     ⚠️  NO CIERRES ESTA VENTANA hasta que termine!")
        print()

        if not download_model_auto(model_url, model_path):
            print()
            print("  ╔══════════════════════════════════════════════╗")
            print("  ║   DESCARGA MANUAL REQUERIDA                ║")
            print("  ╚══════════════════════════════════════════════╝")
            print()
            print("  🔷 Opción recomendada (más rápida):")
            print()
            print("     1. Presiona Ctrl+C y pega este enlace en tu navegador:")
            print(f"        {model_url}")
            print()
            print()
            print("     2. Espera a que descargue (~2 GB)")
            print()
            print(f"     3. Copia el archivo AQUÍ:")
            print(f"        {model_dir}")
            print(f"        NOMBRE EXACTO: {model_name}")
            print()
            print(f"     4. Luego ejecuta install.bat OTRA VEZ")
            print()
            print("  🔷 O intenta descargar con este comando en PowerShell (como Administrador):")
            print()
            print(f'        curl -L "{model_url}" -o "{model_path}"')
            print()
            input("     Presiona Enter cuando hayas puesto el modelo...")
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
        if not os.path.exists(desktop):
            desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")

        # Método 1: crear .bat directamente desde Python (más fiable)
        bat_desktop = os.path.join(desktop, "IRON CHAT - LUNA.bat")
        try:
            with open(bat_desktop, "w") as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{SCRIPT_DIR}"\n')
                f.write(f'"%CD%\\venv\\Scripts\\python.exe" main.py\n')
                f.write('pause\n')
            if os.path.exists(bat_desktop):
                log("Acceso directo creado (.bat en escritorio)")
                shortcut_ok = True
        except Exception as e:
            log(f".bat falló: {e}", False)

        # Método 2: VBS (si no está bloqueado por Windows)
        if not shortcut_ok:
            try:
                vbs_path = os.path.join(SCRIPT_DIR, "crear_acceso_windows.vbs")
                if os.path.exists(vbs_path):
                    result = subprocess.run(["cscript", "//nologo", vbs_path],
                                            cwd=SCRIPT_DIR, capture_output=True, timeout=30)
                    if result.returncode == 0:
                        log("Acceso directo creado (VBS)")
                        shortcut_ok = True
            except Exception as e:
                log(f"VBS falló: {e}", False)

        if not shortcut_ok:
            print("     ⚠️ No se pudo crear acceso directo automáticamente.")
            print(f"     Para crearlo manualmente:")
            print(f"       1. Abre la carpeta: {SCRIPT_DIR}")
            print(f"       2. Clic derecho en 'iron-chat.bat'")
            print(f"       3. → Enviar a → Escritorio")
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
