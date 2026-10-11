# IRON-CHAT-LUNA — Informe de reparación

Fecha: 2026-10-11
Origen: `josemanueb/IRON-CHAT-LUNA` rama `main` (commit `b09258a`)

---

# Parte 1 — Reparación de bugs (v2.2)

Verificación de esa fase:
- `py_compile` de los 14 .py: OK
- `test_all.py`: **19 pasaron, 0 fallaron**
- `verificar_firma.py`: **Firma válida**

## Fallos encontrados y corregidos

1. **`lang.py::get_available_languages()` rota (NameError 100%)**
   - Usaba la variable inexistente `lang_code` dentro de un dict-comprehension.
   - Cualquier llamada (menú de idioma, tests) rompía la app.
   - Fix: devuelve `dict(LANG_NAMES)`. Además `_toggle_lang()` ahora usa
     `lang.set_language()` en vez de asignar `lang.LANG` a mano.

2. **`test_all.py` se rompía en Windows (UnicodeEncodeError con cp1252)**

3. **`test_download.py`: orden de `except` incorrecto**
   - `except HTTPError` debe ir antes de `except URLError`, porque `HTTPError`
     hereda de `URLError` y la rama de red nunca se alcanzaba.

4. **`face_animation.py` / `main.py`: Pillow obligatorio**
   - Importar la app sin Pillow lanzaba `ImportError`.
   - Fix: import protegido + fallback a un óvalo con emoji.

5. **`main.py`: `self.progress = None` anulaba el progreso**
   - Se inicializaba `ProgressTracker` y justo después se sobrescribía con
     `None`, dejando el panel de progreso muerto siempre.

6. **`main.py`: ajustes de la UI nunca se aplicaban**
   - Tema, volumen de música, volumen TTS y velocidad TTS se leían pero no
     se inicializaban desde la configuración, y no se guardaban al cambiar.

7. **`main.py::_view_progress`: deltas invertidos**
   - Recorría las entradas en orden inverso al cronológico, así que las
     variaciones aparecían con el signo cambiado.

8. **`tts_module.py`: recursión infinita**
   - `_speak_windows()` se llamaba a sí misma sin guardia.

9. **`main.py::_stream_response`: `started.wait()` sin timeout**
   - Si la UI no arriveaba, el hilo de inferencia quedaba colgado para siempre.

10. **Cierre de ventana sin limpieza**
    - `root.protocol("WM_DELETE_WINDOW", ...)` guardaba historial y paraba
      timers, TTS y audio.

11. **Scripts que rompían en consola Windows**
    - `check_deps.py`, `generar_firma.py` y `verificar_firma.py` fallaban con
      `UnicodeEncodeError` (cp1252) al imprimir emojis.

12. **El CI regeneraba la firma en vez de verificarla**
    - `test.yml` ejecutaba `generar_firma.py`, así que la comprobación de
      integridad era automática y no detectaba nada.
    - Fix: `python verificar_firma.py`.

---

# Parte 2 — Mejoras (v2.3)

Partiendo del código ya reparado, se implementaron 15 mejoras. Todas
verificadas: **`test_all.py` = 40 pasaron, 0 fallaron** y firma válida.

## Alta prioridad

### 1. La descarga del modelo ya se puede cancelar de verdad
`main.py::_do_download` era un hilo monolitico sin forma de pararlo: el
`WM_DELETE_WINDOW` del diálogo era `lambda: None`, así que cerrar la ventana
no hacía nada y la descarga seguía hasta el final.

- Nuevo módulo **`download_worker.py`**: `ModelDownloader` con
  `threading.Event` de cancelación, comprobada **antes de cada chunk**, que
  borra el `.tmp` parcial y reintenta `os.replace` si el antivirus bloquea.
- `main.py` ahora solo orquesta: `_do_download` crea el worker, y
  `_cancel_download` lo aborta. El botón CANCELAR y cerrar el diálogo hacen
  lo mismo. `_on_close` también cancela al salir.
- Test real con un servidor HTTP local: comprueba que el hilo para, que no
  deja `.tmp` y que no lanza.

### 2. Autodetección de GPU
`n_gpu_layers=0` estaba fijo: siempre CPU, aunque el usuario tuviera GPU.
Ahora `_resolve_gpu_layers()` usa `llama_cpp.llama_supports_gpu_offload()` y
permite override con `n_gpu_layers` en `config.json` (`-1` autodetecta,
`0` fuerza CPU).

### 3. El contexto ya no se desborda
El historial se truncaba por *número de mensajes*, no por tokens. Ahora
`_build_prompt()` calcula un presupuesto a partir de `n_ctx` y
`max_tokens`, descarta los turnos antiguos y **siempre conserva entero el
turno actual**. `n_ctx`, `max_tokens` y `n_threads` son configurables.

### 4. Stop tokens reales
`_stop_tokens()` devolvía `["", ""]`, que en llama.cpp es degenerado: **no
detenía nada** y la generación se comía los `max_tokens` enteros. Ahora
devuelve los tokens de fin del formato de chat (`<|im_end|>` o `<|eot_id|>`).

Además el prompt usaba `f"system\n{sys}\nuser\n{text}"`, que **no es un
formato de chat real**. Ahora se usan plantillas ChatML (Qwen, Llama-3) y
Llama-3, con override mediante `chat_template` en `config.json`.

### 5. SQLite sin bloqueos
`sqlite3.connect()` sin `busy_timeout`: si el panel de progreso escribía
mientras se consultaba, saltaba `database is locked`. Ahora lleva `timeout=5`
y `journal_mode=WAL`. Además se añadió `get_latest()` y `delete_entry()`.

