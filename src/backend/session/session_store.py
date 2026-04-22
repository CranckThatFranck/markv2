"""Persistencia da sessao ativa do Mark Core v2 em JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SessionStore:
    """Gerencia a sessao ativa persistida em disco."""

    def __init__(self, base_dir: str = "/var/lib/jarvis-mark/estado") -> None:
        self._base_dir = Path(base_dir)
        self._session_file = self._base_dir / "session.json"
        self._base_dir.mkdir(parents=True, exist_ok=True)

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

    def clear(self) -> None:
        """Limpa sessao ativa mantendo o arquivo consistente."""

        self.save({"active_session": None, "metadata": {}})

    @property
    def session_file(self) -> str:
        return str(self._session_file)
