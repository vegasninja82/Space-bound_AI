"""
Metrics storage layer. Wraps the SQLite Database from storage/database.py
so the rest of the app doesn't talk to raw SQL.
"""
from __future__ import annotations

from storage.database import Database


class MetricsRecorder:
    def __init__(self):
        self.db = Database()

    def record(self, data: dict) -> int:
        return self.db.insert(data)

    def query_recent(self, limit: int = 50) -> list[dict]:
        rows = self.db.query(
            "SELECT id, ts, payload FROM metrics ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        import json
        return [
            {"id": r[0], "ts": r[1], "data": json.loads(r[2])}
            for r in rows
        ]
