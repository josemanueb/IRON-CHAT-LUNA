import platform
import os
import threading
import subprocess
import struct
import math
import io
import wave

_system = platform.system()
_init_lock = threading.Lock()
_pygame = None

def _get_pygame():
    global _pygame
    if _system == "Windows":
        _pygame = False
        return None
    with _init_lock:
        if _pygame is not None:
            return _pygame if _pygame is not False else None
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100)
            _pygame = pygame
            return pygame
        except Exception:
            _pygame = False
            return None


class Audio:
    _music_process = None
    _music_volume = 0.5

    @staticmethod
    def play_wav(path):
        if not os.path.exists(path):
            return
        if _system == "Windows":
            import winsound
            winsound.PlaySound(path, winsound.SND_ASYNC)
        else:
            pygame = _get_pygame()
            if pygame:
                sound = pygame.mixer.Sound(path)
                sound.play()

    @staticmethod
    def play_beep(freq, duration):
        if _system == "Windows":
            import winsound
            winsound.Beep(freq, duration)
        else:
            pygame = _get_pygame()
            if not pygame:
                return
            sample_rate = 44100
            n = int(sample_rate * duration)
            buf = io.BytesIO()
            w = wave.open(buf, 'w')
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            samples = [int(0.4 * 32767 * math.sin(2 * math.pi * freq * i / sample_rate)) for i in range(n)]
            w.writeframes(struct.pack(f'<{len(samples)}h', *samples))
            w.close()
            buf.seek(0)
            sound = pygame.mixer.Sound(buf)
            sound.play()

    @staticmethod
    def play_music(path, loop=True):
        Audio.stop_music()
        if not os.path.exists(path):
            return
        if _system == "Windows":
            Audio._music_process = subprocess.Popen(
                ['cmd', '/c', 'start', '/min', '', path],
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        else:
            pygame = _get_pygame()
            if not pygame:
                return
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)

    @staticmethod
    def stop_music():
        if _system == "Windows":
            if Audio._music_process:
                try:
                    subprocess.run(
                        ['taskkill', '/f', '/t', '/pid', str(Audio._music_process.pid)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                except Exception:
                    pass
                Audio._music_process = None
        else:
            pygame = _get_pygame()
            if pygame:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass

    @staticmethod
    def set_music_volume(vol):
        Audio._music_volume = max(0.0, min(1.0, vol))

    @staticmethod
    def stop_all():
        Audio.stop_music()

    @staticmethod
    def wait_for_wav(duration_ms):
        if _system == "Linux":
            pygame = _get_pygame()
            if pygame:
                pygame.time.wait(duration_ms)

_init = _get_pygame()
