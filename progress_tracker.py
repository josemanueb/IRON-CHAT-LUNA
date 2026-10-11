import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager


class ProgressTracker:
    # sqlite3.connect no tiene busy_timeout por defecto: si el panel de
    # progreso escribe mientras se consulta, salta "database is locked".
    # 5s es suficiente para operaciones localmente triviales.
    BUSY_TIMEOUT_S = 5

    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path, timeout=self.BUSY_TIMEOUT_S)
        try:
            # wait_for evita "database is locked" tambien en escrituras.
            conn.execute("PRAGMA journal_mode=WAL")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS progress
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          date TEXT NOT NULL,
                          weight REAL,
                          bicep REAL,
                          chest REAL,
                          waist REAL,
                          thigh REAL,
                          notes TEXT)''')

    def add_entry(self, weight=None, bicep=None, chest=None, waist=None, thigh=None, notes=""):
        with self._conn() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO progress (date, weight, bicep, chest, waist, thigh, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (datetime.now().strftime("%Y-%m-%d %H:%M"), weight, bicep, chest, waist, thigh, notes))

    def get_entries(self, limit=20):
        with self._conn() as conn:
            c = conn.cursor()
            c.execute('''SELECT date, weight, bicep, chest, waist, thigh, notes
                         FROM progress ORDER BY id DESC LIMIT ?''', (limit,))
            return c.fetchall()

    def get_latest(self):
        """Ultima entrada, o None si la tabla esta vacia."""
        entries = self.get_entries(limit=1)
        return entries[0] if entries else None

    def delete_entry(self, entry_id):
        """Borra una entrada por id. Devuelve True si se borro algo."""
        with self._conn() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM progress WHERE id = ?", (entry_id,))
            return c.rowcount > 0
