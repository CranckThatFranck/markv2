"""Gerenciamento de interrupcao de tasks do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InterruptResult:
    ok: bool
    task_id: str
    message: str


class InterruptManager:
    """Registra interrupcoes de tasks em andamento."""

    def interrupt(self, task_id: str | None) -> InterruptResult:
        if not task_id:
            return InterruptResult(ok=False, task_id="", message="TASK_NOT_FOUND")
        return InterruptResult(ok=True, task_id=task_id, message="INTERRUPTED")
