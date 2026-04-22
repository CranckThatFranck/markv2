"""Guard de comandos do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass

from .policies import SecurityPolicies


@dataclass(slots=True)
class CommandGuardResult:
    allowed: bool
    reason: str | None = None


class CommandGuard:
    """Aplica politicas de seguranca para comandos de shell."""

    def __init__(self, policies: SecurityPolicies | None = None) -> None:
        self.policies = policies or SecurityPolicies()

    def check(self, command: str) -> CommandGuardResult:
        decision = self.policies.is_safe_command(command)
        return CommandGuardResult(allowed=decision.allowed, reason=decision.reason)
