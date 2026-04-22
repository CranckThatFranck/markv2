"""Ferramenta shell controlada do Mark Core v2."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ShellResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str


class ShellTool:
    """Executa comandos shell com captura simples de saida."""

    def __init__(self, timeout_seconds: int = 60) -> None:
        self.timeout_seconds = timeout_seconds

    async def execute(self, command: str) -> ShellResult:
        if not command.strip():
            return ShellResult(ok=False, exit_code=1, stdout="", stderr="COMMAND_REQUIRED")

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=self.timeout_seconds)
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            return ShellResult(ok=False, exit_code=124, stdout="", stderr="TIMEOUT")

        stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
        stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""
        return ShellResult(ok=process.returncode == 0, exit_code=process.returncode or 0, stdout=stdout, stderr=stderr)

    async def stream(self, command: str) -> list[dict[str, Any]]:
        """Executa comando e devolve lista de eventos de stream para o backend."""

        result = await self.execute(command)
        events: list[dict[str, Any]] = []
        if result.stdout:
            events.append({"stream": "stdout", "content": result.stdout})
        if result.stderr:
            events.append({"stream": "stderr", "content": result.stderr})
        return events
