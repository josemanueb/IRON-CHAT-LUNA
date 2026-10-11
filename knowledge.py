#!/usr/bin/env python3
"""Carga y consulta la base de conocimiento de LUNA (conocimiento.json).

Antes la base de conocimiento vivia como ~400 lineas de `if any(p in text ...)`
dentro de ai_module.py. Aqui es solo datos: se anade una categoria nueva
editando el JSON, sin tocar Python.

Este modulo mantiene el MISMO orden de prioridad que el codigo anterior
(saludo -> agradecimiento -> rutinas -> ...), porque ese orden forma parte
del comportamiento observable de LUNA.
"""
import json
import os
import random
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_PATH = os.path.join(DIR, "conocimiento.json")


def _load(path=None):
    """Carga el JSON de conocimiento. Devuelve {} si esta corrupto o ausente."""
    target = path or KNOWLEDGE_PATH
    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        cats = data.get("categorias")
        if not isinstance(cats, dict):
            return {}
        return data
    except (OSError, ValueError):
        return {}


_DATA = _load()

# Orden explicito: mismo que el codigo original en _offline_response().
# "rutinas" NO va aqui: vive en rutinas.json y se comprueba aparte.
CATEGORIAS = [c for c in (
    "saludo",
    "agradecimiento",
    "consejos",
    "calentamiento",
    "estiramientos",
    "descanso",
    "hidratacion",
    "suplementos",
    "lesiones",
    "dieta_volumen",
    "dieta_definicion",
    "dieta_vegana",
    "dieta_saludable",
    "ejercicios",
    "motivacion",
    "progresion",
    "comandos",
    "recordatorio",
    "musica",
    "frase",
    "despedida",
    "offline",
    "ascii_art",
) if c in _DATA.get("categorias", {})]

EJERCICIOS = _DATA.get("ejercicios", {})
RESPUESTAS_GENERICAS = _DATA.get("respuestas_genericas", [])

# Indice inverso: keyword -> nombre de categoria. Permite localizar en O(1)
# el candidato por palabra suelta antes de comprobar la categoria completa.
_INDICE = {}
for _cat in CATEGORIAS:
    _entrada = _DATA["categorias"][_cat]
    for _kw in _entrada.get("keywords", []):
        _INDICE.setdefault(_kw.lower(), _cat)


def _pick(entrada):
    """Devuelve la respuesta de una entrada. Si tiene lista y random, elige una."""
    resp = entrada.get("response")
    if isinstance(resp, list):
        if not resp:
            return None
        return random.choice(resp)
    return resp


def _norm(text):
    return (text or "").lower().strip()


def find_categoria(user_input):
    """Devuelve el nombre de la primera categoria que coincide, o None.

    Recorre CATEGORIAS en el orden declarado, que es el orden de prioridad
    del comportamiento de LUNA. Las categorias con "special" se saltan aqui
    porque las resuelve el llamador (ascii_art necesita contexto extra).
    """
    text = _norm(user_input)
    if not text:
        return None
    cats = _DATA.get("categorias", {})
    for cat in CATEGORIAS:
        entrada = cats.get(cat)
        if not entrada or entrada.get("special"):
            continue
        for kw in entrada.get("keywords", []):
            if kw.lower() in text:
                return cat
    return None


def find_categoria_categoria(cat, user_input):
    """Comprueba SOLO la categoria indicada.

    Se usa para dar prioridad explicita a saludo/agradecimiento antes de
    rutinar el resto: "hola, dame rutina de pecho" debe saludar primero.
    """
    text = _norm(user_input)
    if not text or not cat:
        return None
    entrada = _DATA.get("categorias", {}).get(cat)
    if not entrada or entrada.get("special"):
        return None
    for kw in entrada.get("keywords", []):
        if kw.lower() in text:
            return cat
    return None


def get_categoria_response(cat):
    """Texto de una categoria, o None si no aplica."""
    entrada = _DATA.get("categorias", {}).get(cat)
    if not entrada:
        return None
    return _pick(entrada)


def find_ejercicio(user_input):
    """Guia tecnica de un ejercicio concreto, o None."""
    text = _norm(user_input)
    if not text:
        return None
    for nombre, descripcion in EJERCICIOS.items():
        if nombre.lower() in text:
            return descripcion
    return None


def es_peticion_ascii(user_input):
    """True si el usuario pide explicitamente un dibujo ASCII."""
    text = _norm(user_input)
    entrada = _DATA.get("categorias", {}).get("ascii_art", {})
    return any(kw.lower() in text for kw in entrada.get("keywords", []))


def es_peticion_ejercicio(user_input):
    """True si la entrada habla de tecnica de ejercicios (no solo de una rutina)."""
    return find_categoria(user_input) == "ejercicios"


# El JSON podria venir sin lista de genericas; en ese caso usamos un texto fijo.
RESPUESTAS_GENERICAS_FALLBACK = (
    "💪 ¡A darle! Puedo ayudarte con rutinas, nutrición o lo que necesites."
)


def respuesta_generica():
    """Respuesta por defecto cuando nada coincide."""
    if RESPUESTAS_GENERICAS:
        return random.choice(RESPUESTAS_GENERICAS)
    return RESPUESTAS_GENERICAS_FALLBACK


def resumen_para_prompt(max_chars=1200):
    """Resumen compacto de la base de conocimiento para inyectar en el prompt
    del modelo real, para que LUNA no pierda las rutinas que ya sabe offline."""
    partes = []
    for cat in CATEGORIAS:
        entrada = _DATA["categorias"][cat]
        if entrada.get("special"):
            continue
        resp = entrada.get("response")
        texto = resp[0] if isinstance(resp, list) and resp else resp
        if not texto:
            continue
        partes.append(f"[{cat}] {texto}")
    resumen = "\n".join(partes)
    if len(resumen) > max_chars:
        resumen = resumen[:max_chars].rsplit("\n", 1)[0]
    return resumen


def stats():
    """Metricas para tests y para el panel de creditos."""
    return {
        "categorias": len(CATEGORIAS),
        "keywords": sum(
            len(_DATA["categorias"][c].get("keywords", [])) for c in CATEGORIAS
        ),
        "ejercicios": len(EJERCICIOS),
        "genericas": len(RESPUESTAS_GENERICAS),
        "disponible": bool(CATEGORIAS),
    }


if __name__ == "__main__":
    # Utilidad: imprime metricas y sirve para depurar la carga.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    info = stats()
    print("Base de conocimiento LUNA")
    print(f"  categorias:  {info['categorias']}")
    print(f"  keywords:    {info['keywords']}")
    print(f"  ejercicios:  {info['ejercicios']}")
    print(f"  genericas:   {info['genericas']}")
    if not info["disponible"]:
        print("  AVISO: no se pudo cargar conocimiento.json", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(0)