"""Persistencia de historico da sessao do Mark Core v2 em SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from src.backend.runtime.paths import build_runtime_layout


class HistoryStore:
    """Gerencia eventos historicos de tarefas em banco SQLite."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._layout = build_runtime_layout(base_dir)
        self._base_dir = self._layout.runtime_dir
        self._db_path = self._layout.tasks_db_file
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def append_event(self, task_id: str, event_type: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO history_events (task_id, event_type, content) VALUES (?, ?, ?)",
                (task_id, event_type, content),
            )
            conn.commit()

    def list_events(self, limit: int = 200) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, task_id, event_type, content, created_at
                FROM history_events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get_history_revision(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM history_meta WHERE key = 'history_revision'"
            ).fetchone()

        if row is None:
            return 0
        return int(row["value"])

    def bump_history_revision(self) -> int:
        revision = self.get_history_revision() + 1
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO history_meta (key, value)
                VALUES ('history_revision', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(revision),),
            )
            conn.commit()
        return revision

    def sync_history_revision(self, revision: int) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO history_meta (key, value)
                VALUES ('history_revision', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(revision),),
            )
            conn.commit()

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM history_events")
            conn.execute("DELETE FROM history_meta")
            conn.commit()

    @property
    def db_path(self) -> str:
        return str(self._db_path)
