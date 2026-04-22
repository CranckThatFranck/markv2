"""Ferramenta de sistema do Mark Core v2."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SystemToolResult:
    ok: bool
    data: dict[str, object]
    error: str | None = None


class SystemTool:
    """Expõe informacoes basicas de sistema sem acesso destrutivo."""

    def inspect(self) -> SystemToolResult:
        try:
            return SystemToolResult(
                ok=True,
                data={
                    "pid": os.getpid(),
                    "cwd": str(Path.cwd()),
                    "platform": os.name,
                },
            )
        except Exception as exc:  # noqa: BLE001
            return SystemToolResult(ok=False, data={}, error=str(exc))
