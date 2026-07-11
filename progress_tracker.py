import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager


class ProgressTracker:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
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
