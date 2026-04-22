"""Execucao controlada e minima de tasks do Mark Core v2."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable

from fastapi import WebSocket

from src.backend.protocol.schemas import error_response, success_response
from src.backend.runtime.rules import build_rules_runtime
from src.backend.session.state_manager import StateManager
from src.backend.session.history_store import HistoryStore


@dataclass(slots=True)
class TaskContext:
    task_id: str
    prompt: str
    rules_text: str
    cancelled: bool = False


class TaskExecutionService:
    """Mantem uma task ativa por vez e emite eventos coerentes no WebSocket."""

    def __init__(self, state_manager: StateManager, history_store: HistoryStore) -> None:
        self.state_manager = state_manager
        self.history_store = history_store
        self.rules_runtime = build_rules_runtime()
        self._active_context: TaskContext | None = None
        self._active_task: asyncio.Task[None] | None = None
        self._shutdown_requested = False

    @property
    def rules_file(self) -> str:
        return str(self.rules_runtime.rules_file)

    @property
    def rules_text(self) -> str:
        return self.rules_runtime.rules_text

    @property
    def active_task_id(self) -> str | None:
        return self._active_context.task_id if self._active_context else None

    def is_running(self) -> bool:
        return self._active_task is not None and not self._active_task.done()

    async def execute_task(
        self,
        websocket: WebSocket,
        prompt: str,
        emit_state: Callable[[], Awaitable[None]],
    ) -> dict[str, object]:
        if self.is_running():
            return error_response(
                action="execute_task",
                error_code="TASK_ALREADY_RUNNING",
                message="Ja existe uma task em execucao.",
            ).model_dump()

        task_id = f"task-{uuid.uuid4().hex[:12]}"
        self._active_context = TaskContext(task_id=task_id, prompt=prompt, rules_text=self.rules_text)
        self.state_manager.set_active_task(task_id)
        self.state_manager.set_status("running")
        self.state_manager.bump_history_revision()
        self.history_store.append_event(task_id, "system", "Task iniciada")
        self.history_store.append_event(task_id, "user", prompt)

        await websocket.send_json(
            {
                "type": "status",
                "protocol_version": "2.0",
                "phase": "START",
                "action": "execute_task",
                "task_id": task_id,
            }
        )
        await websocket.send_json(
            {
                "type": "user",
                "protocol_version": "2.0",
                "content": prompt,
            }
        )
        await websocket.send_json(
            {
                "type": "system",
                "protocol_version": "2.0",
                "message": "Regras iniciais carregadas para a task.",
            }
        )
        await websocket.send_json(
            {
                "type": "message",
                "protocol_version": "2.0",
                "content": f"Executando task controlada com base em {self.rules_file}.",
            }
        )

        async def _run() -> None:
            try:
                for _ in range(30):
                    await asyncio.sleep(0.1)
                    if self._active_context is None or self._active_context.cancelled:
                        return

                if self._active_context is None or self._active_context.cancelled:
                    return

                final_message = f"Task concluida com prompt: {prompt.strip()}"
                self.history_store.append_event(task_id, "message", final_message)
                self.state_manager.set_status("idle")
                self.state_manager.set_active_task(None)
                self.state_manager.bump_history_revision()
                await websocket.send_json(
                    {
                        "type": "message",
                        "protocol_version": "2.0",
                        "content": final_message,
                    }
                )
                await websocket.send_json(
                    {
                        "type": "system",
                        "protocol_version": "2.0",
                        "message": "Task finalizada.",
                    }
                )
                await websocket.send_json(
                    {
                        "type": "status",
                        "protocol_version": "2.0",
                        "phase": "END",
                        "action": "execute_task",
                        "task_id": task_id,
                    }
                )
                await emit_state()
            finally:
                self._active_context = None
                self._active_task = None

        self._active_task = asyncio.create_task(_run())

        return success_response(
            "execute_task",
            {
                "task_id": task_id,
                "status": "running",
                "rules_file": self.rules_file,
            },
        ).model_dump()

    async def interrupt(self, websocket: WebSocket) -> dict[str, object]:
        if self._active_context is None:
            return error_response(
                action="interrupt",
                error_code="TASK_NOT_FOUND",
                message="Nenhuma task ativa.",
            ).model_dump()

        task_id = self._active_context.task_id
        self._active_context.cancelled = True
        self.state_manager.set_status("idle")
        self.state_manager.set_active_task(None)
        self.state_manager.bump_history_revision()
        self.history_store.append_event(task_id, "system", "Task interrompida")
        if self._active_task is not None:
            self._active_task.cancel()
        self._active_context = None
        self._active_task = None

        await websocket.send_json(
            {
                "type": "system",
                "protocol_version": "2.0",
                "message": f"Task {task_id} interrompida.",
            }
        )
        await websocket.send_json(
            {
                "type": "status",
                "protocol_version": "2.0",
                "phase": "END",
                "action": "interrupt",
                "task_id": task_id,
            }
        )
        return success_response(
            "interrupt",
            {
                "task_id": task_id,
                "interrupted": True,
            },
        ).model_dump()

    async def shutdown_backend(self, websocket: WebSocket) -> dict[str, object]:
        self._shutdown_requested = True
        if self._active_context is not None:
            self._active_context.cancelled = True
        if self._active_task is not None:
            self._active_task.cancel()
        self.state_manager.set_status("idle")
        self.state_manager.set_active_task(None)
        self.state_manager.bump_history_revision()
        await websocket.send_json(
            {
                "type": "system",
                "protocol_version": "2.0",
                "message": "Shutdown solicitado.",
            }
        )
        return success_response(
            "shutdown_backend",
            {
                "shutdown": True,
            },
        ).model_dump()