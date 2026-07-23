#!/usr/bin/env python3
import hashlib
import os
import re
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hash_utils import ARCHIVOS_FIRMA

project_dir = os.path.dirname(os.path.abspath(__file__))
hash_total = hashlib.sha256()

for archivo in ARCHIVOS_FIRMA:
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
print(f"Archivos: {len(ARCHIVOS_FIRMA)}")
print("="*50)

sig_file = os.path.join(project_dir, "SIGNATURE.md")
if os.path.exists(sig_file):
    with open(sig_file, 'r', encoding='utf-8') as f:
        contenido = f.read()

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
