import os
import threading
import time
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
    def play_notification(cls):
        if not cls._cooldown():
            return
        def _play():
            try:
                Audio.play_beep(880, 120)
                Audio.play_beep(1100, 150)
            except:
                pass
        threading.Thread(target=_play, daemon=True).start()

    @classmethod
    def play_send(cls):
        if not cls._cooldown():
            return
        def _play():
            try:
                Audio.play_beep(600, 60)
            except:
                pass
        threading.Thread(target=_play, daemon=True).start()
