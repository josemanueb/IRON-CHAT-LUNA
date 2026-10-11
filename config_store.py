#!/usr/bin/env python3
"""Configuracion persistente de LUNA (config.json), validada.

Extraido de main.py para que la validacion se pueda testear sin abrir
Tkinter. Cada ajuste declara su tipo y su rango, y load_config() garantiza
que un config.json corrupto o editado a mano nunca rompa el arranque:
lo que no cuadra se sustituye por el default.
"""
import json
import os

CONFIG_FILENAME = "config.json"

# tipo: (defecto, minimo, maximo)
SCHEMA = {
    "theme":            (0, 0, None),
    "tts_enabled":      (True, None, None),
    "music_volume":     (50, 0, 100),
    "tts_volume":       (70, 0, 100),
    "tts_speed":        (100, 50, 200),
    "sidebar_collapsed": (False, None, None),
    "last_window_geometry": (None, None, None),
    # Ajustes del modelo (mejora #2/#3/#4)
    "n_ctx":            (2048, 512, 32768),
    "max_tokens":       (500, 64, 4096),
    "n_threads":        (None, 1, 256),
    "n_gpu_layers":     (None, None, None),  # -1 = autodetectar
    "chat_template":    (None, None, None),  # chatml | llama3 | plain
}


def default_config():
    return {k: v[0] for k, v in SCHEMA.items()}


def _coerce(key, value):
    """Convierte y valida un valor. Devuelve (ok, valor_normalizado)."""
    defecto, minimo, maximo = SCHEMA[key]

    if key == "tts_enabled":
        if isinstance(value, bool):
            return True, value
        return False, defecto

    if key == "sidebar_collapsed":
        if isinstance(value, bool):
            return True, value
        return False, defecto

    if key == "last_window_geometry":
        if isinstance(value, str) and value:
            return True, value
        return False, defecto

    if key == "chat_template":
        if value in ("chatml", "llama3", "plain"):
            return True, value
        return False, defecto

    if key == "n_gpu_layers":
        # -1 significa autodetectar; 0 fuerza CPU; n>=1 fuerza n capas.
        try:
            n = int(value)
        except (TypeError, ValueError):
            return False, defecto
        if n < -1:
            return False, defecto
        return True, n

    # Resto: enteros con rango.
    try:
        n = int(value)
    except (TypeError, ValueError):
        return False, defecto
    if minimo is not None and n < minimo:
        return False, defecto
    if maximo is not None and n > maximo:
        return False, defecto
    return True, n


def load_config(project_dir):
    """Lee config.json y devuelve un dict valido (siempre completo)."""
    config = default_config()
    path = os.path.join(project_dir, CONFIG_FILENAME)
    if not os.path.exists(path):
        return config
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return config
    if not isinstance(data, dict):
        return config
    for key, value in data.items():
        if key not in SCHEMA:
            continue  # clave desconocida: se ignora, no rompe
        ok, normalizado = _coerce(key, value)
        if ok:
            config[key] = normalizado
    # El tema siempre dentro del rango de themes.py.
    try:
        from themes import theme_count
        config["theme"] = int(config["theme"]) % max(1, theme_count())
    except Exception:
        config["theme"] = 0
    return config


def save_config(project_dir, config):
    """Guarda config.json de forma atomica. Nunca lanza."""
    path = os.path.join(project_dir, CONFIG_FILENAME)
    tmp = path + ".tmp"
    try:
        limpio = {k: config.get(k, v[0]) for k, v in SCHEMA.items()}
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(limpio, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except OSError:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        return False