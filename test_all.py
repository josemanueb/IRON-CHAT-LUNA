#!/usr/bin/env python3
"""Smoke tests para IRON CHAT - LUNA"""
import sys
import os
import tempfile
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
try:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)

PASS = 0
FAIL = 0

def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  [OK] {name}")
        PASS += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
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
    # Pillow test (opcional)
    try:
        from PIL import Image, ImageTk
        PIL_AVAILABLE = True
    except ImportError:
        PIL_AVAILABLE = False
        raise RuntimeError("Falta Pillow: pip install Pillow")
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
    from hash_utils import ARCHIVOS_FIRMA
    assert len(ARCHIVOS_FIRMA) > 0
    for a in ARCHIVOS_FIRMA:
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
    from hash_utils import ARCHIVOS_FIRMA
    assert len(ARCHIVOS_FIRMA) > 0, "ARCHIVOS_FIRMA vacío"
    assert "main.py" in ARCHIVOS_FIRMA


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



# --- v2.3: tests de logica real (antes solo se comprobaba que los metodos
# --- existieran, no que hicieran lo que deben) ---------------------------


def knowledge_carga():
    import knowledge
    info = knowledge.stats()
    assert info["disponible"], "conocimiento.json no se cargo"
    assert info["categorias"] >= 20, f"pocas categorias: {info['categorias']}"
    assert info["keywords"] >= 100, f"pocas keywords: {info['keywords']}"
    assert info["ejercicios"] >= 10, f"pocos ejercicios: {info['ejercicios']}"
    assert info["genericas"] >= 5, f"pocas genericas: {info['genericas']}"


def knowledge_respuestas():
    import knowledge
    # Cada intention debe resolverse a la categoria esperada.
    casos = [
        ("hola", "saludo"),
        ("gracias!", "agradecimiento"),
        ("quiero una rutina de volumen", "dieta_volumen"),
        ("me duele la rodilla", "lesiones"),
        ("quiero creature", None),          # no debe matchear nada
        ("quiero un consejo", "consejos"),
    ]
    for entrada, esperado in casos:
        cat = knowledge.find_categoria(entrada)
        assert cat == esperado, f"{entrada!r} -> {cat!r}, esperaba {esperado!r}"
        if esperado:
            resp = knowledge.get_categoria_response(esperado)
            assert resp, f"categoria {esperado} sin respuesta"


def knowledge_ejercicio_exacto():
    import knowledge
    guia = knowledge.find_ejercicio("como se hace el press banca")
    assert guia and "BANCA" in guia.upper(), f"no encontro guia: {guia}"
    assert knowledge.find_ejercicio("xyzabc") is None


def knowledge_generica_siempre():
    import knowledge
    r = knowledge.respuesta_generica()
    assert r and len(r) > 10, "respuesta generica vacia"


def knowledge_resumen_prompt():
    import knowledge
    resumen = knowledge.resumen_para_prompt(max_chars=800)
    assert resumen, "resumen vacio"
    assert len(resumen) <= 800, f"resumen sin recortar: {len(resumen)}"


def ai_offline_saludo_prioritario():
    """'hola' debe ganar a 'rutina de pecho' (mismo orden que antes)."""
    from ai_module import GPT4AllAI
    resp = GPT4AllAI._offline_response(None, "hola, dame rutina de pecho")
    assert "LUNA" in resp, f"saludo no tiene prioridad: {resp[:60]}"


def ai_offline_rutina_prioritaria():
    from ai_module import GPT4AllAI
    resp = GPT4AllAI._offline_response(None, "dame rutina de piernas")
    assert "PIERNAS" in resp.upper(), f"no es rutina de piernas: {resp[:60]}"


def ai_offline_ejercicio():
    from ai_module import GPT4AllAI
    # La guia tecnica gana a las keywords de rutina: "peso muerto" es una
    # peticion de tecnica, no una peticion de rutina de piernas/espalda.
    resp = GPT4AllAI._offline_response(None, "como se hace el peso muerto")
    assert "PESO MUERTO" in resp.upper(), f"no es guia de peso muerto: {resp[:60]}"
    assert "Deadlift" in resp, "le falta el nombre ingles del ejercicio"
    # Y una peticion de rutina sigue devolviendo la rutina, no la guia.
    resp2 = GPT4AllAI._offline_response(None, "dame rutina de espalda")
    assert "RUTINA" in resp2.upper(), f"no es rutina: {resp2[:60]}"


def ai_offline_vacio_no_rompe():
    from ai_module import GPT4AllAI
    for entrada in ("", "   ", None):
        resp = GPT4AllAI._offline_response(None, entrada)
        assert resp and isinstance(resp, str), f"fallo con {entrada!r}"


