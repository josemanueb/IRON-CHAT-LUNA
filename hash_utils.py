import hashlib
import os


def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_file(filepath, expected_hex):
    if not os.path.exists(filepath):
        return False
    actual = sha256_file(filepath)
    return actual.lower() == expected_hex.lower()


def file_size_ok(filepath, min_bytes=1_000_000):
    return os.path.exists(filepath) and os.path.getsize(filepath) >= min_bytes
