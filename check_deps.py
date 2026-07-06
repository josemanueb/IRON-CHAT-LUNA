#!/usr/bin/env python3
"""
check_deps.py — Verifica dependencias de IRON CHAT - LUNA
y descarga automáticamente lo que falta (modelo, voces, paquetes).
Uso:  python3 check_deps.py
"""

import os
import sys
import subprocess
import platform
import urllib.request
import hashlib

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


def download_model_auto(force_qwen=True):
    """Descarga modelo sin interacción."""
    model_dir = os.path.join(SCRIPT_DIR, "models")
    os.makedirs(model_dir, exist_ok=True)

    if force_qwen:
        name = "qwen2.5-3b-instruct-q4_k_m.gguf"
        url = ("https://huggingface.co/Qwen/"
               "Qwen2.5-3B-Instruct-GGUF/resolve/main/"
               "qwen2.5-3b-instruct-q4_k_m.gguf")
    else:
        name = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
        url = ("https://huggingface.co/bartowski/"
               "Llama-3.2-3B-Instruct-GGUF/resolve/main/"
               "Llama-3.2-3B-Instruct-Q4_K_M.gguf")

    path = os.path.join(model_dir, name)
    if os.path.exists(path) and os.path.getsize(path) > 1000000:
        return True

    print(f"     Descargando {name} (~2 GB)...")
    try:
        urllib.request.urlretrieve(url, path + ".tmp")
        os.rename(path + ".tmp", path)
        sz = os.path.getsize(path) / (1024**3)
        log(f"{name} descargado ({sz:.2f} GB)", True)
        return True
    except Exception as e:
        print(f"     {FAIL} Error: {e}")
        print(f"     Descargá manualmente de:\n            {url}")
        return False


def download_voice_auto():
    """Descarga voz Piper sin interacción."""
    voices_dir = os.path.join(SCRIPT_DIR, "voices")
    os.makedirs(voices_dir, exist_ok=True)

    voice_name = "es_ES-sharvard-medium.onnx"
    voice_path = os.path.join(voices_dir, voice_name)
    voice_json_path = voice_path + ".json"

    if os.path.exists(voice_path) and os.path.getsize(voice_path) > 10000:
        return True

    base = ("https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx")
    for suffix, dest in [("", voice_path), (".json", voice_json_path)]:
        try:
            urllib.request.urlretrieve(base + suffix, dest + ".tmp")
            os.rename(dest + ".tmp", dest)
        except Exception as e:
            print(f"     {WARN} Error descargando {suffix or 'voz'}: {e}")
            return False

    ok = os.path.exists(voice_path) and os.path.getsize(voice_path) > 10000
    if ok:
        log(f"Voz {voice_name} descargada", True)
    else:
        log("Voz no disponible", False)
    return ok


def check_packages(auto_install=False):
    section("Paquetes Python")
    pkgs = [("llama-cpp-python", "llama_cpp"),
            ("Pillow", "PIL")]
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


def check_models(auto_download=False, force_qwen=True):
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

    log("Ningún modelo encontrado", False)
    if auto_download:
        return download_model_auto(force_qwen)
    else:
        print(f"     {INFO} Ejecutá con --download-model o:\n"
              "            python3 install.py")
        return False


def check_voices(auto_download=False):
    section("Voces TTS (Piper)")
    voices_dir = os.path.join(SCRIPT_DIR, "voices")
    os.makedirs(voices_dir, exist_ok=True)

    voice_name = "es_ES-sharvard-medium.onnx"
    voice_path = os.path.join(voices_dir, voice_name)
    voice_json_path = voice_path + ".json"

    if os.path.exists(voice_path) and os.path.getsize(voice_path) > 10000:
        log(f"Voz {voice_name} existe", True)
        return True

    log("Voz Piper no encontrada", False)
    if auto_download:
        return download_voice_auto()
    else:
        print(f"     {INFO} Ejecutá con --download-voice")
        return False


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


def main(auto_install=False, download_model=False, download_voice=False,
         force_qwen=True):
    print(f"\n{'='*55}")
    print(f"  🔍 CHECK DEPS — IRON CHAT LUNA")
    print(f"  {platform.system()} | Python {sys.version.split()[0]}")
    print(f"{'='*55}")

    results = []

    results.append(("Python", check_python()))
    results.append(("Entorno virtual", check_venv()))
    results.append(("pip", check_pip()))
    results.append(("Paquetes", check_packages(auto_install)))
    results.append(("Modelo IA", check_models(download_model, force_qwen)))
    if platform.system() == "Linux":
        results.append(("Voces TTS", check_voices(download_voice)))

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
    parser.add_argument("--download-model", action="store_true",
                        help="Descargar modelo Qwen (o usar --llama)")
    parser.add_argument("--download-voice", action="store_true",
                        help="Descargar voz Piper")
    parser.add_argument("--llama", action="store_true",
                        help="Usar Llama 3.2 3B en vez de Qwen")
    parser.add_argument("--all", action="store_true",
                        help="Equivalente a --yes --download-model --download-voice")
    args = parser.parse_args()

    if args.all:
        args.yes = True
        args.download_model = True
        args.download_voice = True

    ok = main(auto_install=args.yes,
              download_model=args.download_model,
              download_voice=args.download_voice,
              force_qwen=not args.llama)
    sys.exit(0 if ok else 1)
