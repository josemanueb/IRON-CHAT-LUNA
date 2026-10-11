import hashlib
import os
import re


def sha256_file(filepath):
    """SHA256 de un fichero tal cual (binario: modelo GGUF, etc.)."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_source_file(filepath):
    """SHA256 de un fichero de TEXTO normalizando los finales de linea.

    Necesario para la firma del proyecto: Git guarda LF en el indice y
    checkout en Windows escribe CRLF, asi que el hash de los mismos bytes
    logicos daba distinto en cada plataforma y el CI siempre fallaba.
    Normalizar CRLF/CR a LF hace que la firma dependa del contenido, no de
    como lo guardo cada sistema operativo.
    """
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            datos = f.read()
    except OSError:
        raise
    datos = datos.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    h.update(datos)
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
    "test_all.py", "test_download.py", "test_smoke_gui.py",
    ".gitignore", "requirements.txt",
    # Nucleo extraido de main.py en la v2.3.
    "knowledge.py", "config_store.py", "download_worker.py", "logging_setup.py",
    # Datos de la base de conocimiento.
    "rutinas.json", "conocimiento.json",
]


def _hash_firmado(archivo):
    """Hash de un archivo de la firma, normalizando finales de linea."""
    return sha256_source_file(archivo)


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
            # Normalizado: la firma no puede depender de CRLF vs LF.
            hash_total.update(bytes.fromhex(_hash_firmado(ruta)))
        else:
            missing.append(archivo)

    hash_actual = hash_total.hexdigest()
    if hash_actual == hash_original:
        if missing:
            return ("⚠️", f"Firma válida, pero faltan archivos: {', '.join(missing)}")
        return ("✅", "Firma válida — ningún archivo fue modificado")
    else:
        return ("❌", "¡FIRMA INVÁLIDA! Los archivos han sido modificados")
