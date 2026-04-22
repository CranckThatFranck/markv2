"""Gerenciamento de streams de execucao do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class StreamBuffer:
    stdout: list[str] = field(default_factory=list)
    stderr: list[str] = field(default_factory=list)


class StreamManager:
    """Acumula saidas de stdout e stderr para uma task em andamento."""

    def __init__(self) -> None:
        self._buffers: dict[str, StreamBuffer] = {}

    def append_stdout(self, task_id: str, content: str) -> None:
        self._buffers.setdefault(task_id, StreamBuffer()).stdout.append(content)

    def append_stderr(self, task_id: str, content: str) -> None:
        self._buffers.setdefault(task_id, StreamBuffer()).stderr.append(content)

    def get_buffer(self, task_id: str) -> StreamBuffer:
        return self._buffers.setdefault(task_id, StreamBuffer())
