import hashlib
import os
import re


def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_file(filepath, expected_hex):
    if not os.path.exists(filepath):
        return False
    actual = sha256_file(filepath)
    return actual.lower() == expected_hex.lower()


def file_size_ok(filepath, min_bytes=1_000_000):
    return os.path.exists(filepath) and os.path.getsize(filepath) >= min_bytes


ARCHIVOS_FIRMA = [
    "main.py", "ai_module.py", "tts_module.py", "face_animation.py",
    "ascii_art.py", "sounds.py", "audio.py", "progress_tracker.py",
    "hash_utils.py", "themes.py", "lang.py", "check_deps.py",
    "install.py", "install_windows.ps1", "install.sh", "install.bat",
    "uninstall.bat", "uninstall.sh",
    "iron-chat.bat", "backup.bat",
    "generar_firma.py", "verificar_firma.py",
    ".gitignore", "requirements.txt",
    "test_download.py"
]


def verify_project_integrity(project_dir):
    sig_file = os.path.join(project_dir, "SIGNATURE.md")
    if not os.path.exists(sig_file):
        return ("⚠️", "No se encontró SIGNATURE.md — integridad no verificable")

    with open(sig_file, 'r', encoding='utf-8') as f:
        contenido = f.read()
    match = re.search(r'SHA256:\s*([a-f0-9]{64})', contenido)
    if not match:
        return ("⚠️", "No hay hash en SIGNATURE.md")

    hash_original = match.group(1)
    hash_total = hashlib.sha256()
    missing = []
    for archivo in ARCHIVOS_FIRMA:
        ruta = os.path.join(project_dir, archivo)
        if os.path.exists(ruta):
            with open(ruta, 'rb') as f:
                hash_total.update(f.read())
        else:
            missing.append(archivo)

    hash_actual = hash_total.hexdigest()
    if hash_actual == hash_original:
        if missing:
            return ("⚠️", f"Firma válida, pero faltan archivos: {', '.join(missing)}")
        return ("✅", "Firma válida — ningún archivo fue modificado")
    else:
        return ("❌", "¡FIRMA INVÁLIDA! Los archivos han sido modificados")
