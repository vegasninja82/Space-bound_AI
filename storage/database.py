import sqlite3
import json
import time
import os
from threading import Lock

class Database:
    """SQLite abstraction layer for metrics storage."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.environ.get("METRICS_DB", "spacebound.db")
        self.db_path = db_path
        self.lock = Lock()
        self.conn = None
        self._connect()
        self._init_schema()
    
    def _connect(self):
        """Establish database connection with thread safety."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.isolation_level = None  # Autocommit mode
    
    def _init_schema(self):
        """Create metrics table if it doesn't exist."""
        with self.lock:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    payload TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ts ON metrics(ts DESC)
            """)
    
    def insert(self, data):
        """Insert a metrics record into the database.
        
        Args:
            data: Dictionary to be serialized as JSON and stored
        
        Returns:
            int: The inserted record ID
        """
        with self.lock:
            try:
                payload = json.dumps(data)
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO metrics (ts, payload) VALUES (?, ?)",
                    (time.time(), payload)
                )
                return cursor.lastrowid
            except Exception as e:
                raise RuntimeError(f"Failed to insert metric: {e}")
    
    def query(self, sql, params=None):
        """Execute a SELECT query and return results.
        
        Args:
            sql: SQL query string
            params: Optional query parameters
        
        Returns:
            list: List of tuples representing query results
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                return cursor.fetchall()
            except Exception as e:
                raise RuntimeError(f"Failed to query metrics: {e}")
    
    def close(self):
        """Close the database connection."""
        with self.lock:
            if self.conn:
                self.conn.close()
                self.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
