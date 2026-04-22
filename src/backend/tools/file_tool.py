"""Ferramenta de arquivo controlada do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FileToolResult:
    ok: bool
    content: str | None = None
    error: str | None = None


class FileTool:
    """Leitura simples e segura de arquivos permitidos."""

    def read_text(self, path: str) -> FileToolResult:
        file_path = Path(path)
        if not file_path.exists():
            return FileToolResult(ok=False, error="FILE_NOT_FOUND")
        try:
            return FileToolResult(ok=True, content=file_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            return FileToolResult(ok=False, error=str(exc))
