import os
import threading
import subprocess
import platform
import tempfile
import re
import time
import shutil
from audio import Audio

class TTS:
    def __init__(self):
        print("Inicializando TTS...")
        self.speaking = False
        self.on_finish_callback = None
        self.volume = 0.7
        self.sistema = platform.system()
        self.mode = "offline"

        if self.sistema == "Windows":
            self._init_windows()
        else:
            self._init_linux()

    def _init_windows(self):
        try:
            import pyttsx3
            self.engine_w = pyttsx3.init()
            self.engine_w.setProperty('rate', 150)
            self.engine_w.setProperty('volume', self.volume)
            voices = self.engine_w.getProperty('voices')
            for v in voices:
                if 'spanish' in v.name.lower() or 'es' in v.id.lower() or 'helena' in v.name.lower():
                    self.engine_w.setProperty('voice', v.id)
                    break
            self.mode = "windows_tts"
            print("✅ TTS Windows listo (voz natural del sistema)")
        except Exception:
            print("⚠️ TTS Windows no disponible")

    def _init_linux(self):
        self.espeak_bin = shutil.which("espeak-ng")
        if self.espeak_bin:
            self.mode = "espeak"
            print(f"✅ TTS Linux listo (espeak-ng)")
        else:
            print("⚠️ espeak-ng no instalado. Sin TTS en Linux.")
            print("   Instala con: sudo apt install espeak-ng")
            self.mode = "none"

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))

    def set_speed(self, speed_pct):
        if self.sistema == "Windows" and hasattr(self, 'engine_w') and self.engine_w:
            rate = int(150 * speed_pct / 100)
            self.engine_w.setProperty('rate', rate)

    def speak(self, text, on_finish=None):
        if not text:
            if on_finish:
                on_finish()
            return
        self.on_finish_callback = on_finish
        self.speaking = True
        thread = threading.Thread(target=self._speak_thread, args=(text,))
        thread.daemon = True
        thread.start()

    def _speak_thread(self, text):
        try:
            if self.mode == "windows_tts":
                self._speak_windows(text)
            elif self.mode == "espeak":
                self._speak_espeak(text)
        except Exception as e:
            print(f"Error en TTS: {e}")
        finally:
            self.speaking = False
            if self.on_finish_callback:
                try:
                    self.on_finish_callback()
                except Exception:
                    pass

    def _speak_windows(self, text):
        if hasattr(self, 'engine_w') and self.engine_w:
            try:
                self.engine_w.say(text)
                self.engine_w.runAndWait()
            except Exception:
                # pyttsx3 can crash on repeated calls; reinitialize
                try:
                    import pyttsx3
                    self.engine_w = pyttsx3.init()
                    self.engine_w.setProperty('rate', 150)
                    self.engine_w.setProperty('volume', self.volume)
                    self.engine_w.say(text)
                    self.engine_w.runAndWait()
                except Exception:
                    pass

    def _speak_espeak(self, text):
        try:
            texto_limpio = re.sub(r'[^\w\s,;:.!?¡¿áéíóúüñÁÉÍÓÚÜÑ]', ' ', text)
            texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
            if not texto_limpio:
                return

            wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            wav_path = wav_file.name
            wav_file.close()

            amp = max(30, int(self.volume * 100))
            cmd = [
                self.espeak_bin,
                '-v', 'es',
                '-s', '140',
                '-a', str(amp),
                '-w', wav_path,
                texto_limpio,
            ]
            subprocess.run(cmd, capture_output=True, timeout=30)

            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 100:
                Audio.play_wav(wav_path)
                time.sleep(0.3)

            try:
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
            except Exception:
                pass
        except Exception as e:
            print(f"Error en espeak-ng TTS: {e}")

    def stop(self):
        Audio.stop_all()
        self.speaking = False
