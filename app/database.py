import sqlite3
import os
import hashlib
from datetime import datetime


class ClipDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.expanduser("~"), ".clipser", "clips.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                pinned INTEGER DEFAULT 0,
                timestamp REAL NOT NULL,
                content_hash TEXT UNIQUE
            )"""
        )
        self._conn.commit()

    MAX_PINNED = 5

    def add_entry(self, text):
        h = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        ts = datetime.now().timestamp()
        with self._conn:
            existing = self._conn.execute(
                "SELECT id, pinned FROM clips WHERE content_hash=?", (h,)
            ).fetchone()
            if existing:
                pinned = existing[1]
                self._conn.execute("DELETE FROM clips WHERE id=?", (existing[0],))
            else:
                pinned = 0
            self._conn.execute(
                "INSERT INTO clips (text, pinned, timestamp, content_hash) VALUES (?, ?, ?, ?)",
                (text, pinned, ts, h),
            )

    def get_entries(self, limit=200):
        return self._conn.execute(
            "SELECT id, text, pinned, timestamp FROM clips ORDER BY pinned DESC, timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def delete_entry(self, entry_id):
        self._conn.execute("DELETE FROM clips WHERE id=?", (entry_id,))
        self._conn.commit()

    def toggle_pin(self, entry_id):
        row = self._conn.execute(
            "SELECT pinned FROM clips WHERE id=?", (entry_id,)
        ).fetchone()
        if not row:
            return False
        currently_pinned = bool(row[0])
        if not currently_pinned:
            pinned_count = self._conn.execute(
                "SELECT COUNT(*) FROM clips WHERE pinned=1"
            ).fetchone()[0]
            if pinned_count >= self.MAX_PINNED:
                return False
        self._conn.execute(
            "UPDATE clips SET pinned = CASE WHEN pinned = 0 THEN 1 ELSE 0 END WHERE id=?",
            (entry_id,),
        )
        self._conn.commit()
        return True

    def clear_all(self):
        self._conn.execute("DELETE FROM clips")
        self._conn.commit()

    def search(self, query, limit=200):
        return self._conn.execute(
            "SELECT id, text, pinned, timestamp FROM clips WHERE text LIKE ? ORDER BY pinned DESC, timestamp DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()

    def count(self):
        return self._conn.execute("SELECT COUNT(*) FROM clips").fetchone()[0]

    def is_pinned(self, entry_id):
        row = self._conn.execute(
            "SELECT pinned FROM clips WHERE id=?", (entry_id,)
        ).fetchone()
        return bool(row[0]) if row else False

    def enforce_limit(self, max_entries):
        self._conn.execute(
            """DELETE FROM clips WHERE id NOT IN (
                SELECT id FROM clips ORDER BY pinned DESC, timestamp DESC LIMIT ?
            )""",
            (max_entries,),
        )
        self._conn.commit()

    def close(self):
        self._conn.close()