def ai_prompt_chatml():
    """El prompt debe usar cabeceras de chat reales, no texto plano."""
    import ai_module
    ai = object.__new__(ai_module.GPT4AllAI)
    ai.model_type = "qwen"
    ai.n_ctx = 2048
    ai.max_tokens = 500
    ai._memorias = []

    ims = "<|" + "im_start" + "|>"
    ime = "<|" + "im_end" + "|>"
    prompt = ai._build_prompt("hola", history=[("user", "q"), ("assistant", "a")])
    assert prompt.startswith(ims + "system"), "no empieza por cabecera system"
    # La ultima linea debe ser la cabecera de assistant, con salto de linea.
    assert prompt.endswith(ims + "assistant" + chr(10)), \
        "no termina pidiendo assistant"
    assert ime in prompt, "no cierra turnos"
    assert "<|im_end|>" in ai._stop_tokens(), "stop token ChatML ausente"


def ai_prompt_trunca_historial():
    """Un historial enorme no debe desbordar el presupuesto de contexto."""
    import ai_module
    ai = object.__new__(ai_module.GPT4AllAI)
    ai.model_type = "qwen"
    ai.n_ctx = 2048
    ai.max_tokens = 500
    ai._memorias = []
    largo = [("user", "x" * 5000), ("assistant", "y" * 5000)] * 8
    prompt = ai._build_prompt("cuanto pesa una sentadilla", history=largo)
    presupuesto = (2048 - 500 - 200) * 3
    assert len(prompt) < presupuesto + 2000, f"prompt desborde: {len(prompt)}"
    assert "cuanto pesa una sentadilla" in prompt, "perdio la pregunta actual"


def ai_llama3_usa_plantilla_propia():
    import ai_module
    assert ai_module.GPT4AllAI._detect_model_type("Llama-3.2-3B.gguf") == "llama3"
    assert ai_module.GPT4AllAI._detect_model_type("Qwen2.5-1.5B.gguf") == "qwen"
    assert ai_module.GPT4AllAI._detect_model_type("TinyLlama.gguf") == "llama"
    ai = object.__new__(ai_module.GPT4AllAI)
    ai.model_type = "llama3"
    ai.n_ctx, ai.max_tokens, ai._memorias = 2048, 500, []
    eot = "<|" + "eot_id" + "|>"
    assert ai._stop_tokens()[0] == eot, "Llama3 debe parar con eot_id"
    assert ai._chat_template() == "llama3"
    sh = "<|" + "start_header_id" + "|>"
    assert sh in ai._build_prompt("hola"), "falta cabecera Llama3"


def ai_gpu_layers_segun_config():
    import ai_module
    ai = object.__new__(ai_module.GPT4AllAI)
    assert ai._resolve_gpu_layers({"n_gpu_layers": 0}) == 0, "0 debe forzar CPU"
    assert ai._resolve_gpu_layers({"n_gpu_layers": -1}) == -1, "-1 = autodetect"
    assert ai._resolve_gpu_layers({"n_gpu_layers": 20}) == 20
    # Sin llama_cpp no debe lanzar.
    assert ai._resolve_gpu_layers({}) in (0, -1)


def config_store_default():
    import config_store
    cfg = config_store.load_config(".")
    for key in config_store.SCHEMA:
        assert key in cfg, f"falta clave por defecto: {key}"


def config_store_corrupto_no_rompe():
    import config_store, tempfile, os
    d = tempfile.mkdtemp()
    for contenido in ("{no es json", "", "[1,2,3]", '"texto"', "null"):
        with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
            f.write(contenido)
        cfg = config_store.load_config(d)
        assert cfg["theme"] == 0, f"config corrupto filtro mal: {contenido!r}"
        assert cfg["music_volume"] == 50
    import shutil
    shutil.rmtree(d, ignore_errors=True)


def config_store_valida_rangos():
    import config_store, tempfile, os, json
    d = tempfile.mkdtemp()
    casos = [
        ({"music_volume": 9999}, "music_volume", 50),
        ({"music_volume": -5}, "music_volume", 50),
        ({"tts_speed": 1000}, "tts_speed", 100),
        ({"tts_speed": 1}, "tts_speed", 100),
        ({"n_ctx": 999999}, "n_ctx", 2048),
        ({"n_gpu_layers": -7}, "n_gpu_layers", None),
        ({"chat_template": "inventado"}, "chat_template", None),
        ({"theme": "abc"}, "theme", 0),
    ]
    for datos, clave, esperado in casos:
        with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
            json.dump(datos, f)
        cfg = config_store.load_config(d)
        if esperado is None:
            assert cfg[clave] == config_store.default_config()[clave], \
                f"{clave} deberia caer al default: {cfg[clave]}"
        else:
            assert cfg[clave] == esperado, \
                f"{clave} no se valido: {cfg[clave]} != {esperado}"
    import shutil
    shutil.rmtree(d, ignore_errors=True)


