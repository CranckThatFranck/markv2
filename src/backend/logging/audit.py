"""Auditoria minima do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AuditEntry:
    action: str
    detail: str


class AuditLog:
    """Registra eventos relevantes em formato simples."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def add(self, action: str, detail: str) -> None:
        self._entries.append(AuditEntry(action=action, detail=detail))

    def list_entries(self) -> list[AuditEntry]:
        return list(self._entries)
