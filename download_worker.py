#!/usr/bin/env python3
"""Descarga de modelos GGUF en segundo plano, con cancelacion real.

Antes la descarga vivia entera dentro de main.py y no habia forma de
detenerla: cerrar el dialogo no hacia nada (el WM_DELETE_WINDOW estaba
en "lambda: None") y el hilo se comia el ancho de banda hasta el final,
incluso aunque el usuario ya no quisiera el modelo.

Aqui el trabajo de red vive aparte de la UI y se puede abortar limpiamente:

    worker = ModelDownloader(url, dest, on_progress)
    worker.start()
    ...
    worker.cancel()      # el hilo para en el siguiente chunk y borra el .tmp
    worker.join(timeout)

La UI nunca se toca desde el hilo: el worker solo invoca los callbacks,
que se registran con root.after(0, ...) desde main.py.
"""
import os
import ssl
import threading
import time
import urllib.error
import urllib.request

CHUNK_SIZE = 65536
CONNECT_TIMEOUT = 120
MIN_MODEL_BYTES = 1_000_000
USER_AGENT = "IRON-CHAT-LUNA/2.3"
MAX_RETRIES = 3


class DownloadCancelled(Exception):
    """Se lanza cuando el usuario cancela la descarga."""


class ModelDownloader:
    """Descarga un archivo a disco con progreso y cancelacion."""

    def __init__(self, url, dest, expected_sha256=None, on_progress=None,
                 on_done=None, on_error=None):
        self.url = url
        self.dest = dest
        self.expected_sha256 = expected_sha256
        self.on_progress = on_progress
        self.on_done = on_done
        self.on_error = on_error

        self._cancel = threading.Event()
        self._thread = None
        self.bytes_sent = 0
        self.total_bytes = 0
        self.error = None
        self.cancelled = False

    # --- API publica ---
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def cancel(self):
        """Pide cancelar. Es seguro llamarlo desde la UI."""
        self._cancel.set()

    def join(self, timeout=None):
        if self._thread:
            self._thread.join(timeout)

    def is_alive(self):
        return bool(self._thread and self._thread.is_alive())

    @property
    def percent(self):
        if not self.total_bytes:
            return 0
        return min(100, int(self.bytes_sent * 100 / self.total_bytes))

    # --- Interno ---
    def _check_cancel(self):
        if self._cancel.is_set():
            raise DownloadCancelled()

    def _progress(self, sent, total):
        self.bytes_sent = sent
        self.total_bytes = total
        if self.on_progress:
            self.on_progress(sent, total)

    def _run(self):
        tmp = self.dest + ".tmp"
        try:
            self._download(tmp)
        except DownloadCancelled:
            self.cancelled = True
            _remove(tmp)
        except Exception as e:
            self.error = e
            _remove(tmp)
            if self.on_error:
                self.on_error(e)
        else:
            if self.on_done:
                self.on_done(self.dest)

    def _download(self, tmp):
        ctx = ssl.create_default_context()
        req = urllib.request.Request(self.url)
        req.add_header("User-Agent", USER_AGENT)

        resp = urllib.request.urlopen(req, context=ctx, timeout=CONNECT_TIMEOUT)
        try:
            total = int(resp.headers.get("Content-Length", 0))
            sent = 0
            last_report = 0.0
            with open(tmp, "wb") as f:
                while True:
                    # Comprueba cancelacion ANTES de escribir el siguiente
                    # chunk: aborta en cuanto llega la peticion, no al final.
                    self._check_cancel()
                    chunk = resp.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    sent += len(chunk)
                    now = time.time()
                    if total > 0 or now - last_report >= 0.5:
                        last_report = now
                        self._progress(sent, total)
        finally:
            try:
                resp.close()
            except Exception:
                pass

        self._progress(sent, total if total else 0)

        size = os.path.getsize(tmp)
        if size < MIN_MODEL_BYTES:
            raise RuntimeError(f"Archivo corrupto: solo {size} bytes")

        if self.expected_sha256:
            from hash_utils import sha256_file, verify_file
            if not verify_file(tmp, self.expected_sha256):
                got = sha256_file(tmp)
                raise RuntimeError(
                    "SHA256 no coincide: esperado %s..., obtenido %s..."
                    % (self.expected_sha256[:16], got[:16])
                )

        self._check_cancel()
        _atomic_replace(tmp, self.dest)


def _atomic_replace(tmp, dest):
    """os.replace puede fallar si el antivirus tiene el destino abierto."""
    for intento in range(MAX_RETRIES):
        try:
            os.replace(tmp, dest)
            return
        except OSError:
            if intento == MAX_RETRIES - 1:
                raise
            time.sleep(1)


def _remove(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass