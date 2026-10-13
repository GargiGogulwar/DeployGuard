"""Tiny SQLite-backed deployment history store."""
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# source values:
#   runtime   - automatic record written when this application process starts
#   simulated - demo record created through the API; NO real deployment happened
#   ci-cd     - reported by the real pipeline/Ansible after a real deployment step
SOURCES = ("runtime", "simulated", "ci-cd")
STATUSES = ("started", "success", "failed")
MAX_ROWS = 100

_SCHEMA = """
CREATE TABLE IF NOT EXISTS deployments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    version TEXT NOT NULL,
    image_tag TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    environment TEXT NOT NULL,
    status TEXT NOT NULL,
    source TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT ''
)
"""


class DeploymentStore:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute(_SCHEMA)
            self._conn.commit()

    def add(self, *, version, image_tag, commit_sha, environment, status, source, note="") -> dict:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO deployments (timestamp, version, image_tag, commit_sha,"
                " environment, status, source, note) VALUES (?,?,?,?,?,?,?,?)",
                (ts, version, image_tag, commit_sha, environment, status, source, note),
            )
            # keep the table small
            self._conn.execute(
                "DELETE FROM deployments WHERE id <= (SELECT MAX(id) FROM deployments) - ?",
                (MAX_ROWS,),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT * FROM deployments WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
        return dict(row)

    def list(self, limit: int = 20, source: Optional[str] = None) -> list:
        sql = "SELECT * FROM deployments"
        args: list = []
        if source:
            sql += " WHERE source = ?"
            args.append(source)
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        with self._lock:
            return [dict(r) for r in self._conn.execute(sql, args).fetchall()]

    def latest(self, source: Optional[str] = None) -> Optional[dict]:
        rows = self.list(limit=1, source=source)
        return rows[0] if rows else None

    def ping(self) -> bool:
        """Used by the readiness probe."""
        try:
            with self._lock:
                self._conn.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error:
            return False

    def close(self) -> None:
        with self._lock:
            self._conn.close()
