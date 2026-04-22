"""Gerenciamento de processos do Mark Core v2."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import os
import signal


@dataclass(slots=True)
class ProcessHandle:
    task_id: str
    pid: int
    pgid: int
    process: asyncio.subprocess.Process
    return_code: int | None = None


class ProcessManager:
    """Cria e finaliza processos locais controlados."""

    def __init__(self) -> None:
        self._handles: dict[str, ProcessHandle] = {}

    async def start(self, task_id: str, command: str) -> ProcessHandle:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=os.setsid,
        )
        pid = process.pid or -1
        try:
            pgid = os.getpgid(pid) if pid > 0 else -1
        except ProcessLookupError:
            pgid = -1

        handle = ProcessHandle(task_id=task_id, pid=pid, pgid=pgid, process=process)
        self._handles[task_id] = handle
        return handle

    async def wait(self, handle: ProcessHandle, timeout_seconds: int) -> int:
        try:
            return_code = await asyncio.wait_for(handle.process.wait(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            self.interrupt(handle.task_id)
            await handle.process.wait()
            return_code = 124
        handle.return_code = return_code
        self._handles.pop(handle.task_id, None)
        return return_code

    def get(self, task_id: str | None) -> ProcessHandle | None:
        if not task_id:
            return None
        return self._handles.get(task_id)

    def interrupt(self, task_id: str | None) -> bool:
        handle = self.get(task_id)
        if handle is None:
            return False
        try:
            if handle.pgid > 0:
                os.killpg(handle.pgid, signal.SIGTERM)
            elif handle.pid > 0:
                os.kill(handle.pid, signal.SIGTERM)
            return True
        except ProcessLookupError:
            return False
        finally:
            self._handles.pop(handle.task_id, None)

    def clear(self) -> None:
        self._handles.clear()
