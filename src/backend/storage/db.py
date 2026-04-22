"""Banco SQLite base do Mark Core v2."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    """Cria e prepara o banco SQLite base do produto."""

    def __init__(self, base_dir: str = "/var/lib/jarvis-mark/estado") -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._base_dir / "tasks.db"
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS config_store (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rules_store (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_text TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @property
    def db_path(self) -> str:
        return str(self._db_path)
