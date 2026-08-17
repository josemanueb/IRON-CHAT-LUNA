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
import tempfile

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
                completed = False
                while True:
                    try:
                        chunk = resp.read(CHUNK)
                        if not chunk:
                            completed = True
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
            if completed and (resume_bytes >= total or total == 0):
                os.replace(tmp, dest)
                return True
        except urllib.request.HTTPError as e:
            if e.code == 416 and resume_bytes > 0:
                # 416 = el rango ya no aplica: la descarga ya está completa
                try:
                    if os.path.exists(dest):
                        os.remove(dest)
                    os.replace(tmp, dest)
                except OSError:
                    try:
                        shutil.move(tmp, dest)
                    except OSError:
                        return False
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
        try:
            os.replace(tmp, dest)
            return True
        except OSError as e:
            print(f"     ⚠️  Error al renombrar: {e}")
            return False
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
                min_size = 100 * 1024 * 1024
                if os.path.exists(dest) and os.path.getsize(dest) >= min_size:
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
            print("     y ejecuta install_windows.ps1 desde allí.")
            print()
            input("     Presiona Enter para continuar de todas formas...")
            print()

    # === 1. PYTHON ===
    section("🔍 Python")
    log(f"Python {sys.version.split()[0]}")

    # === 2. ENTORNO VIRTUAL ===
    section("🔧 Entorno virtual")
    venv_dir = os.path.join(SCRIPT_DIR, "venv")
    venv_py = os.path.join(venv_dir, "Scripts", "python.exe") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "python")
    # En Windows preferir el Python portable 3.12.5 para crear el venv
    base_python = sys.executable
    if platform.system() == "Windows":
        portable_py = os.path.join(SCRIPT_DIR, "portable_python", "python.exe")
        if os.path.exists(portable_py):
            base_python = portable_py
    if os.path.exists(venv_py):
        # Si el venv ya existe, comprobar su version de Python (debe ser 3.12.x)
        try:
            r = subprocess.run([venv_py, "-c", "import sys; print(sys.version_info[:2])"],
                               capture_output=True, text=True, timeout=30)
            ver = r.stdout.strip()
            if ver != "(3, 12)":
                log(f"El venv usa Python {ver}, se requiere 3.12. Recreando...", False)
                shutil.rmtree(venv_dir, ignore_errors=True)
            else:
                log("Entorno virtual ya existe")
        except Exception:
            log("No se pudo verificar la version del venv. Recreando...", False)
            shutil.rmtree(venv_dir, ignore_errors=True)
    if not os.path.exists(venv_dir):
        subprocess.run([base_python, "-m", "venv", venv_dir], check=True)
        log("Entorno virtual creado")

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
        # Buscar vcruntime140.dll y vcruntime140_1.dll (ambos los necesita llama-cpp)
        for root in [os.environ.get("SystemRoot", "C:\\Windows"),
                     os.environ.get("WINDIR", "C:\\Windows")]:
            sys32 = os.path.join(root, "System32")
            if os.path.exists(os.path.join(sys32, "vcruntime140.dll")) and \
               os.path.exists(os.path.join(sys32, "vcruntime140_1.dll")):
                return True
        # También buscar en el directorio del proyecto (extracción directa)
        if os.path.exists(os.path.join(SCRIPT_DIR, "vcruntime140.dll")) and \
           os.path.exists(os.path.join(SCRIPT_DIR, "vcruntime140_1.dll")):
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
            # 3010 = OK, requiere reinicio; 1638 = ya hay versión más nueva
            print("     🛠️ Instalando...")
            result = subprocess.run([tmp, "/install", "/quiet", "/norestart"],
                                    timeout=120, capture_output=True)
            if result.returncode in (0, 3010, 1638):
                os.unlink(tmp)
                return _check_vcredist()
            # Paso 2: fallback con interfaz
            print("     ⚠️ Modo silencioso falló, intentando con interfaz...")
            result = subprocess.run([tmp, "/install", "/passive", "/norestart"],
                                    timeout=120)
            if result.returncode in (0, 3010, 1638):
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
                dll1_path = _find_vcruntime1(extract_dir)
                if dll1_path:
                    dest1 = os.path.join(SCRIPT_DIR, "vcruntime140_1.dll")
                    shutil.copy2(dll1_path, dest1)
                    print(f"     ✅ vcruntime140_1.dll extraído a: {dest1}")
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

    def _find_vcruntime1(search_dir):
        """Busca vcruntime140_1.dll recursivamente en un directorio"""
        for root, dirs, files in os.walk(search_dir):
            for f in files:
                if f.lower() == "vcruntime140_1.dll":
                    return os.path.join(root, f)
        return None

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

    def _cpu_has_avx2():
        """Detecta soporte AVX2 de la CPU (necesario para los wheels precompilados)."""
        try:
            import ctypes
            if platform.system() == "Windows":
                libc = ctypes.windll.kernel32
                # PF_AVX2_INSTRUCTIONS_AVAILABLE = 40
                return bool(libc.GetIsProcessorFeaturePresent(40))
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("flags") and "avx2" in line:
                        return True
            return False
        except Exception:
            return False

    def _install_w64devkit():
        """Descarga y extrae w64devkit (toolchain MinGW portable) para compilar sin AVX."""
        tool_ver = "2.8.0"
        tool_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "w64devkit")
        # El archivo extrae dentro de una subcarpeta w64devkit\w64devkit\bin; buscar recursivo
        existing = None
        for root, dirs, files in os.walk(tool_dir):
            if os.path.exists(os.path.join(root, "bin", "gcc.exe")):
                existing = root
                break
        if existing:
            return existing
        exe = os.path.join(tempfile.gettempdir(), f"w64devkit-x64-{tool_ver}.7z.exe")
        url = (f"https://github.com/skeeto/w64devkit/releases/download/"
               f"v{tool_ver}/w64devkit-x64-{tool_ver}.7z.exe")
        print(f"     ⬇️ Descargando w64devkit {tool_ver} (compilador portable)...")
        try:
            urllib.request.urlretrieve(url, exe)
            os.makedirs(tool_dir, exist_ok=True)
            print("     🛠️ Extrayendo...")
            subprocess.run([exe, "-y", f"-o{tool_dir}"], timeout=120, capture_output=True)
            os.unlink(exe)
        except Exception as e:
            print(f"     ⚠️ Error con w64devkit: {e}")
            if os.path.exists(exe):
                os.unlink(exe)
            return None
        for root, dirs, files in os.walk(tool_dir):
            if os.path.exists(os.path.join(root, "bin", "gcc.exe")):
                return root
        return None

    def _build_llama_no_avx():
        """Compila llama-cpp-python desde fuente SIN AVX (para CPUs antiguas)."""
        tool_dir = _install_w64devkit()
        if not tool_dir:
            print("     ⚠️ No se pudo obtener el toolchain de compilacion.")
            return False
        bin_dir = os.path.join(tool_dir, "bin")
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        gcc_exe = os.path.join(bin_dir, "gcc.exe")
        gpp_exe = os.path.join(bin_dir, "g++.exe")
        gcc_for_cmake = gcc_exe.replace("\\", "/")
        gpp_for_cmake = gpp_exe.replace("\\", "/")
        # Generador MinGW y compiladores explicitos (documentado en llama-cpp-python para Windows)
        os.environ["CMAKE_GENERATOR"] = "MinGW Makefiles"
        os.environ["CMAKE_ARGS"] = (f"-DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF "
                                    f"-DGGML_BMI2=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF "
                                    f"-DCMAKE_C_COMPILER={gcc_for_cmake} "
                                    f"-DCMAKE_CXX_COMPILER={gpp_for_cmake}")
        print("     ⚠️ Compilando desde fuente SIN AVX (puede tardar 5-15 min)...")
        # NOTA: --no-binary llama-cpp-python (NO :all:) para no forzar a compilar cmake/ninja desde fuente
        # Fijar 0.3.19: las versiones >= 0.3.22 traen rutas >260 chars (web UI de llama.cpp)
        # que superan MAX_PATH de Windows y rompen la extraccion del sdist (OSError Errno 2).
        # Temp corto para dar margen adicional a la longitud de rutas.
        old_tmp = os.environ.get("TMP")
        old_temp = os.environ.get("TEMP")
        short_tmp = os.path.join(os.path.splitdrive(SCRIPT_DIR)[0] or "C:", "pip-tmp")
        try:
            os.makedirs(short_tmp, exist_ok=True)
            os.environ["TMP"] = short_tmp
            os.environ["TEMP"] = short_tmp
        except Exception:
            pass
        log_path = os.path.join(SCRIPT_DIR, "llama_install.log")
        with open(log_path, "w", encoding="utf-8") as lf:
            result = subprocess.run(
                [pip, "install", "--no-cache-dir", "llama-cpp-python==0.3.19",
                 "--no-binary", "llama-cpp-python"],
                stdout=lf, stderr=lf)
        ok = result.returncode == 0
        if not ok:
            print(f"     ❌ Error compilando llama-cpp-python. Ultimas lineas del log:")
            try:
                with open(log_path, encoding="utf-8") as lf:
                    for line in lf.readlines()[-30:]:
                        print("        " + line.rstrip())
            except Exception:
                pass
        for var, val in (("TMP", old_tmp), ("TEMP", old_temp)):
            if val is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = val
        os.environ.pop("CMAKE_ARGS", None)
        os.environ.pop("CMAKE_GENERATOR", None)
        return ok

    def _linux_pkg_manager():
        for pm in ("apt-get", "dnf", "pacman"):
            if shutil.which(pm):
                return pm
        return None

    def _ensure_linux_build_tools():
        """Asegura que existan gcc, g++ y make para compilar llama-cpp-python."""
        missing = []
        for tool in ("gcc", "g++", "make"):
            if not shutil.which(tool):
                missing.append(tool)
        if not missing:
            return True
        print(f"     ⚠️ Faltan herramientas de compilación: {', '.join(missing)}")
        pm = _linux_pkg_manager()
        if pm == "apt-get":
            args = ["sudo", "apt-get", "install", "-y"] + missing
        elif pm == "dnf":
            args = ["sudo", "dnf", "install", "-y"] + missing
        elif pm == "pacman":
            args = ["sudo", "pacman", "-S", "--noconfirm"] + missing
        else:
            print(f"     ❌ No se pudo detectar el gestor de paquetes.")
            print(f"     Instala manualmente: sudo apt install {' '.join(missing)}")
            return False
        print(f"     🛠️ Ejecutando: {' '.join(args)}")
        print("     (puede pedir tu contraseña de sudo)")
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode != 0:
            print("     ❌ No se pudo instalar automáticamente (¿sin permisos sudo?).")
            print(f"     Ejecuta manualmente: sudo apt install {' '.join(missing)}")
            print("     y vuelve a ejecutar este instalador.")
            return False
        return all(shutil.which(t) for t in missing)

    def _build_llama_linux_no_avx():
        """Compila llama-cpp-python desde fuente SIN AVX/AVX2 (Linux, CPUs antiguas)."""
        if not _ensure_linux_build_tools():
            return False
        print("     ⚠️ Compilando desde fuente SIN AVX/AVX2 (puede tardar 5-15 min)...")
        old_cmake = os.environ.get("CMAKE_ARGS")
        os.environ["CMAKE_ARGS"] = ("-DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF "
                                    "-DGGML_BMI2=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF")
        log_path = os.path.join(SCRIPT_DIR, "llama_install.log")
        with open(log_path, "w", encoding="utf-8") as lf:
            result = subprocess.run(
                [pip, "install", "--no-cache-dir", "llama-cpp-python",
                 "--no-binary", "llama-cpp-python"],
                stdout=lf, stderr=lf)
        if old_cmake is None:
            os.environ.pop("CMAKE_ARGS", None)
        else:
            os.environ["CMAKE_ARGS"] = old_cmake
        ok = result.returncode == 0
        if not ok:
            print("     ❌ Error compilando llama-cpp-python. Ultimas lineas del log:")
            try:
                with open(log_path, encoding="utf-8") as lf:
                    for line in lf.readlines()[-20:]:
                        print("        " + line.rstrip())
            except Exception:
                pass
        return ok

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

            # Paso 2: detectar AVX2. Sin AVX2 los wheels precompilados crashean (SIGILL).
            has_avx2 = _cpu_has_avx2()
            if has_avx2:
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
            else:
                print("     CPU SIN AVX2: los wheels precompilados no son compatibles.")
                if _build_llama_no_avx():
                    return True
                print("     ⚠️ Compilacion sin AVX fallida, intentando wheels por si acaso...")
                if _pip_llama(["install", "llama-cpp-python", "--only-binary", ":all:"]):
                    return True
                if _pip_llama(["install", "llama-cpp-python", "--only-binary", ":all:",
                               "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cpu"]):
                    return True
            return False

        # Linux: los wheels precompilados requieren AVX2. En CPUs sin AVX2
        # crashean con SIGILL, así que primero compilar desde fuente.
        has_avx2 = _cpu_has_avx2()
        if not has_avx2:
            print("     CPU SIN AVX2: los wheels precompilados no son compatibles.")
            if _build_llama_linux_no_avx():
                return True
            print("     ⚠️ Compilacion sin AVX fallida, intentando wheels por si acaso...")
        if _pip_llama(["install", "llama-cpp-python", "--prefer-binary"]):
            return True
        print("  ⚠️ Reintentando con --no-cache-dir...")
        if _pip_llama(["install", "--no-cache-dir", "--prefer-binary", "llama-cpp-python"]):
            return True
        return False

    result_ok = _install_llama()

    if result_ok:
        if verify_import(venv_dir, "llama_cpp"):
            log("llama-cpp-python instalado")
        else:
            log("No se pudo importar. Forzando reinstall...", False)
            if _pip_llama(["install", "--force-reinstall", "--no-cache-dir", "llama-cpp-python"]) \
               and verify_import(venv_dir, "llama_cpp"):
                log("llama-cpp-python reinstalado y verificado")
            else:
                log("Error CRITICO: llama-cpp-python no funciona", False)
                fatal_error = True
    else:
        log("Error CRITICO: no se pudo instalar llama-cpp-python", False)
        fatal_error = True

    # 3b. Otras dependencias pip
    deps = ["Pillow", "ttkbootstrap"]
    if platform.system() == "Windows":
        deps.extend(["pyttsx3", "pywin32"])
    else:
        deps.extend(["pygame"])
    if not pip_install(pip, deps, ", ".join(deps)):
        print("  ⚠️ Error instalando dependencias secundarias.")
        print("     Puedes instalarlas manualmente después.")

    # 3c. espeak-ng para TTS en Linux
    if platform.system() != "Windows":
        print("  ⏳ Verificando espeak-ng (TTS en Linux)...")
        espeak = shutil.which("espeak-ng")
        if espeak:
            log("espeak-ng encontrado")
        else:
            print("     ⚠️ espeak-ng no instalado. Para activar TTS de voz:")
            print("       sudo apt install espeak-ng")
            print("     (La app funciona igual sin TTS)")

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

    # === 4. MODELO DE IA (opcional) ===
    section("🤖 Modelo de IA")
    model_dir = os.path.join(SCRIPT_DIR, "models")
    os.makedirs(model_dir, exist_ok=True)
    modelos_existentes = [f for f in os.listdir(model_dir) if f.endswith(".gguf") and os.path.getsize(os.path.join(model_dir, f)) > 1000000]
    if modelos_existentes:
        log(f"Modelo encontrado: {modelos_existentes[0]}")
        print("     ✅ La IA podrá usar respuestas avanzadas si está presente.")
    else:
        print("     ℹ️ Sin modelo descargado. LUNA usará su modo offline con")
        print("     respuestas completas de rutinas, dietas y consejos.")
        print("     Si quieres respuestas más avanzadas, coloca un modelo .gguf")
        print("     en la carpeta 'models/' manualmente.")

    # === 5. MUSICA ===
    section("🎵 Música")
    music_dir = os.path.join(SCRIPT_DIR, "musica")
    os.makedirs(music_dir, exist_ok=True)
    log("Carpeta musica/ creada (mete tus MP3 ahí)")

    # === 6. ACCESO DIRECTO (solo Linux) ===
    if platform.system() != "Windows":
        section("📌 Acceso directo")
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
            f.write('@echo off\ncd /d "%~dp0"\nstart "" /B "venv\\Scripts\\pythonw.exe" "main.py"\nexit\n')
        log("run.bat creado")

    # === 7. RESUMEN ===
    print("\n╔══════════════════════════════════════╗")
    print("║   INSTALACIÓN COMPLETADA            ║")
    print("╚══════════════════════════════════════╝")
    print("\n  🚀 Ejecutar:")
    if platform.system() == "Windows":
        print("     - Doble clic en 'run.bat'")
        print("     - O doble clic en 'iron-chat.bat'")
    else:
        print("     - Menú de aplicaciones → IRON CHAT - LUNA")
        print("     - O doble clic en el icono del escritorio")
        print("     - O en terminal:")
        print(f"        cd {SCRIPT_DIR}")
        print(f"        source venv/bin/activate")
        print(f"        python3 main.py")
    print("\n  💡 También puedes crear acceso desde la app: ☰ Menú → Acceso Escritorio")
    print("\n  ⚡ JMbirner ⚡\n")

    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
