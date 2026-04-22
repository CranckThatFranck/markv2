"""Gerenciamento de streams de execucao do Mark Core v2."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Awaitable, Callable


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

    async def _stream_reader(
        self,
        task_id: str,
        reader: asyncio.StreamReader,
        stream: str,
        emit_console: Callable[[str, str], Awaitable[None]],
    ) -> None:
        while True:
            chunk = await reader.readline()
            if not chunk:
                break
            content = chunk.decode("utf-8", errors="replace")
            if stream == "stdout":
                self.append_stdout(task_id, content)
            else:
                self.append_stderr(task_id, content)
            await emit_console(stream, content)

    async def stream_process(
        self,
        task_id: str,
        stdout: asyncio.StreamReader | None,
        stderr: asyncio.StreamReader | None,
        emit_console: Callable[[str, str], Awaitable[None]],
    ) -> None:
        tasks: list[asyncio.Task[None]] = []
        if stdout is not None:
            tasks.append(asyncio.create_task(self._stream_reader(task_id, stdout, "stdout", emit_console)))
        if stderr is not None:
            tasks.append(asyncio.create_task(self._stream_reader(task_id, stderr, "stderr", emit_console)))

        if tasks:
            await asyncio.gather(*tasks)
