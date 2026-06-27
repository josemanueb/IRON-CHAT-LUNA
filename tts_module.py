import os
import threading
import platform
import tempfile
import re
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
        """Linux: usa Piper TTS (paquete Python) con voz femenina española"""
        voices_dir = os.path.join(os.path.dirname(__file__), "voices")
        
        # Verificar que el paquete Python piper-tts está disponible
        try:
            from piper import PiperVoice
            self.piper_available = True
        except ImportError:
            print("⚠️ Paquete piper-tts no instalado en el venv")
            print("⚠️ TTS no disponible, modo texto")
            self.piper_available = False
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
                print(f"✅ TTS Linux: Piper (Python) con voz {tipo} española ({voz})")
                return
        
        print("⚠️ No se encontraron voces Piper en la carpeta voices/")
        print("⚠️ TTS no disponible, modo texto")

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
    
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
        if self.engine_w:
            self.engine_w.say(text)
            self.engine_w.runAndWait()
    
    def _speak_piper(self, text):
        """Usa Piper TTS (paquete Python) con voz femenina española"""
        try:
            from piper import PiperVoice
            import wave
            
            # Limpiar texto
            texto_limpio = re.sub(r'[^\w\s,;:.!?¡¿áéíóúüñÁÉÍÓÚÜÑ]', ' ', text)
            texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
            
            if not texto_limpio:
                return
            
            # Cargar voz
            voice = PiperVoice.load(self.voice_path)
            
            # Generar WAV en memoria
            wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            wav_path = wav_file.name
            wav_file.close()
            
            with wave.open(wav_path, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(voice.config.sample_rate)
                for audio_chunk in voice.synthesize(texto_limpio):
                    wav.writeframes(audio_chunk.audio_int16_bytes)
            
            # Reproducir el WAV esperando a que termine
            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
                if self.sistema == "Windows":
                    Audio.play_wav(wav_path)
                    import time
                    time.sleep(1.0)
                else:
                    sound = Audio.load_wav(wav_path)
                    if sound:
                        import time
                        time.sleep(sound.get_length())
            
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
