import os
import threading
import time
import math
import struct
import io
import wave
from audio import Audio

class Sounds:
    _project_dir = os.path.dirname(os.path.abspath(__file__))
    _last_sound_time = 0
    _lock = threading.Lock()

    @classmethod
    def _cooldown(cls):
        with cls._lock:
            now = time.time()
            if now - cls._last_sound_time < 1.0:
                return False
            cls._last_sound_time = now
            return True

    @staticmethod
    def _gen_wav(samples, sample_rate=44100):
        buf = io.BytesIO()
        w = wave.open(buf, 'w')
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(struct.pack(f'<{len(samples)}h', *samples))
        w.close()
        buf.seek(0)
        return buf.read()

    @classmethod
    def play_startup(cls):
        def _play():
            try:
                wav_path = os.path.join(cls._project_dir, "iniciodesesion.wav")
                Audio.play_wav(wav_path)
            except Exception as e:
                print("Error al reproducir sonido de inicio: " + str(e))
        threading.Thread(target=_play, daemon=True).start()

    @classmethod
    def play_chat(cls):
        """Sonido burbujeante tipo 'bloop' para cuando se envia/recibe un mensaje"""
        if not cls._cooldown():
            return
        def _play():
            try:
                sr = 22050
                chunks = []
                # 3 burbujas ascendentes, cada una de 65ms
                for bubble in range(3):
                    n = int(sr * 0.065)
                    base = 350 + bubble * 180
                    for i in range(n):
                        t = i / n
                        freq = base + t * 400
                        env = 1.0 - t * 0.7
                        val = int(0.4 * 32767 * env * math.sin(2 * math.pi * freq * i / sr))
                        chunks.append(val)
                    # silencio de 15ms entre burbujas
                    silence = int(sr * 0.015)
                    chunks.extend([0] * silence)
                # pop final (burbuja que explota)
                n = int(sr * 0.08)
                for i in range(n):
                    t = i / n
                    freq = 700 + t * 500
                    env = 1.0 - t * 0.9
                    val = int(0.3 * 32767 * env * math.sin(2 * math.pi * freq * i / sr))
                    chunks.append(val)

                wav_data = cls._gen_wav(chunks, sr)
                import platform
                if platform.system() == "Windows":
                    import winsound
                    winsound.PlaySound(wav_data, winsound.SND_ASYNC | winsound.SND_MEMORY)
                else:
                    import pygame
                    if pygame.mixer.get_init() is None:
                        pygame.mixer.init(frequency=sr)
                    sound = pygame.mixer.Sound(io.BytesIO(wav_data))
                    sound.play()
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    @classmethod
    def play_notification(cls):
        if not cls._cooldown():
            return
        def _play():
            try:
                Audio.play_beep(880, 120)
                Audio.play_beep(1100, 150)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()


