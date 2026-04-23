"""Execucao de tasks do Mark Core v2."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable

from .interrupt_manager import InterruptManager
from .process_manager import ProcessManager
from .stream_manager import StreamManager
from src.backend.tools.shell_tool import ShellTool


@dataclass(slots=True)
class TaskRunResult:
    task_id: str
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    pid: int
    pgid: int


class TaskRunner:
    """Coordena processo, streams e interrupcao de uma task."""

    def __init__(self, timeout_seconds: int = 60) -> None:
        self.timeout_seconds = timeout_seconds
        self.shell_tool = ShellTool(timeout_seconds=timeout_seconds)
        self.process_manager = ProcessManager()
        self.stream_manager = StreamManager()
        self.interrupt_manager = InterruptManager()

    async def run_command(
        self,
        task_id: str,
        command: str,
        emit_console: Callable[[str, str], Awaitable[None]],
        mode: str = "agent",
    ) -> TaskRunResult:
        normalized = command.strip()
        if not normalized:
            return TaskRunResult(
                task_id=task_id,
                ok=False,
                exit_code=1,
                stdout="",
                stderr="COMMAND_REQUIRED",
                pid=-1,
                pgid=-1,
            )

        guard = self.shell_tool.command_guard.check(normalized, mode=mode)
        if not guard.allowed:
            return TaskRunResult(
                task_id=task_id,
                ok=False,
                exit_code=126,
                stdout="",
                stderr=guard.reason or "COMMAND_BLOCKED",
                pid=-1,
                pgid=-1,
            )

        handle = await self.process_manager.start(task_id=task_id, command=normalized)
        await emit_console("stdout", f"[pid:{handle.pid} pgid:{handle.pgid}]\n")

        stream_task = asyncio.create_task(
            self.stream_manager.stream_process(
                task_id=task_id,
                stdout=handle.process.stdout,
                stderr=handle.process.stderr,
                emit_console=emit_console,
            )
        )
        exit_code = await self.process_manager.wait(handle, timeout_seconds=self.timeout_seconds)
        await stream_task

        buffer = self.stream_manager.get_buffer(task_id)
        stdout = "".join(buffer.stdout)
        stderr = "".join(buffer.stderr)
        if exit_code == 124:
            stderr = (stderr + "\nTIMEOUT").strip()

        return TaskRunResult(
            task_id=task_id,
            ok=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            pid=handle.pid,
            pgid=handle.pgid,
        )

    def interrupt(self, task_id: str | None) -> str:
        interrupted = self.process_manager.interrupt(task_id)
        if interrupted:
            return "INTERRUPTED"
        return self.interrupt_manager.interrupt(task_id).message
