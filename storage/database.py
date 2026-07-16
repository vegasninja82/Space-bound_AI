import sqlite3, json, os, time
DB_PATH = os.environ.get('SPACE_DB', 'spacebound.db')

class Database:
    def __init__(self, path=None):
        self.path = path or DB_PATH
        self._ensure()

    def _ensure(self):
        conn = sqlite3.connect(self.path)
        try:
            conn.execute('''CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, payload TEXT)''')
            conn.commit()
        finally:
            conn.close()

    def insert(self, payload):
        conn = sqlite3.connect(self.path)
        try:
            cur = conn.cursor()
            cur.execute('INSERT INTO metrics (ts, payload) VALUES (?, ?)', (time.time(), json.dumps(payload)))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def query(self, sql, params=()):
        conn = sqlite3.connect(self.path)
        try:
            cur = conn.execute(sql, params)
            return cur.fetchall()
        finally:
            conn.close()
