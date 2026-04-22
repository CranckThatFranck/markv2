"""Persistencia de regras iniciais do Mark Core v2."""

from __future__ import annotations

from pathlib import Path


class RulesStore:
    """Lê e grava regras iniciais em arquivo texto."""

    def __init__(self, base_dir: str = "/opt/jarvis/backend/product_config") -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._file = self._base_dir / "initial_rules.txt"

    def load(self) -> str:
        if not self._file.exists():
            return ""
        return self._file.read_text(encoding="utf-8")

    def save(self, content: str) -> None:
        self._file.write_text(content, encoding="utf-8")

    @property
    def file_path(self) -> str:
        return str(self._file)
