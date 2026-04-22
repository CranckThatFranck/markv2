"""Persistencia da sessao ativa do Mark Core v2 em JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.backend.runtime.paths import build_runtime_layout


class SessionStore:
    """Gerencia a sessao ativa persistida em disco."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._layout = build_runtime_layout(base_dir)
        self._base_dir = self._layout.runtime_dir
        self._session_file = self._layout.session_file

    def load(self) -> dict[str, Any]:
        """Carrega sessao atual; retorna estrutura vazia quando nao existir."""

        if not self._session_file.exists():
            return {"active_session": None, "metadata": {}}

        with self._session_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, payload: dict[str, Any]) -> None:
        """Persiste sessao atual."""

        with self._session_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def set_active_session(
        self,
        task_id: str,
        prompt: str,
        rules_file: str,
        history_revision: int,
    ) -> None:
        self.save(
            {
                "active_session": {
                    "task_id": task_id,
                    "prompt": prompt,
                    "rules_file": rules_file,
                    "history_revision": history_revision,
                    "status": "running",
                },
                "metadata": {
                    "last_task_id": task_id,
                    "last_rules_file": rules_file,
                },
            }
        )

    def set_idle_session(self, history_revision: int, last_task_id: str | None = None) -> None:
        self.save(
            {
                "active_session": None,
                "metadata": {
                    "last_task_id": last_task_id,
                    "history_revision": history_revision,
                },
            }
        )

    def clear(self) -> None:
        """Limpa sessao ativa mantendo o arquivo consistente."""

        self.save({"active_session": None, "metadata": {}})

    @property
    def session_file(self) -> str:
        return str(self._session_file)
