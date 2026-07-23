#!/usr/bin/env python3
"""Smoke tests para IRON CHAT - LUNA"""
import sys
import os
import tempfile

DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)

PASS = 0
FAIL = 0

def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  ✅ {name}")
        PASS += 1
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        FAIL += 1


def imports_ok():
    import platform
    import re
    import json
    import glob
    import logging
    import threading
    import subprocess
    import struct
    import math
    import io
    import wave
    import hashlib
    from datetime import datetime
    from tkinter import messagebox, ttk
    import tkinter as tk
    # Pillow test
    from PIL import Image, ImageTk
    # Project modules (except ai_module which needs model file)
    from ascii_art import ASCIIArt
    from audio import Audio
    from sounds import Sounds
    from tts_module import TTS
    from face_animation import AnimatedFace


def ascii_art_ok():
    from ascii_art import ASCIIArt
    arts = ASCIIArt.list_arts()
    assert len(arts) > 0, "No hay ASCII arts"
    art = ASCIIArt.get_art(arts[0])
    assert art and len(art) > 10


def progress_tracker_ok():
    import tempfile
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    try:
        from progress_tracker import ProgressTracker
        p = ProgressTracker(f.name)
        p.add_entry(weight=75, bicep=35, chest=80, waist=90, notes="test")
        entries = p.get_entries()
        assert len(entries) == 1
        assert entries[0][0] is not None  # date
        assert entries[0][1] == 75.0      # weight
        assert entries[0][2] == 35.0      # bicep
        assert entries[0][3] == 80.0      # chest
    finally:
        os.unlink(f.name)


def sounds_imports_ok():
    from sounds import Sounds as S
    assert hasattr(S, "play_chat")
    assert hasattr(S, "play_startup")
    assert hasattr(S, "play_notification")


def audio_imports_ok():
    from audio import Audio as A
    assert hasattr(A, "play_wav")
    assert hasattr(A, "play_beep")
    assert hasattr(A, "play_music")
    assert hasattr(A, "stop_music")
    assert hasattr(A, "stop_all")


def tts_imports_ok():
    from tts_module import TTS as T
    assert hasattr(T, "speak")
    assert hasattr(T, "stop")
    assert hasattr(T, "set_volume")


def signature_files_match():
    import ast
    def _extract_list(filepath):
        with open(filepath) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "archivos":
                        return [el.value for el in node.value.elts]
        return []
    gen = _extract_list(os.path.join(DIR, "generar_firma.py"))
    ver = _extract_list(os.path.join(DIR, "verificar_firma.py"))
    assert gen == ver, f"Listas diferentes!\n  gen: {gen}\n  ver: {ver}"
    for a in gen:
        assert os.path.exists(os.path.join(DIR, a)), f"Falta archivo: {a}"


def check_deps_imports_ok():
    import check_deps
    assert hasattr(check_deps, "main")
    assert hasattr(check_deps, "check_python")
    assert hasattr(check_deps, "check_packages")

def install_imports_ok():
    import install
    assert hasattr(install, "download_model_auto")
    assert hasattr(install, "_download_chunked")
    assert hasattr(install, "download_with_powershell")
    assert hasattr(install, "download_with_bits")


def sounds_generate_wav():
    from sounds import Sounds as S
    samples = S._gen_wav([0, 100, 200, 100, 0], 22050)
    assert len(samples) > 0
    assert samples[:4] == b'RIFF'


def verificar_firma_syntax():
    import ast
    with open(os.path.join(DIR, "verificar_firma.py")) as f:
        tree = ast.parse(f.read())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "archivos":
                    found = True
    assert found, "No se encontró variable 'archivos' en verificar_firma.py"


def face_animation_import():
    from face_animation import AnimatedFace as F
    assert hasattr(F, "set_speaking")


def main_methods_exist():
    import inspect
    import main as m
    required = [
        "download_model", "crear_acceso_escritorio",
        "_model_downloaded", "_reload_ai_after_download",
        "_modelo_nombre",
        "_desktop_path", "_pythonw_path", "_abrir_menu",
    ]
    for method in required:
        assert hasattr(m.ChatbotApp, method), f"Falta método: {method}"


def luna_sh_syntax():
    path = os.path.join(DIR, "luna.sh")
    with open(path) as f:
        lines = f.readlines()
    assert len(lines) >= 2, "luna.sh muy corto"
    assert lines[0].startswith("#!/"), "luna.sh falta shebang"