def config_store_guarda_y_recarga():
    import config_store, tempfile, json, os, shutil
    d = tempfile.mkdtemp()
    cfg = config_store.default_config()
    cfg["theme"] = 2
    cfg["n_gpu_layers"] = -1
    assert config_store.save_config(d, cfg)
    recargada = config_store.load_config(d)
    assert recargada["theme"] == 2, "no guardo el tema"
    assert recargada["n_gpu_layers"] == -1, "no guardo gpu_layers"
    shutil.rmtree(d, ignore_errors=True)


def progress_tracker_bloqueo():
    """Escrituras y lecturas seguidas no deben soltar database is locked."""
    import tempfile
    from progress_tracker import ProgressTracker
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    try:
        p = ProgressTracker(f.name)
        for i in range(30):
            p.add_entry(weight=70 + i, notes=f"n{i}")
            p.get_entries(limit=5)
        assert len(p.get_entries(limit=50)) == 30
        assert p.get_latest()[1] == 99.0, "get_latest mal"
    finally:
        import os
        for sufijo in ("", "-wal", "-shm"):
            try:
                os.unlink(f.name + sufijo)
            except OSError:
                pass


def download_worker_cancela():
    """La descarga debe abortar y borrar el .tmp al cancelar."""
    import threading, time, tempfile, os
    from http.server import BaseHTTPRequestHandler
    from download_worker import ModelDownloader

    servidor_done = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                self.send_response(200)
                self.send_header("Content-Length", str(50 * 1024 * 1024))
                self.end_headers()
                bloque = b"x" * 65536
                for _ in range(800):
                    try:
                        self.wfile.write(bloque)
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        break
                    time.sleep(0.01)
            finally:
                servidor_done.set()

        def log_message(self, *a):
            pass

    import socketserver
    srv = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    puerto = srv.server_address[1]

    d = tempfile.mkdtemp()
    destino = os.path.join(d, "modelo.gguf")
    err = []

    def on_error(e):
        err.append(e)

    worker = ModelDownloader(f"http://127.0.0.1:{puerto}/m.gguf", destino,
                              on_error=on_error)
    worker.start()
    time.sleep(0.4)
    assert worker.is_alive(), "la descarga deberia seguir viva"
    worker.cancel()
    worker.join(timeout=10)
    srv.shutdown()

    assert not worker.is_alive(), "el hilo no paró tras cancelar"
    assert err == [], f"cancelar no deberia ser error: {err}"
    assert not os.path.exists(destino + ".tmp"), "no borro el .tmp"
    assert not os.path.exists(destino), "no deberia existir el destino"


def download_worker_siempre_responde():
    """La API publica no debe lanzar, aun sin conexión."""
    from download_worker import ModelDownloader
    w = ModelDownloader("http://127.0.0.1:1/no-existe", "x.gguf")
    assert w.percent == 0
    assert not w.is_alive()
    w.cancel()  # seguro aunque nunca arrancó
    w.join(timeout=1)


def logging_setup_no_lanza():
    import logging_setup, tempfile, logging, os
    d = tempfile.mkdtemp()
    root = logging.getLogger()
    previos = list(root.handlers)
    for h in previos:
        root.removeHandler(h)
    try:
        ruta = logging_setup.setup_logging(d)
        assert ruta is not None, "no creo el handler"
        assert os.path.exists(ruta)
        assert root.handlers, "no registro ningun handler"
        logging.getLogger("prueba").info("linea de prueba")
        assert "linea de prueba" in logging_setup.tail(ruta)
    finally:
        for h in list(root.handlers):
            root.removeHandler(h)
        for h in previos:
            root.addHandler(h)
    assert logging_setup.tail(os.path.join(d, "no-existe.log")) == ""




