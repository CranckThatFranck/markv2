"""Politicas de seguranca do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SecurityDecision:
    allowed: bool
    reason: str | None = None


class SecurityPolicies:
    """Conjunto minimo de regras para operacao segura do backend."""

    destructive_commands = {"rm -rf /", "shutdown", "reboot", "mkfs"}

    def is_safe_command(self, command: str) -> SecurityDecision:
        normalized = command.strip().lower()
        for pattern in self.destructive_commands:
            if pattern in normalized:
                return SecurityDecision(allowed=False, reason="COMMAND_BLOCKED")
        return SecurityDecision(allowed=True)

    def is_plan_mode_allowed(self, action: str) -> SecurityDecision:
        if action in {"execute_task", "shutdown_backend"}:
            return SecurityDecision(allowed=False, reason="PLAN_MODE_BLOCKED")
        return SecurityDecision(allowed=True)
