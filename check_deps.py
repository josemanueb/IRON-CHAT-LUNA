#!/usr/bin/env python3
"""
check_deps.py — Verifica dependencias de IRON CHAT - LUNA
Uso:  python3 check_deps.py
"""

import os
import sys
import subprocess
import platform
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OK = chr(0x2705)
WARN = chr(0x26A0) + chr(0xFE0F)
FAIL = chr(0x274C)
INFO = chr(0x2139) + chr(0xFE0F)


def log(msg, ok=True):
    icon = OK if ok else FAIL
    print(f"  {icon} {msg}")


def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def check_python():
    section("Python")
    v = sys.version_info
    ok = v.major == 3 and v.minor >= 10
    log(f"Python {v.major}.{v.minor}.{v.micro}", ok)
    if not ok:
        print(f"     {WARN} Se necesita Python 3.10+")
    return ok


def check_espeak():
    section("TTS (espeak-ng)")
    try:
        espeak = shutil.which("espeak-ng")
        ok = espeak is not None
        if ok:
            log("espeak-ng instalado", True)
        else:
            log("espeak-ng no instalado. sudo apt install espeak-ng", False)
        return ok
    except Exception:
        log("espeak-ng no disponible", False)
        return False


def check_pip():
    section("pip")
    try:
        r = subprocess.run([sys.executable, "-m", "pip", "--version"],
                           capture_output=True, text=True, timeout=15)
        ok = r.returncode == 0
        log(r.stdout.strip() if ok else "pip no encontrado", ok)
        return ok
    except Exception as e:
        log(f"pip: {e}", False)
        return False


def check_package(name, import_name=None):
    if import_name is None:
        import_name = name.replace("-", "_")
    try:
        __import__(import_name)
        log(f"{name}", True)
        return True
    except ImportError:
        log(f"{name} — NO INSTALADO", False)
        return False


def install_package(name):
    print(f"     {INFO} Instalando {name}...")
    r = subprocess.run([sys.executable, "-m", "pip", "install", name],
                       capture_output=True, text=True, timeout=120)
    if r.returncode == 0:
        log(f"{name} instalado", True)
        return True
    print(f"     {WARN} Falló instalación de {name}. Intentá:")
    print(f"            pip install {name}")
    return False


def check_packages(auto_install=False):
    section("Paquetes Python")
    pkgs = [("llama-cpp-python", "llama_cpp"),
            ("Pillow", "PIL"),
            ("ttkbootstrap", "ttkbootstrap")]
    if platform.system() == "Linux":
        pkgs.append(("pygame", "pygame"))
    elif platform.system() == "Windows":
        pkgs.append(("pyttsx3", "pyttsx3"))
        pkgs.append(("pywin32", "win32api"))

    all_ok = True
    for name, imp in pkgs:
        ok = check_package(name, imp)
        if not ok:
            all_ok = False
            if auto_install:
                install_package(name)

    return all_ok


def check_models():
    section("Modelo de IA")
    model_dir = os.path.join(SCRIPT_DIR, "models")
    os.makedirs(model_dir, exist_ok=True)

    existentes = [f for f in os.listdir(model_dir)
                  if f.endswith(".gguf") and
                  os.path.getsize(os.path.join(model_dir, f)) > 1000000]

    if existentes:
        for f in existentes:
            sz = os.path.getsize(os.path.join(model_dir, f)) / (1024**3)
            log(f"{f} ({sz:.2f} GB)", True)
        return True

    log("Sin modelo — modo offline activo", True)
    print(f"     {INFO} LUNA funciona offline con respuestas completas.")
    print(f"     {INFO} Para IA avanzada, coloca un .gguf en models/")
    return True


def check_venv():
    section("Entorno virtual")
    venv_dir = os.path.join(SCRIPT_DIR, "venv")
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    log("Entorno virtual activo" if in_venv else "NO hay entorno virtual activo", in_venv)
    if not in_venv and os.path.exists(venv_dir):
        log(f"Venv detectado en: {venv_dir}", True)
        print(f"     {INFO} Activá con:")
        if platform.system() == "Windows":
            print(f"            {venv_dir}\\Scripts\\activate")
        else:
            print(f"            source {venv_dir}/bin/activate")
    elif not in_venv:
        log("Podés crear uno con: python3 -m venv venv", True)
    return in_venv


def main(auto_install=False):
    print(f"\n{'='*55}")
    print(f"  🔍 CHECK DEPS — IRON CHAT LUNA")
    print(f"  {platform.system()} | Python {sys.version.split()[0]}")
    print(f"{'='*55}")

    results = []

    results.append(("Python", check_python()))
    results.append(("Entorno virtual", check_venv()))
    results.append(("pip", check_pip()))
    results.append(("Paquetes", check_packages(auto_install)))
    results.append(("Modelo IA", check_models()))
    if platform.system() == "Linux":
        results.append(("TTS espeak-ng", check_espeak()))

    print(f"\n{'='*55}")
    print(f"  RESUMEN")
    print(f"{'='*55}")
    all_ok = True
    for name, ok in results:
        icon = OK if ok else FAIL
        print(f"  {icon} {name}")
        if not ok:
            all_ok = False

    if all_ok:
        print(f"\n  {OK} TODO LISTO — podés ejecutar main.py")
    else:
        print(f"\n  {WARN} Algunas cosas faltan, revisá los mensajes de arriba")
    print()

    return all_ok


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Verifica dependencias de IRON CHAT - LUNA")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Instalar paquetes faltantes automáticamente")
    parser.add_argument("--all", action="store_true",
                        help="Equivalente a --yes")
    args = parser.parse_args()

    if args.all:
        args.yes = True

    ok = main(auto_install=args.yes)
    sys.exit(0 if ok else 1)
