"""Execucao de tasks do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass

from .interrupt_manager import InterruptManager
from .process_manager import ProcessManager
from .stream_manager import StreamManager


@dataclass(slots=True)
class TaskRunResult:
    task_id: str
    ok: bool


class TaskRunner:
    """Coordena processo, streams e interrupcao de uma task."""

    def __init__(self) -> None:
        self.process_manager = ProcessManager()
        self.stream_manager = StreamManager()
        self.interrupt_manager = InterruptManager()

    def run_command(self, task_id: str, command: list[str]) -> TaskRunResult:
        handle = self.process_manager.start(command)
        self.stream_manager.append_stdout(task_id, f"started:{handle.pid}")
        self.process_manager.terminate(handle)
        return TaskRunResult(task_id=task_id, ok=True)

    def interrupt(self, task_id: str | None) -> str:
        return self.interrupt_manager.interrupt(task_id).message
