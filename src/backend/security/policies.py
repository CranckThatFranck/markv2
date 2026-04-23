"""Politicas de seguranca do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(slots=True)
class SecurityDecision:
    allowed: bool
    reason: str | None = None
    requires_confirmation: bool = False


class SecurityPolicies:
    """Conjunto minimo de regras para operacao segura do backend."""

    destructive_patterns = (
        r"\brm\s+-rf\b",
        r"\bmkfs\b",
        r"\bshutdown\b",
        r"\breboot\b",
        r"\bpoweroff\b",
        r"\bhalt\b",
        r"\bdd\s+if=",
        r":\(\)\s*\{\s*:\s*\|\s*&\s*;\s*\}\s*;\s*:",
    )

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

    def is_safe_command(self, command: str, mode: str = "agent", confirmed: bool = False) -> SecurityDecision:
        normalized = command.strip().lower()
        if mode == "plan":
            return SecurityDecision(allowed=False, reason="PLAN_MODE_BLOCKED")

        for pattern in self.destructive_patterns:
            if re.search(pattern, normalized):
                return SecurityDecision(allowed=False, reason="COMMAND_BLOCKED")

        for pattern in self.confirmation_patterns:
            if re.search(pattern, normalized):
                if confirmed:
                    return SecurityDecision(allowed=True)
                return SecurityDecision(allowed=False, reason="CONFIRMATION_REQUIRED", requires_confirmation=True)

        return SecurityDecision(allowed=True)

    def is_plan_mode_allowed(self, action: str) -> SecurityDecision:
        if action in {"execute_task", "shutdown_backend"}:
            return SecurityDecision(allowed=False, reason="PLAN_MODE_BLOCKED")
        return SecurityDecision(allowed=True)
