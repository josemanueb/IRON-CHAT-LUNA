import sqlite3
import os
from datetime import datetime

class ProgressTracker:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
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
        conn.commit()
        conn.close()

    def add_entry(self, weight=None, bicep=None, chest=None, waist=None, thigh=None, notes=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO progress (date, weight, bicep, chest, waist, thigh, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), weight, bicep, chest, waist, thigh, notes))
        conn.commit()
        conn.close()

    def get_entries(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT date, weight, bicep, chest, waist, thigh, notes
                     FROM progress ORDER BY id DESC LIMIT ?''', (limit,))
        rows = c.fetchall()
        conn.close()
        return rows