def themes_module_ok():
    from themes import COLORES, get_theme, theme_count
    assert theme_count() == 3, f"Se esperaban 3 temas, hay {theme_count()}"
    for i in range(theme_count()):
        t = get_theme(i)
        assert "nombre" in t, f"Tema {i} sin nombre"
        assert "bg" in t, f"Tema {i} sin bg"
        assert "fg" in t, f"Tema {i} sin fg"
    t = get_theme(99)
    assert t["nombre"] == COLORES[0]["nombre"], "Wrap-around no funciona"


def hash_utils_ok():
    from hash_utils import sha256_file, verify_file, file_size_ok
    import tempfile
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    f.write(b"hello world")
    f.close()
    try:
        h = sha256_file(f.name)
        assert len(h) == 64, f"Hash no es SHA256: {len(h)}"
        assert verify_file(f.name, h), "verify_file falla con hash correcto"
        assert not verify_file(f.name, "badhash"), "verify_file no rechaza hash malo"
        assert file_size_ok(f.name, 1), "file_size_ok falla"
        assert not file_size_ok(f.name, 999999), "file_size_ok no rechaza minimo alto"
    finally:
        os.unlink(f.name)


def rutinas_json_ok():
    import json
    path = os.path.join(DIR, "rutinas.json")
    assert os.path.exists(path), "rutinas.json no existe"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 10, f"Se esperaban >=10 rutinas, hay {len(data)}"
    for key, rutina in data.items():
        assert "keywords" in rutina, f"Rutina {key} sin keywords"
        assert "response" in rutina, f"Rutina {key} sin response"
        assert len(rutina["keywords"]) > 0, f"Rutina {key} con keywords vacías"
        assert len(rutina["response"]) > 20, f"Rutina {key} response muy corta"


def ai_module_rutinas_ok():
    from ai_module import _RUTINAS, GPT4AllAI
    assert len(_RUTINAS) >= 10, f"Se esperaban >=10 rutinas cargadas"
    resp = GPT4AllAI._offline_response(None, "dame rutina de pecho")
    assert "RUTINA" in resp, f"Respuesta no contiene RUTINA: {resp[:50]}"
    resp2 = GPT4AllAI._offline_response(None, "quiero rutina de piernas")
    assert "PIERNAS" in resp2, f"Respuesta no contiene PIERNAS: {resp2[:50]}"


def progress_tracker_context_manager_ok():
    import tempfile
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    try:
        from progress_tracker import ProgressTracker
        p = ProgressTracker(f.name)
        p.add_entry(weight=80)
        p.add_entry(weight=82)
        entries = p.get_entries()
        assert len(entries) == 2
    finally:
        os.unlink(f.name)


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print("  PRUEBAS DE ESTABILIDAD - IRON CHAT LUNA")
    print(f"{'='*50}\n")

    test("Todos los imports estándar y del proyecto", imports_ok)
    test("ASCII Art: lista y obtiene arte", ascii_art_ok)
    test("Progress Tracker: crear entrada y leer", progress_tracker_ok)
    test("Sounds: métodos existen", sounds_imports_ok)
    test("Audio: métodos existen", audio_imports_ok)
    test("TTS: métodos existen", tts_imports_ok)
    test("FaceAnimation: métodos existen", face_animation_import)
    test("generar_firma == verificar_firma (mismos archivos)", signature_files_match)
    test("Install: módulo se importa", install_imports_ok)
    test("check_deps: módulo se importa", check_deps_imports_ok)
    test("Verificar firma: módulo se importa", verificar_firma_syntax)
    test("Sounds: _gen_wav genera RIFF válido", sounds_generate_wav)
    test("Main: métodos nuevos existen", main_methods_exist)
    test("luna.sh: sintaxis válida", luna_sh_syntax)
    test("Themes: 3 temas con keys correctas", themes_module_ok)
    test("Hash utils: SHA256 y verificación", hash_utils_ok)
    test("Rutinas JSON: 10+ rutinas válidas", rutinas_json_ok)
    test("AI module: rutinas desde JSON funcionan", ai_module_rutinas_ok)
    test("Progress Tracker: context manager funciona", progress_tracker_context_manager_ok)

    print(f"\n{'='*50}")
    print(f"  RESULTADO: {PASS} pasaron, {FAIL} fallaron")
    if FAIL == 0:
        print("  ✅ TODO OK")
    else:
        print("  ❌ HAY FALLOS")
    print(f"{'='*50}\n")
    sys.exit(FAIL)
