#!/usr/bin/env python3
"""Logging con rotacion para iron_chat.log.

Antes se usaba logging.basicConfig(filename=...) sin rotacion: el log
crecia sin limite y un usuario que entrena a diario acababa con un
iron_chat.log de cientos de MB.

Aqui se limita a 2 MB con 3 copias de seguridad (rotacion automatica).
"""
import logging
import logging.handlers
import os

LOG_NAME = "iron_chat.log"
MAX_BYTES = 2 * 1024 * 1024
BACKUP_COUNT = 3
FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATEFMT = "%H:%M:%S"


def setup_logging(project_dir):
    """Configura el logger raiz. Devuelve la ruta del log o None si falla.

    Nunca lanza: si el disco esta lleno o el fichero esta bloqueado, la app
    debe arrancar igual escribiendo en consola.
    """
    log_path = os.path.join(project_dir, LOG_NAME)
    root = logging.getLogger()
    # Si ya hay handlers (main.py los puso antes), no duplicamos.
    if root.handlers:
        return log_path
    try:
        handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
    except OSError:
        return None
    handler.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFMT))
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    return log_path


def tail(path, lines=40):
    """Ultimas lineas del log, para el dialogo de ayuda/diagnostico."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return "".join(f.readlines()[-lines:])
    except OSError:
        return ""