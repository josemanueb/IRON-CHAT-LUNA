#!/usr/bin/env python3
import hashlib
import os
import re

project_dir = os.path.dirname(os.path.abspath(__file__))
archivos = [
    "main.py", "ai_module.py", "tts_module.py", "face_animation.py",
    "ascii_art.py", "sounds.py", "audio.py", "progress_tracker.py",
    "install.py", "install_windows.ps1", "install.sh", "install.bat",
    "uninstall.bat", "uninstall.sh",
    "iron-chat.bat", "backup.bat",
    "generar_firma.py", "verificar_firma.py",
    ".gitignore", "requirements.txt", "check_deps.py",
    ".github/workflows/test.yml"
]

hash_total = hashlib.sha256()
for archivo in archivos:
    ruta = os.path.join(project_dir, archivo)
    if os.path.exists(ruta):
        with open(ruta, 'rb') as f:
            hash_total.update(f.read())

hash_actual = hash_total.hexdigest()

sig_file = os.path.join(project_dir, "SIGNATURE.md")
if os.path.exists(sig_file):
    with open(sig_file, 'r', encoding='utf-8') as f:
        contenido = f.read()
    match = re.search(r'SHA256:\s*([a-f0-9]{64})', contenido)
    if match:
        hash_original = match.group(1)
        print("="*50)
        print("🔐 VERIFICACION DE INTEGRIDAD")
        print("="*50)
        print(f"Hash original: {hash_original}")
        print(f"Hash actual:   {hash_actual}")
        if hash_actual == hash_original:
            print("\n✅ ¡FIRMA VALIDA! Los archivos no han sido modificados.")
        else:
            print("\n❌ ¡FIRMA INVALIDA! Los archivos han sido modificados.")
        print("="*50)
    else:
        print("❌ No se encontro hash en SIGNATURE.md")
else:
    print("❌ No se encontro SIGNATURE.md")