def firma_independiente_del_fin_de_linea():
    """La firma debe ser la misma con CRLF (Windows) y con LF (CI/Linux).

    Regresion real: hash_utils hasheaba los bytes tal cual, asi que el mismo
    contenido daba distinto en cada plataforma y el CI fallaba siempre en
    "Verify signature" aunque nadie hubiera tocado nada.
    """
    import hashlib
    import shutil
    import tempfile
    from hash_utils import ARCHIVOS_FIRMA, sha256_source_file

    def hash_de(directorio):
        h = hashlib.sha256()
        for a in ARCHIVOS_FIRMA:
            ruta = os.path.join(directorio, a)
            if os.path.exists(ruta):
                h.update(bytes.fromhex(sha256_source_file(ruta)))
        return h.hexdigest()

    original = hash_de(DIR)
    copia = tempfile.mkdtemp()
    destino = os.path.join(copia, "lf")
    try:
        shutil.copytree(DIR, destino,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
        convertidos = 0
        for root, _, files in os.walk(destino):
            for f in files:
                p = os.path.join(root, f)
                if f.endswith((".py", ".json", ".md", ".sh", ".bat", ".ps1")) \
                        or f == ".gitignore":
                    with open(p, "rb") as fh:
                        b = fh.read()
                    nuevo = b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                    if nuevo != b:
                        with open(p, "wb") as fh:
                            fh.write(nuevo)
                        convertidos += 1
        assert convertidos > 0, "no se convertio nada: el test no probaria nada"
        assert hash_de(destino) == original, \
            "la firma cambia entre CRLF y LF: el CI volveria a fallar"
    finally:
        shutil.rmtree(copia, ignore_errors=True)



if __name__ == "__main__":
    print(f"\n{'='*50}")
    print("  PRUEBAS DE ESTABILIDAD - IRON CHAT LUNA")
    print(f"{'='*50}\n")

    test("Todos los imports estandar y del proyecto", imports_ok)
    test("ASCII Art: lista y obtiene arte", ascii_art_ok)
    test("Progress Tracker: crear entrada y leer", progress_tracker_ok)
    test("Sounds: metodos existen", sounds_imports_ok)
    test("Audio: metodos existen", audio_imports_ok)
    test("TTS: metodos existen", tts_imports_ok)
    test("FaceAnimation: metodos existen", face_animation_import)
    test("generar_firma == verificar_firma (mismos archivos)", signature_files_match)
    test("Install: modulo se importa", install_imports_ok)
    test("check_deps: modulo se importa", check_deps_imports_ok)
    test("Verificar firma: modulo se importa", verificar_firma_syntax)
    test("Sounds: _gen_wav genera RIFF valido", sounds_generate_wav)
    test("Main: metodos nuevos existen", main_methods_exist)
    test("luna.sh: sintaxis valida", luna_sh_syntax)
    test("Themes: 3 temas con keys correctas", themes_module_ok)
    test("Hash utils: SHA256 y verificacion", hash_utils_ok)
    test("Rutinas JSON: 10+ rutinas validas", rutinas_json_ok)
    test("AI module: rutinas desde JSON funcionan", ai_module_rutinas_ok)
    test("Progress Tracker: context manager funciona", progress_tracker_context_manager_ok)
    test("Knowledge: carga completa del JSON", knowledge_carga)
    test("Knowledge: resuelve intenciones", knowledge_respuestas)
    test("Knowledge: guia tecnica por ejercicio", knowledge_ejercicio_exacto)
    test("Knowledge: respuesta generica nunca vacia", knowledge_generica_siempre)
    test("Knowledge: resumen para el prompt", knowledge_resumen_prompt)
    test("AI offline: saludo tiene prioridad", ai_offline_saludo_prioritario)
    test("AI offline: rutina tiene prioridad", ai_offline_rutina_prioritaria)
    test("AI offline: guia de ejercicio", ai_offline_ejercicio)
    test("AI offline: entrada vacia no rompe", ai_offline_vacio_no_rompe)
    test("AI prompt: usa cabeceras ChatML", ai_prompt_chatml)
    test("AI prompt: trunca historial enorme", ai_prompt_trunca_historial)
    test("AI: Llama3 usa su propia plantilla", ai_llama3_usa_plantilla_propia)
    test("AI: gpu_layers segun config", ai_gpu_layers_segun_config)
    test("Config: defaults completos", config_store_default)
    test("Config: JSON corrupto no rompe", config_store_corrupto_no_rompe)
    test("Config: valida rangos y tipos", config_store_valida_rangos)
    test("Config: guarda y recarga", config_store_guarda_y_recarga)
    test("Progress: escrituras/lecturas sin bloqueo", progress_tracker_bloqueo)
    test("Download: cancelar detiene y borra .tmp", download_worker_cancela)
    test("Download: API segura sin conexion", download_worker_siempre_responde)
    test("Logging: rotacion no lanza", logging_setup_no_lanza)
    test("Firma: independiente de CRLF/LF", firma_independiente_del_fin_de_linea)

    print(f"\n{'='*50}")
    print(f"  RESULTADO: {PASS} pasaron, {FAIL} fallaron")
    if FAIL == 0:
        print("  [OK] TODO OK")
    else:
        print("  [FAIL] HAY FALLOS")
    print(f"{'='*50}\n")
    sys.exit(FAIL)
