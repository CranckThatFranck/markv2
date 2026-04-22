"""Ferramenta SSH do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SSHResult:
    ok: bool
    output: str
    error: str | None = None


class SSHTool:
    """Placeholder controlado para execucao remota via SSH."""

    def execute(self, host: str, command: str) -> SSHResult:
        if not host.strip():
            return SSHResult(ok=False, output="", error="HOST_REQUIRED")
        if not command.strip():
            return SSHResult(ok=False, output="", error="COMMAND_REQUIRED")
        return SSHResult(ok=False, output="", error="SSH_NOT_IMPLEMENTED_YET")
