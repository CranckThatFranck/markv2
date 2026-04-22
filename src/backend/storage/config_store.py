"""Persistencia de configuracao do Mark Core v2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.backend.runtime.paths import build_runtime_layout


class ConfigStore:
    """Lê e grava configuracoes simples em JSON."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._layout = build_runtime_layout(base_dir)
        self._base_dir = self._layout.runtime_dir
        self._file = self._layout.config_file

    def load(self) -> dict[str, Any]:
        if not self._file.exists():
            return {}
        with self._file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, config: dict[str, Any]) -> None:
        with self._file.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    @property
    def file_path(self) -> str:
        return str(self._file)
