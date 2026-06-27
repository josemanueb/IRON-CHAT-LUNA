#!/usr/bin/env python3
import hashlib
import os
from datetime import datetime

project_dir = os.path.dirname(os.path.abspath(__file__))
archivos = [
    "main.py", "ai_module.py", "tts_module.py", "face_animation.py",
    "ascii_art.py", "sounds.py", "audio.py", "progress_tracker.py",
    "install.py", "install_windows.ps1", "install.sh", "install.bat",
    "uninstall.bat", "uninstall.sh", "crear_acceso_windows.vbs",
    "iron-chat.bat", "backup.bat",
    "generar_firma.py", "verificar_firma.py",
    ".gitignore", "requirements.txt"
]

hash_total = hashlib.sha256()

for archivo in archivos:
    ruta = os.path.join(project_dir, archivo)
    if os.path.exists(ruta):
        with open(ruta, 'rb') as f:
            contenido = f.read()
            hash_total.update(contenido)
            print(f"✅ {archivo} - OK")
    else:
        print(f"⚠️ {archivo} - NO ENCONTRADO")

hash_final = hash_total.hexdigest()

print("\n" + "="*50)
print("🔐 SELLO DE INTEGRIDAD IRON CHAT - LUNA")
print("="*50)
print(f"Hash SHA256: {hash_final}")
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Archivos: {len(archivos)}")
print("="*50)

# Guardar en SIGNATURE.md
sig_file = os.path.join(project_dir, "SIGNATURE.md")
if os.path.exists(sig_file):
    with open(sig_file, 'r', encoding='utf-8') as f:
        contenido = f.read()

    import re
    if re.search(r'SHA256:.*', contenido):
        contenido = re.sub(r'SHA256:.*', f'SHA256: {hash_final}', contenido)
        contenido = re.sub(r'Fecha:.*', f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', contenido)
    else:
        contenido += f"\n### 🔐 VERIFICACION\n```\nSHA256: {hash_final}\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n```\n"

    with open(sig_file, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"\n✅ Firma guardada en SIGNATURE.md")
else:
    print(f"\n⚠️ No se encontro SIGNATURE.md")

print("\n💪 IRON CHAT - LUNA | ⚡ JMbirner ⚡ + 🤖 UOS AI")
