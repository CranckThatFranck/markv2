"""Ferramenta SSH do Mark Core v2."""

from __future__ import annotations

import asyncio
import getpass
from typing import Awaitable, Callable
from dataclasses import dataclass

import asyncssh

from src.backend.security.command_guard import CommandGuard
from src.backend.security.policies import SecurityPolicies


@dataclass(slots=True)
class SSHResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    host: str
    command: str
    user: str | None = None
    port: int = 22
    error_code: str | None = None
    error: str | None = None


class SSHTool:
    """Execucao remota via SSH com politica de host e comando."""

    def __init__(
        self,
        timeout_seconds: int = 60,
        command_guard: CommandGuard | None = None,
        security_policies: SecurityPolicies | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.command_guard = command_guard or CommandGuard()
        self.security_policies = security_policies or SecurityPolicies()

    async def _emit_console(self, emit_console: Callable[[str, str], Awaitable[None]] | None, stream: str, content: str) -> None:
        if emit_console is not None:
            await emit_console(stream, content)

    async def execute(
        self,
        host: str,
        command: str,
        user: str | None = None,
        port: int = 22,
        password: str | None = None,
        mode: str = "agent",
        confirmed: bool = False,
        emit_console: Callable[[str, str], Awaitable[None]] | None = None,
    ) -> SSHResult:
        if not host.strip():
            return SSHResult(ok=False, exit_code=1, stdout="", stderr="HOST_REQUIRED", host="", command=command)
        if not command.strip():
            return SSHResult(ok=False, exit_code=1, stdout="", stderr="COMMAND_REQUIRED", host=host, command="")

        host_decision = self.security_policies.is_allowed_remote_host(host, mode=mode)
        if not host_decision.allowed:
            return SSHResult(
                ok=False,
                exit_code=126,
                stdout="",
                stderr=host_decision.reason or "HOST_NOT_ALLOWED",
                host=host_decision.normalized_host or host,
                command=command,
                user=user,
                port=port,
                error_code=host_decision.reason or "HOST_NOT_ALLOWED",
                error=host_decision.reason or "HOST_NOT_ALLOWED",
            )

        guard = self.command_guard.check(command, mode=mode, confirmed=confirmed)
        if not guard.allowed:
            return SSHResult(
                ok=False,
                exit_code=126,
                stdout="",
                stderr=guard.reason or "COMMAND_BLOCKED",
                host=host_decision.normalized_host or host,
                command=command,
                user=user,
                port=port,
                error_code=guard.reason or "COMMAND_BLOCKED",
                error=guard.reason or "COMMAND_BLOCKED",
            )

        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []

        try:
            effective_user = user or getpass.getuser()
            async with asyncio.timeout(self.timeout_seconds):
                async with asyncssh.connect(
                    host_decision.normalized_host or host,
                    port=port,
                    username=effective_user,
                    password=password,
                    known_hosts=None,
                ) as conn:
                    process = await conn.create_process(command)
                    await self._emit_console(emit_console, "stdout", f"[ssh:{host_decision.normalized_host or host}:{port}]\n")

                    async def read_stream(stream_reader: asyncio.StreamReader | None, stream_name: str) -> None:
                        if stream_reader is None:
                            return
                        while True:
                            chunk = await stream_reader.readline()
                            if not chunk:
                                break
                            content = chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else str(chunk)
                            if stream_name == "stdout":
                                stdout_chunks.append(content)
                            else:
                                stderr_chunks.append(content)
                            await self._emit_console(emit_console, stream_name, content)

                    readers = [
                        asyncio.create_task(read_stream(getattr(process, "stdout", None), "stdout")),
                        asyncio.create_task(read_stream(getattr(process, "stderr", None), "stderr")),
                    ]
                    await process.wait_closed()
                    await asyncio.gather(*readers)

                    exit_code = getattr(process, "returncode", None)
                    if exit_code is None:
                        exit_code = getattr(process, "exit_status", 0)

                    stdout = "".join(stdout_chunks)
                    stderr = "".join(stderr_chunks)
                    return SSHResult(
                        ok=exit_code == 0,
                        exit_code=exit_code,
                        stdout=stdout,
                        stderr=stderr,
                        host=host_decision.normalized_host or host,
                        command=command,
                        user=user,
                        port=port,
                    )
        except TimeoutError:
            return SSHResult(
                ok=False,
                exit_code=124,
                stdout="",
                stderr="TIMEOUT",
                host=host_decision.normalized_host or host,
                command=command,
                user=user,
                port=port,
                error_code="TIMEOUT",
                error="TIMEOUT",
            )
        except asyncssh.PermissionDenied:
            return SSHResult(
                ok=False,
                exit_code=255,
                stdout="",
                stderr="AUTHENTICATION_FAILED",
                host=host_decision.normalized_host or host,
                command=command,
                user=user,
                port=port,
                error_code="AUTHENTICATION_FAILED",
                error="AUTHENTICATION_FAILED",
            )
        except (OSError, asyncssh.Error) as exc:
            error_text = str(exc) or "CONNECTION_ERROR"
            if "auth" in error_text.lower():
                error_code = "AUTHENTICATION_FAILED"
            elif "timed out" in error_text.lower():
                error_code = "TIMEOUT"
            else:
                error_code = "CONNECTION_ERROR"
            return SSHResult(
                ok=False,
                exit_code=255,
                stdout="",
                stderr=error_code,
                host=host_decision.normalized_host or host,
                command=command,
                user=user,
                port=port,
                error_code=error_code,
                error=error_text,
            )
