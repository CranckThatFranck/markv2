"""Politicas de seguranca do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass
from os import environ
import re
import ipaddress


@dataclass(slots=True)
class SecurityDecision:
    allowed: bool
    reason: str | None = None
    requires_confirmation: bool = False


@dataclass(slots=True)
class HostDecision:
    allowed: bool
    reason: str | None = None
    normalized_host: str | None = None


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

    default_allowed_ssh_hosts = {"localhost", "127.0.0.1", "::1"}

    def __init__(self, allowed_ssh_hosts: set[str] | None = None) -> None:
        env_hosts = {
            host.strip().lower()
            for host in environ.get("MARK_ALLOWED_SSH_HOSTS", "").split(",")
            if host.strip()
        }
        self.allowed_ssh_hosts = {host.lower() for host in (allowed_ssh_hosts or self.default_allowed_ssh_hosts)} | env_hosts

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
        if action in {"execute_task", "shutdown_backend", "ssh_tool"}:
            return SecurityDecision(allowed=False, reason="PLAN_MODE_BLOCKED")
        return SecurityDecision(allowed=True)

    def normalize_host(self, host: str) -> str:
        return host.strip().lower().removeprefix("[").removesuffix("]")

    def is_valid_host_format(self, host: str) -> bool:
        candidate = self.normalize_host(host)
        if not candidate or any(ch.isspace() for ch in candidate):
            return False
        if ":" in candidate:
            try:
                ipaddress.ip_address(candidate)
                return True
            except ValueError:
                return False
        return bool(re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,251}", candidate))

    def is_allowed_remote_host(self, host: str, mode: str = "agent") -> HostDecision:
        if mode == "plan":
            return HostDecision(allowed=False, reason="PLAN_MODE_BLOCKED")

        normalized = self.normalize_host(host)
        if not self.is_valid_host_format(normalized):
            return HostDecision(allowed=False, reason="HOST_INVALID", normalized_host=normalized)

        if normalized not in self.allowed_ssh_hosts:
            return HostDecision(allowed=False, reason="HOST_NOT_ALLOWED", normalized_host=normalized)

        return HostDecision(allowed=True, normalized_host=normalized)