## Media prioridad

### 6. `main.py` con la lógica pesada extraída
El objetivo no era reducir el fichero, sino **sacar lo testeable**: la
configuración, el logging, la descarga y la base de conocimiento tienen
ahora sus propios tests, que corren sin levantar Tkinter. `main.py` queda en
1743 líneas y su mayor parte sigue siendo UI, pero lo que sí se puede testear
ya se testea.

| Módulo nuevo | Qué hace |
|---|---|
| `config_store.py` | Config validada por tipo y rango |
| `logging_setup.py` | Logging con rotación |
| `download_worker.py` | Descargas cancelables |
| `knowledge.py` | Base de conocimiento |

### 7. La base de conocimiento es ahora dato, no código
`ai_module._offline_response` eran **~334 líneas de `if any(p in text ...)`**.
Ahora:
- **`conocimiento.json`** — 23 categorías, 152 keywords, 10 ejercicios.
- **`knowledge.py`** — índice y resolución.
- **Añadir contenido ya no requiere tocar Python.**

El orden de prioridad se conservó a propósito, porque es comportamiento
observable: "hola, dame rutina de pecho" debe saludar primero.

`ai_module.py` pasó de 614 a **485 líneas**, y los ~334 de
`_offline_response` viven ahora en `knowledge.py` como datos.

### 8. El modelo real ya no pierde las rutinas
Con un GGUF cargado, `_system_prompt()` no incluía los textos de rutinas y
dietas: LUNA sabíaOffline cosas que al cargar el modelo olvidaba. Ahora se
inyecta un resumen de la base de conocimiento en el prompt.

### 9. Menos `except Exception` silenciosos
Los `except` críticos ahora registran con `logging` en vez de tragarse el
error (p. ej. el del reloj, que ocultaba fallos de Tkinter).

### 10. Tests de lógica real (19 → 41)
Antes se comprobaba que los métodos **existieran**. Ahora se prueba que
**funcionen**: config corrupta, rangos, template de chat, truncado de
contexto, detección de GPU, orden de prioridad del offline, cancelación de
descarga, bloqueo de SQLite y rotación del log.

## Baja prioridad

### 11. `LICENSE` GPL-3.0
El repositorio no tenía licencia, así que GitHub lo trataba como "todos los
derechos reservados" y nadie podía reutilizarlo ni contribuir legalmente.

### 12. Rotación de `iron_chat.log`
`basicConfig` sin `RotatingFileHandler`: el log crecía sin límite. Ahora
2 MB × 3 rotaciones.

### 13. `.gitignore` corregido
Ignoraba `historial.json`, `memorias.json` y `progreso.db`, pero **no**
`config.json`, que contiene preferencias del usuario. Añadido, junto con
`*.db-wal`, `*.db-shm` y los scripts de parche.

### 14. CI también en Windows
El workflow solo corría en `ubuntu-latest`, y la app es multiplataforma con
ramas por SO en TTS/audio. Ahora corre en `ubuntu-latest` **y**
`windows-latest`, compila los módulos nuevos y valida
`install_windows.ps1` con el parser de PowerShell.

### 15. La firma de integridad era frágil ante el fin de línea
Este lo encontró el propio CI nuevo: los 5 jobs fallaron en *Verify signature*.

**Causa**: `hash_utils` hasheaba los bytes tal cual. Git guarda LF en el
índice, un checkout en Windows escribe CRLF, así que **los mismos bytes
lógicos daban un hash distinto en cada plataforma**. Localmente daba
`✅` y en CI `❌`, sin que nadie hubiera modificado nada.

**Fix**: `sha256_source_file()` normaliza CRLF/CR a LF antes de hashear.
`sha256_file()` se mantiene en bruto para binarios (los modelos GGUF deben
verificarse byte a byte, sin normalizar).

Hay un test que lo blinda: comprueba la firma en las **dos** direcciones (a
LF y a CRLF), porque si solo prueba una el test no significa nada en la otra
plataforma.

### 16. `test_download.py`: descarga fallida con resultado "correcto"
Otro que salió al ampliar el CI. El bloque estaba así:

```python
except urllib.error.URLError as e:

except Exception as e:
```

Sin red, sin DNS o con el servidor caído, la excepción se consumía y el
script **terminaba con código 0**, dando por buena una descarga que nunca
había ocurrido. Ahora informa del fallo, borra el `.tmp` y sale con código 1.

### 17. El CI compilaba una lista de ficheros a mano
El paso *Syntax check* hacía `py_compile` de 14 ficheros escritos a mano, y
`test_download.py` no estaba en la lista, así que su error de sintaxis era
invisible. Ahora compila **todos** los `.py` del proyecto con `compileall`,
así que el próximo fichero roto no puede colarse por la lista.

---

## Archivos nuevos

| Fichero | Para qué |
|---|---|
| `knowledge.py` | Índice y resolución de la base de conocimiento |
| `conocimiento.json` | 23 categorías, 152 keywords, 10 ejercicios |
| `config_store.py` | Configuración validada por tipo y rango |
| `download_worker.py` | Descargas cancelables |
| `logging_setup.py` | Logging con rotación |
| `LICENSE` | GPL-3.0 |

## Verificación final de la v2.3

```
test_all.py:  41 pasaron, 0 fallaron
verificar_firma.py:  Firma válida (32 archivos)
py_compile:  18 módulos OK
firma estable entre CRLF y LF:  OK
```