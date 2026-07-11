#!/usr/bin/env python3
"""Simulación de descarga de modelo - test sin GUI"""
import os
import sys
import ssl
import time
import urllib.request

DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Modelo más pequeño para test rápido (TinyLlama ~700MB)
REPO = "MaziyarPanahi/Llama-3.2-1B-Instruct-GGUF"
FILE = "Llama-3.2-1B-Instruct.Q4_K_M.gguf"
URL = f"https://huggingface.co/{REPO}/resolve/main/{FILE}"
DEST = os.path.join(MODELS_DIR, FILE)

print("=" * 50)
print("  SIMULACIÓN DE DESCARGA - IRON CHAT")
print("=" * 50)
print(f"\nModelo: TinyLlama 1.1B (~700 MB)")
print(f"URL: {URL}")
print(f"Destino: {DEST}")
print()

# Verificar si ya existe
if os.path.exists(DEST) and os.path.getsize(DEST) > 1_000_000:
    print(f"✅ Modelo ya existe ({os.path.getsize(DEST) / 1_024_000:.1f} MB)")
    print("No es necesario descargar de nuevo.")
    sys.exit(0)

# Intentar descargar
print("📥 Iniciando descarga...")
print("   (esto puede tomar varios minutos dependiendo de tu conexión)")
print()

try:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(URL)
    req.add_header("User-Agent", "IRON-CHAT-LUNA/2.2")
    
    print("   Conectando a HuggingFace...")
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    total = int(resp.headers.get("Content-Length", 0))
    print(f"   Content-Length: {total:,} bytes ({total / 1_024_000:.1f} MB)")
    print()
    
    sent = 0
    chunk_size = 65536
    tmp = DEST + ".tmp"
    start_time = time.time()
    last_pct = -1
    
    with open(tmp, "wb") as f:
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            sent += len(chunk)
            
            if total > 0:
                pct = int(sent * 100 / total)
                if pct >= last_pct + 5 or pct == 100:
                    last_pct = pct
                    elapsed = time.time() - start_time
                    speed = sent / elapsed / 1_024_000 if elapsed > 0 else 0
                    mb_sent = sent / 1_024_000
                    mb_total = total / 1_024_000
                    print(f"\r   [{pct:3d}%] {mb_sent:.1f}/{mb_total:.1f} MB ({speed:.1f} MB/s)", end="", flush=True)
    
    resp.close()
    elapsed = time.time() - start_time
    sz = os.path.getsize(tmp)
    
    print(f"\n\n   ✅ Descarga completada en {elapsed:.1f}s")
    print(f"   Tamaño: {sz:,} bytes ({sz / 1_024_000:.1f} MB)")
    
    if sz < 1_000_000:
        print(f"\n   ❌ ERROR: Archivo corrupto (solo {sz} bytes)")
        os.remove(tmp)
        sys.exit(1)
    
    # Renombrar
    os.replace(tmp, DEST)
    print(f"   Guardado en: {DEST}")
    print("\n   ✅ ¡Listo! El modelo está disponible para usar.")
    
except ssl.SSLCertVerificationError as e:
    print(f"\n\n   ❌ Error SSL: {e}")
    print("   Solución: pip install --upgrade certifi")
    sys.exit(1)
    
except urllib.error.URLError as e:
    err = str(e.reason) if hasattr(e, 'reason') else str(e)
    print(f"\n\n   ❌ Error de red: {err}")
    if "timed out" in err.lower():
        print("   Tu conexión a internet está lenta. Intentá de nuevo en unos minutos.")
    sys.exit(1)
    
except urllib.error.HTTPError as e:
    print(f"\n\n   ❌ HTTP Error {e.code}: {e.reason}")
    if e.code in (401, 403):
        print("   Acceso denegado. El archivo puede haber sido movido.")
    sys.exit(1)
    
except Exception as e:
    print(f"\n\n   ❌ Error inesperado: {e}")
    # Limpiar tmp
    if os.path.exists(DEST + ".tmp"):
        try: os.remove(DEST + ".tmp")
        except: pass
    sys.exit(1)
