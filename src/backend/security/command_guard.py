"""Guard de comandos do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass

from .policies import SecurityPolicies


@dataclass(slots=True)
class CommandGuardResult:
    allowed: bool
    reason: str | None = None
    requires_confirmation: bool = False


class CommandGuard:
    """Aplica politicas de seguranca para comandos de shell."""

    def __init__(self, policies: SecurityPolicies | None = None) -> None:
        self.policies = policies or SecurityPolicies()

    def check(self, command: str, mode: str = "agent", confirmed: bool = False) -> CommandGuardResult:
        decision = self.policies.is_safe_command(command, mode=mode, confirmed=confirmed)
        return CommandGuardResult(
            allowed=decision.allowed,
            reason=decision.reason,
            requires_confirmation=decision.requires_confirmation,
        )
