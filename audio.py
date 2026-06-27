import platform
import os
import threading
import subprocess
import struct
import math
import io
import wave
import time

_system = platform.system()
_system_encoding = "utf-8"


def _ensure_pygame():
    if _system != "Windows":
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100)
            return pygame
        except ImportError:
            pass
    return None


class Audio:
    _music_process = None
    _music_winsound_playing = False

    @staticmethod
    def play_wav(path):
        if not os.path.exists(path):
            return
        if _system == "Windows":
            import winsound
            winsound.PlaySound(path, winsound.SND_ASYNC)
        else:
            pygame = _ensure_pygame()
            if pygame:
                sound = pygame.mixer.Sound(path)
                sound.play()

    @staticmethod
    def play_beep(freq, duration):
        if _system == "Windows":
            import winsound
            winsound.Beep(freq, duration)
        else:
            pygame = _ensure_pygame()
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
        ext = os.path.splitext(path)[1].lower()
        if _system == "Windows":
            if ext == ".wav":
                import winsound
                flags = winsound.SND_ASYNC | winsound.SND_LOOP if loop else winsound.SND_ASYNC
                winsound.PlaySound(path, flags)
                Audio._music_winsound_playing = True
            else:
                Audio._music_process = subprocess.Popen(
                    ['powershell', '-NoProfile', '-Command',
                     f'Start-Process -WindowStyle Hidden -FilePath "{path}"'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
        else:
            pygame = _ensure_pygame()
            if not pygame:
                return
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)

    @staticmethod
    def stop_music():
        if _system == "Windows":
            if Audio._music_winsound_playing:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
                Audio._music_winsound_playing = False
            if Audio._music_process:
                try:
                    Audio._music_process.kill()
                    Audio._music_process.wait(timeout=3)
                except:
                    pass
                Audio._music_process = None
        else:
            pygame = _ensure_pygame()
            if pygame:
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                except:
                    pass

    @staticmethod
    def stop_all():
        Audio.stop_music()

    @staticmethod
    def wait_for_wav(duration_ms):
        if _system == "Linux":
            pygame = _ensure_pygame()
            if pygame:
                pygame.time.wait(duration_ms)

    @staticmethod
    def load_wav(path):
        if _system == "Windows":
            import winsound
            if os.path.exists(path):
                winsound.PlaySound(path, winsound.SND_ASYNC)
                return True
            return None
        else:
            pygame = _ensure_pygame()
            if pygame and os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.play()
                return sound
        return None
