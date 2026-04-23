"""Confirmacoes de operacoes sensiveis no Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(slots=True)
class ConfirmationResult:
    required: bool
    reason: str | None = None


class ConfirmationPolicy:
    """Define quando uma operacao deve exigir confirmacao humana."""

    confirmation_actions = {"clear_session", "shutdown_backend", "execute_task"}
    confirmation_patterns = (
        r"\bsudo\b",
        r"\bchmod\s+777\b",
        r"\bchown\s+-R\b",
        r"\bkill\s+-9\b",
        r"\bpkill\s+-9\b",
        r"\bkillall\b",
        r"\buserdel\b",
        r"\bcurl\b.*\|\s*bash\b",
        r"\bwget\b.*\|\s*bash\b",
    )

    def requires_confirmation(self, action: str | None = None, command: str | None = None) -> ConfirmationResult:
        if action is not None and action in self.confirmation_actions:
            return ConfirmationResult(required=True, reason="SENSITIVE_ACTION")

        if command is not None:
            normalized = command.strip().lower()
            for pattern in self.confirmation_patterns:
                if re.search(pattern, normalized):
                    return ConfirmationResult(required=True, reason="HIGH_RISK_COMMAND")

        return ConfirmationResult(required=False)
