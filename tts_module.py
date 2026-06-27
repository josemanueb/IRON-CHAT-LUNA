import os
import threading
import subprocess
import platform
import tempfile
import re
import time
from audio import Audio

class TTS:
    def __init__(self):
        print("Inicializando TTS con Piper real...")
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
        """Windows: usa pyttsx3 con voces SAPI5"""
        self.engine_w = None
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
            print("✅ TTS Windows listo (voz natural)")
        except:
            print("⚠️ TTS Windows no disponible")
    
    def _init_linux(self):
        """Linux: usa Piper TTS real con voz femenina española"""
        voices_dir = os.path.join(os.path.dirname(__file__), "voices")
        
        # Buscar piper-tts real (el que descargamos)
        piper_paths = [
            "/usr/local/bin/piper-tts",  # El que acabamos de instalar
            "/usr/local/bin/piper",       # Por si acaso
        ]
        
        self.piper_bin = None
        for p in piper_paths:
            if os.path.exists(p):
                self.piper_bin = p
                break
        
        if not self.piper_bin:
            print("⚠️ Piper TTS no encontrado en /usr/local/bin")
            print("⚠️ TTS no disponible, modo texto")
            self.mode = "none"
            return
        
        # Buscar voz femenina española (preferida) o masculina
        voces = [
            ("es_ES-sharvard-medium.onnx", "femenina"),
            ("es_ES-carlfm-x_low.onnx", "masculina"),
        ]
        
        for voz, tipo in voces:
            ruta = os.path.join(voices_dir, voz)
            if os.path.exists(ruta):
                self.voice_path = ruta
                self.mode = "piper"
                print(f"✅ TTS Linux: Piper real con voz {tipo} española ({voz})")
                print(f"   Binario: {self.piper_bin}")
                return
        
        print("⚠️ No se encontraron voces Piper en la carpeta voices/")
        print("⚠️ TTS no disponible, modo texto")
        self.mode = "none"

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))

    def set_speed(self, speed_pct):
        """speed_pct: 50-200 (100 = normal)"""
        if self.sistema == "Windows" and self.engine_w:
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
            elif self.mode == "piper":
                self._speak_piper(text)
        except Exception as e:
            print(f"Error en TTS: {e}")
        finally:
            self.speaking = False
            if self.on_finish_callback:
                try:
                    self.on_finish_callback()
                except:
                    pass
    
    def _speak_windows(self, text):
        if getattr(self, 'engine_w', None):
            self.engine_w.say(text)
            self.engine_w.runAndWait()
    
    def _speak_piper(self, text):
        """Usa Piper TTS real con voz femenina española"""
        try:
            # Limpiar texto
            texto_limpio = re.sub(r'[^\w\s,;:.!?¡¿áéíóúüñÁÉÍÓÚÜÑ]', ' ', text)
            texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
            
            if not texto_limpio:
                return
            
            # Generar WAV con Piper TTS
            wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            wav_path = wav_file.name
            wav_file.close()
            
            cmd = [
                self.piper_bin,
                '--model', self.voice_path,
                '--output_file', wav_path,
            ]
            
            with subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ) as proc:
                proc.communicate(input=texto_limpio.encode('utf-8'), timeout=60)
            
            # Reproducir el WAV
            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
                Audio.play_wav(wav_path)
                time.sleep(0.5)
            
            # Limpiar
            try:
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
            except:
                pass
                
        except Exception as e:
            print(f"Error en Piper TTS: {e}")
    
    def stop(self):
        Audio.stop_all()
        self.speaking = False
