# IRON-CHAT-LUNA — Informe de reparación

Fecha: 2026-10-11
Origen: `josemanueb/IRON-CHAT-LUNA` rama `main` (commit `b09258a`)
Copia reparada: `IRON-CHAT-LUNA-fixed/` + `IRON-CHAT-LUNA-fixed.zip`

Verificación final:
- `py_compile` de los 14 .py: OK
- `test_all.py`: **19 pasaron, 0 fallaron**
- `verificar_firma.py`: **Firma válida** (regenerada con `generar_firma.py`)

## Fallos encontrados y corregidos

1. **`lang.py::get_available_languages()` rota (NameError 100%)**
   - Usaba la variable inexistente `lang_code` dentro de un dict-comprehension.
   - Cualquier llamada (menú de idioma, tests) rompía la app.
   - Fix: devuelve `dict(LANG_NAMES)`. Además `_toggle_lang()` ahora usa
     `lang.set_language()` en vez de asignar `lang.LANG` a mano.

2. **`test_all.py` se rompía en Windows (UnicodeEncodeError con cp1252)**
   - Los `print("✅ ...")` / `print("❌ ...")` petan en consolas Windows sin UTF-8,
     y el propio harness de tests moría antes de informar.
   - Fix: reconfigura stdout/stderr a UTF-8 con `errors="replace"` y usa
     marcadores ASCII `[OK]` / `[FAIL]` en los nombres de test.
   - También se eliminó el doble `from PIL import` (el segundo era incondicional
     y contradecía el bloque try/except anterior): ahora si falta Pillow falla
     con mensaje claro `Falta Pillow: pip install Pillow`.

3. **`test_download.py`: orden de `except` incorrecto**
   - `urllib.error.HTTPError` es subclase de `URLError`; el `except URLError`
     estaba antes y tragaba los HTTPError (el handler específico era inalcanzable,
     y los 401/403 nunca mostraban su mensaje).
   - Fix: `HTTPError` primero, `URLError` después (igual que ya hace `main.py`).

4. **`face_animation.py` y `main.py`: `from PIL import` incondicional**
   - Si Pillow no está instalado, la app no arranca ni en modo offline.
   - Fix: import protegido con `_HAS_PIL`; la cara animada usa fallback
     (óvalo + emoji) y el fondo/iconos se saltan si no hay PIL.

5. **`main.py`: la configuración guardada no se aplicaba nunca**
   - `cargar_configuracion()` se llamaba pero `tema_actual`, volúmenes y
     `tts_enabled` se fijaban a valores hardcodeados justo después.
   - Además había un bug grave: `self.progress = ProgressTracker(...)` y dos
     líneas después `self.progress = None` → el seguimiento de progreso quedaba
     **siempre deshabilitado**.
   - Fix: se aplica `CONFIG["theme"]`, `tts_volume`, `music_volume`,
     `tts_speed`, `tts_enabled` a la UI; se fusiona el JSON con
     `DEFAULT_CONFIG` (claves desconocidas se ignoran, valores se validan);
     y `toggle_theme` / `cambiar_volumen*` / `toggle_tts` ahora guardan en
     `config.json`.
   - El idioma se inicializa con `lang.set_language("es")`.

6. **`main.py::_view_progress`: deltas invertidos + crash con `0.0`**
   - `get_entries()` devuelve newest-first pero el bucle comparaba cada fila
     con la anterior de la lista (= la medición POSTERIOR), así que subir de
     80→82 kg mostraba bajada.
   - Además `f"{v:.1f}" if v else "-"` trataba `0.0` como ausente.
   - Fix: se recorre en orden cronológico, se calculan deltas correctos
     (`+x.x` / `-x.x`) y se muestra newest-first. Se usa `v is not None`.

7. **`tts_module.py::_speak_windows`: recursión infinita**
   - En `except: self.engine_w = None; self._speak_windows(text)` reintentaba
     sin límite → `RecursionError` si el motor seguía fallando.
   - Fix: un solo reintento (`_retried` flag).

8. **`main.py::_stream_response`: bloqueo eterno**
   - `started.wait()` sin timeout: si la UI no responde, el hilo se queda
     colgado para siempre.
   - Fix: `started.wait(timeout=10)` con log y finalización segura.

9. **Sin handler de cierre de ventana**
   - Cerrar la ventana no paraba TTS/música/temporizador ni guardaba
     historial/config.
   - Fix: `root.protocol("WM_DELETE_WINDOW", _on_close)` que para todo,
     guarda historial + config y destruye la ventana.

10. **Scripts de consola rompían en Windows (cp1252)**
    - `check_deps.py`, `generar_firma.py`, `verificar_firma.py` imprimen
      emojis → `UnicodeEncodeError` en PowerShell/cmd.
    - Fix: `sys.stdout/stderr.reconfigure(encoding="utf-8", errors="replace")`.
    - En `check_deps.py` además se quitaron em-dashes (`—`) de mensajes clave.

11. **CI `.github/workflows/test.yml` regeneraba la firma en cada run**
    - `python generar_firma.py` SOBRESCRIBE `SIGNATURE.md` con un hash nuevo,
      así que el "check" siempre pasaba y nunca detectaba manipulaciones.
    - Fix: ahora corre `python verificar_firma.py` (falla si hay cambios).

12. **Firma regenerada**
    - `SIGNATURE.md` actualizado al hash de la copia reparada
      (`e3f3268c...be40b`, 2026-10-11). `verificar_firma.py` → OK.

## Archivos modificados (respecto a `main` de GitHub)

- `lang.py` — fix `get_available_languages`
- `test_all.py` — UTF-8 + ASCII markers + Pillow con mensaje claro
- `test_download.py` — orden HTTPError/URLError
- `face_animation.py` — PIL opcional
- `main.py` — PIL opcional, config persistente, fix progress=None,
  deltas cronológicos, stream timeout, handler WM_DELETE_WINDOW,
  `set_language()`
- `tts_module.py` — reintento único en Windows
- `check_deps.py` — UTF-8 + mensajes sin em-dash
- `generar_firma.py`, `verificar_firma.py` — UTF-8
- `.github/workflows/test.yml` — verificar en vez de regenerar
- `SIGNATURE.md` — hash regenerado

## Cómo subirlo a tu repo

No puedo hacer push sin tu token de GitHub, así que desde tu PC:

```powershell
# Opción A: sustituir tu carpeta local y pushear
Expand-Archive -Force IRON-CHAT-LUNA-fixed.zip .
cd IRON-CHAT-LUNA
git add -A
git commit -m "fix: lang NameError, PIL opcional, config persistente, deltas progreso, TTS/stream robustos, CI verifica firma"
git push origin main
```

```bash
# Opción B (Linux)
unzip -o ../IRON-CHAT-LUNA-fixed.zip -d IRON-CHAT-LUNA-fixed
cp -r IRON-CHAT-LUNA-fixed/* IRON-CHAT-LUNA/
cd IRON-CHAT-LUNA
git add -A
git commit -m "fix: lang NameError, PIL opcional, config persistente, deltas progreso, TTS/stream robustos, CI verifica firma"
git push origin main
```

Luego en GitHub verás el workflow `Test` en verde (19/19) y la firma válida.
