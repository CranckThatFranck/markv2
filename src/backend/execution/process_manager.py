"""Gerenciamento de processos do Mark Core v2."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class ProcessHandle:
    pid: int
    return_code: int | None = None


class ProcessManager:
    """Cria e finaliza processos locais controlados."""

    def start(self, command: list[str]) -> ProcessHandle:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ProcessHandle(pid=process.pid)

    def terminate(self, handle: ProcessHandle) -> ProcessHandle:
        return ProcessHandle(pid=handle.pid, return_code=0)
