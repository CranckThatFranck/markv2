"""Execucao controlada e minima de tasks do Mark Core v2."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable

from fastapi import WebSocket

from src.backend.models.providers.google_ai_client import GoogleAIClient
from src.backend.models.providers.vertex_ai_client import VertexAIClient
from src.backend.models.router import ModelRouter
from src.backend.protocol.schemas import error_response, success_response
from src.backend.runtime.credentials import CredentialRuntime
from src.backend.runtime.rules import build_rules_runtime
from src.backend.session.history_store import HistoryStore
from src.backend.session.session_store import SessionStore
from src.backend.session.state_manager import StateManager


@dataclass(slots=True)
class TaskContext:
    task_id: str
    prompt: str
    rules_text: str
    provider: str
    model_id: str
    cancelled: bool = False


class TaskExecutionService:
    """Mantem uma task ativa por vez e emite eventos coerentes no WebSocket."""

    def __init__(
        self,
        state_manager: StateManager,
        history_store: HistoryStore,
        session_store: SessionStore,
        credential_runtime: CredentialRuntime,
        model_router: ModelRouter,
    ) -> None:
        self.state_manager = state_manager
        self.history_store = history_store
        self.session_store = session_store
        self.credential_runtime = credential_runtime
        self.model_router = model_router
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

    def _validate_provider_ready(self, provider: str) -> bool:
        status = self.credential_runtime.get_credentials_status().get(provider, {})
        return bool(status.get("configured"))

    async def _execute_with_provider(self, provider: str, model_id: str, prompt: str) -> tuple[bool, str, str]:
        if provider == "google_ai":
            google_api_key = self.credential_runtime.get_google_api_key()
            result = await asyncio.to_thread(
                GoogleAIClient(api_key=google_api_key).generate_text,
                prompt,
                model_id,
            )
        elif provider == "vertex_ai":
            active_vertex = self.credential_runtime.get_vertex_active_credential()
            if not active_vertex:
                return False, "AUTHENTICATION_FAILED", "Credenciais Vertex AI ausentes."
            result = await asyncio.to_thread(
                VertexAIClient(
                    credentials_path=active_vertex["service_account_path"],
                    project=active_vertex["project"],
                    location=active_vertex["location"],
                ).generate_text,
                prompt,
                model_id,
            )
        else:
            return False, "PROVIDER_NOT_FOUND", "Provider desconhecido."

        if result.ok:
            return True, "OK", result.text or ""
        return False, result.error_code or "PROVIDER_ERROR", result.message or "Falha no provider."

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

        model_id = self.state_manager.state.model
        provider = self.model_router.resolve_provider(model_id, self.state_manager.state.provider)
        if not self._validate_provider_ready(provider):
            return error_response(
                action="execute_task",
                error_code="CREDENTIAL_NOT_CONFIGURED",
                message=f"Provider {provider} sem credencial configurada.",
            ).model_dump()

        self.state_manager.set_model_and_provider(model_id, provider)

        task_id = f"task-{uuid.uuid4().hex[:12]}"
        self._active_context = TaskContext(
            task_id=task_id,
            prompt=prompt,
            rules_text=self.rules_text,
            provider=provider,
            model_id=model_id,
        )
        self.state_manager.set_active_task(task_id)
        self.state_manager.set_status("running")
        self.state_manager.bump_history_revision()
        self.history_store.bump_history_revision()
        self.session_store.set_active_session(task_id, prompt, self.rules_file, self.state_manager.state.history_revision)
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

                ok, code, output = await self._execute_with_provider(provider, model_id, prompt)
                if not ok:
                    self.history_store.append_event(task_id, "system", f"Provider error {code}: {output}")
                    await websocket.send_json(
                        error_response(
                            action="execute_task",
                            error_code=code,
                            message=output,
                        ).model_dump()
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
                    self.state_manager.set_status("idle")
                    self.state_manager.set_active_task(None)
                    self.state_manager.bump_history_revision()
                    self.history_store.bump_history_revision()
                    self.session_store.set_idle_session(self.state_manager.state.history_revision, last_task_id=task_id)
                    await emit_state()
                    return

                final_message = output
                self.history_store.append_event(task_id, "message", final_message)
                self.state_manager.set_status("idle")
                self.state_manager.set_active_task(None)
                self.state_manager.bump_history_revision()
                self.history_store.bump_history_revision()
                self.session_store.set_idle_session(self.state_manager.state.history_revision, last_task_id=task_id)
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
                "provider": provider,
                "model_id": model_id,
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
        self.history_store.bump_history_revision()
        self.session_store.set_idle_session(self.state_manager.state.history_revision, last_task_id=task_id)
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
        last_task_id = self._active_context.task_id if self._active_context else None
        if self._active_context is not None:
            self._active_context.cancelled = True
        if self._active_task is not None:
            self._active_task.cancel()
        self.state_manager.set_status("idle")
        self.state_manager.set_active_task(None)
        self.state_manager.bump_history_revision()
        self.history_store.bump_history_revision()
        self.session_store.set_idle_session(self.state_manager.state.history_revision, last_task_id=last_task_id)
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

    async def clear_session(self, websocket: WebSocket) -> dict[str, object]:
        last_task_id = self._active_context.task_id if self._active_context else None
        if self._active_task is not None:
            self._active_context = None
            self._active_task.cancel()
            self._active_task = None

        self.state_manager.set_status("idle")
        self.state_manager.set_active_task(None)
        new_revision = self.state_manager.bump_history_revision()
        self.history_store.bump_history_revision()
        self.history_store.clear()
        self.history_store.sync_history_revision(new_revision)
        self.session_store.set_idle_session(new_revision, last_task_id=last_task_id)
        await websocket.send_json(
            {
                "type": "system",
                "protocol_version": "2.0",
                "message": "Sessao limpa.",
            }
        )
        return success_response(
            "clear_session",
            {
                "cleared": True,
                "history_revision": new_revision,
            },
        ).model_dump()