"""Confirmacoes de operacoes sensiveis no Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConfirmationResult:
    required: bool
    reason: str | None = None


class ConfirmationPolicy:
    """Define quando uma operacao deve exigir confirmacao humana."""

    def requires_confirmation(self, action: str) -> ConfirmationResult:
        if action in {"clear_session", "shutdown_backend", "execute_task"}:
            return ConfirmationResult(required=True, reason="SENSITIVE_ACTION")
        return ConfirmationResult(required=False)
