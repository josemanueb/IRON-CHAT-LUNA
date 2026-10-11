#!/usr/bin/env python3
"""Test de humo: la app arranca de verdad, no solo "existen los metodos".

Ejecuta ChatbotApp contra un display virtual (Xvfb en Linux, el display de
la sesion en Windows), procesa la cola de eventos y cierra. Un error al
construir la ventana, al crear un widget o al cargar una preferencia
revienta aqui, que es justo lo que el resto de tests no cubria.

Se ejecuta aparte de test_all.py porque necesita un display y tarda unos
segundos. El CI lo lanza en ambos sistemas operativos.
"""
import os
import sys
import traceback

DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)


def _bomba(ventana, segundos=1.5):
    """Procesa la cola de eventos durante unos segundos.

    Tkinter lanza 'main thread is not in main loop' si se llama a update()
    desde fuera de un mainloop real, asi que hay que entrar y salir de el.
    """
    import time
    tope = time.time() + segundos
    cont = 0
    while time.time() < tope and cont < 200:
        ventana.update()
        cont += 1
        time.sleep(0.005)


def main():
    try:
        import tkinter as tk
    except ImportError as e:
        print(f"  [SKIP] tkinter no disponible: {e}")
        return 0

    # Sin display en Linux: no es un fallo del proyecto, es del entorno.
    try:
        probe = tk.Tk()
        probe.destroy()
    except Exception as e:
        if "display" in str(e).lower():
            print(f"  [SKIP] sin display disponible: {e}")
            return 0
        raise

    app = None
    ventana = None
    try:
        import main as m

        # THEME_NAME solo existe si ttkbootstrap esta disponible.
        if getattr(m, "_HAS_TTB", False):
            import ttkbootstrap as tb
            ventana = tb.Window(themename=getattr(m, "THEME_NAME", "darkly"))
        else:
            ventana = tk.Tk()

        app = m.ChatbotApp(ventana)
        ventana.withdraw()

        # main() arranca estos hilos con after(0), ya dentro del mainloop.
        # El test reproduce ese orden exacto: si se arrancaran antes, el
        # fallo de after() desde hilo pasaria desapercibido.
        ventana.after(0, app.iniciar_hilos)
        _bomba(ventana, 3.0)

        assert ventana.winfo_exists(), "la ventana no se creo"
        assert app.root is ventana, "la app no guardo su ventana"
        assert getattr(app, "tts_enabled", None) is not None, \
            "no se cargo la configuracion"
        assert app.lang == "es", f"idioma inesperado: {app.lang!r}"
        assert app._ai_ready.wait(timeout=15), \
            "load_ai no termino: la IA no llego a cargarse"
        assert app.ai_loaded, "la app no marco la IA como cargada"
        # Sin modelo en disco la app cae a modo offline a proposito: lo que
        # no puede pasar es que load_ai quede a medias o lance.
        assert app._hilos_iniciados, "los hilos de arranque no llegaron a lanzarse"

        print("  [OK] La app arranca y procesa eventos")

        ventana.destroy()
        ventana = None
        return 0

    except Exception:
        print("  [FAIL] La app NO arranca:")
        for linea in traceback.format_exc().splitlines():
            print("         " + linea)
        return 1
    finally:
        try:
            if app is not None and getattr(app, "timer_running", False):
                app.timer_stop()
        except Exception:
            pass
        try:
            if ventana is not None:
                ventana.destroy()
        except Exception:
            pass
        # ttkbootstrap dispara un evento de tema al destruir la ventana que
        # puede quejarse si la app ya esta muerta. Es cosmetico.
        try:
            root = tk.Tk()
            root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())