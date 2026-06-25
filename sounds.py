import pygame
import os
import threading

class Sounds:
    _initialized = False
    _project_dir = os.path.dirname(os.path.abspath(__file__))
    
    @classmethod
    def _init(cls):
        if not cls._initialized:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=1)
                cls._initialized = True
            except:
                pass
    
    @classmethod
    def play_startup(cls):
        """Sonido de inicio - tu archivo personalizado"""
        cls._init()
        def _play():
            try:
                wav_path = os.path.join(cls._project_dir, "iniciodesesion.wav")
                if os.path.exists(wav_path):
                    sound = pygame.mixer.Sound(wav_path)
                    sound.play()
                    # Esperar que termine
                    pygame.time.wait(int(sound.get_length() * 1000) + 200)
                else:
                    print("Archivo de sonido no encontrado")
            except Exception as e:
                print("Error al reproducir sonido de inicio: " + str(e))
        threading.Thread(target=_play, daemon=True).start()
    
    @classmethod
    def play_notification(cls):
        """Sonido de notificacion"""
        cls._init()
        def _play():
            try:
                import struct, math, io, wave
                sample_rate = 44100
                # Dos tonos rapidos
                for freq, dur in [(880, 0.12), (1100, 0.15)]:
                    n = int(sample_rate * dur)
                    buf = io.BytesIO()
                    wav = wave.open(buf, 'w')
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(sample_rate)
                    samples = [int(0.4 * 32767 * math.sin(2 * math.pi * freq * i / sample_rate)) for i in range(n)]
                    wav.writeframes(struct.pack(f'<{len(samples)}h', *samples))
                    wav.close()
                    buf.seek(0)
                    sound = pygame.mixer.Sound(buf)
                    sound.play()
                    pygame.time.wait(int(dur * 1000) + 50)
            except:
                pass
        threading.Thread(target=_play, daemon=True).start()
    
    @classmethod
    def play_send(cls):
        """Sonido al enviar mensaje"""
        cls._init()
        def _play():
            try:
                import struct, math, io, wave
                sample_rate = 44100
                n = int(sample_rate * 0.06)
                buf = io.BytesIO()
                wav = wave.open(buf, 'w')
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                samples = [int(0.2 * 32767 * math.sin(2 * math.pi * 600 * i / sample_rate)) for i in range(n)]
                wav.writeframes(struct.pack(f'<{len(samples)}h', *samples))
                wav.close()
                buf.seek(0)
                sound = pygame.mixer.Sound(buf)
                sound.play()
                pygame.time.wait(100)
            except:
                pass
        threading.Thread(target=_play, daemon=True).start()
