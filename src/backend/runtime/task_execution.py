"""Execucao controlada e minima de tasks do Mark Core v2."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable

from fastapi import WebSocket

from src.backend.agent.context_builder import TaskContextBuilder
from src.backend.agent.engine import AgentDecision, AgentEngine
from src.backend.agent.planner import Planner
from src.backend.agent.tool_router import ToolRouter
from src.backend.execution.task_runner import TaskRunner
from src.backend.logging.task_logger import BackendLogger, TaskLogger
from src.backend.models.providers.google_ai_client import GoogleAIClient
from src.backend.models.providers.vertex_ai_client import VertexAIClient
from src.backend.models.router import ModelRouter
from src.backend.security.confirmations import ConfirmationPolicy
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
    mode: str
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
        self.agent_engine = AgentEngine(default_mode=state_manager.state.mode, max_iterations=6)
        self.planner = Planner()
        self.tool_router = ToolRouter()
        self.task_runner = TaskRunner(timeout_seconds=90)
        self.tool_router.register_tool("shell_tool", self._shell_tool_handler)
        self._active_context: TaskContext | None = None
        self._active_task: asyncio.Task[None] | None = None
        self._shutdown_requested = False
        self._dispatch_task_id: str | None = None
        self._dispatch_emit_console: Callable[[str, str], Awaitable[None]] | None = None
        self._dispatch_mode: str | None = None
        self.context_builder = TaskContextBuilder()
        self.task_logger = TaskLogger()
        self.backend_logger = BackendLogger()
        self.confirmation_policy = ConfirmationPolicy()

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

    async def _shell_tool_handler(self, tool_input: dict[str, object]) -> dict[str, object]:
        command = str(tool_input.get("command", "")).strip()
        if not command:
            raise ValueError("COMMAND_REQUIRED")
        if self._dispatch_task_id is None or self._dispatch_emit_console is None:
            raise RuntimeError("TOOL_ROUTER_CONTEXT_MISSING")

        mode = self._dispatch_mode or "agent"
        confirmation = self.confirmation_policy.requires_confirmation(command=command)
        if confirmation.required:
            return {
                "ok": False,
                "exit_code": 126,
                "stdout": "",
                "stderr": confirmation.reason or "CONFIRMATION_REQUIRED",
                "pid": -1,
                "pgid": -1,
                "command": command,
            }

        result = await self.task_runner.run_command(
            task_id=self._dispatch_task_id,
            command=command,
            emit_console=self._dispatch_emit_console,
            mode=mode,
        )
        return {
            "ok": result.ok,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "pid": result.pid,
            "pgid": result.pgid,
            "command": command,
        }

    async def _run_agent_loop(
        self,
        context: TaskContext,
        websocket: WebSocket,
    ) -> tuple[bool, str, str]:
        async def emit_console(stream: str, content: str) -> None:
            await websocket.send_json(
                {
                    "type": "console",
                    "protocol_version": "2.0",
                    "stream": stream,
                    "content": content,
                }
            )

        # Extract rules from the initial_rules.txt and log application
        rules_applied = self.context_builder._extract_rules(context.rules_text, context.mode)
        self.task_logger.log_rule_application(
            context.task_id,
            context.mode,
            rules_applied,
            "rules_loaded_for_decision_making",
        )

        decision: AgentDecision = self.agent_engine.decide(context.prompt, context.mode, rules_text=context.rules_text)

        # Log the agent decision
        self.task_logger.log_agent_decision(
            context.task_id,
            decision.decision,
            decision.tool_name,
            decision.reason or "no reason provided",
        )

        if decision.decision == "use_tool":
            tool_name = decision.tool_name or ""
            tool_input = decision.tool_input or {}
            command = str(tool_input.get("command", "")).strip()
            await websocket.send_json(
                {
                    "type": "code",
                    "protocol_version": "2.0",
                    "content": command,
                    "language": "bash",
                }
            )
            await websocket.send_json(
                {
                    "type": "system",
                    "protocol_version": "2.0",
                    "message": f"Executando ferramenta {tool_name}.",
                }
            )

            self._dispatch_task_id = context.task_id
            self._dispatch_emit_console = emit_console
            self._dispatch_mode = context.mode
            try:
                tool_result = await self.tool_router.dispatch(tool_name, tool_input)
            finally:
                self._dispatch_task_id = None
                self._dispatch_emit_console = None
                self._dispatch_mode = None

            if not bool(tool_result.get("ok")):
                blocked_reason = str(tool_result.get("stderr") or "COMMAND_BLOCKED")
                await websocket.send_json(
                    {
                        "type": "system",
                        "protocol_version": "2.0",
                        "message": f"Comando bloqueado pela política de segurança: {blocked_reason}",
                    }
                )
                return (
                    False,
                    "TOOL_EXECUTION_FAILED",
                    f"shell_tool bloqueou a execução (exit_code={tool_result.get('exit_code')}): {blocked_reason}",
                )

            stdout = str(tool_result.get("stdout", "")).strip()
            final = stdout or "Comando executado com sucesso sem saida visivel."
            return True, "OK", final

        if decision.message == "__PLAN_RESPONSE__":
            plan_message = self.planner.render_plan_message(context.prompt, context.mode, rules_applied)
            return True, "OK", plan_message

        return await self._execute_with_provider(context.provider, context.model_id, context.prompt)

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
        mode = self.state_manager.state.mode
        if not self._validate_provider_ready(provider):
            # Apenas modo agent depende de provider para resposta direta.
            if mode != "plan":
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
            mode=mode,
            provider=provider,
            model_id=model_id,
        )
        
        # Log task execution start
        self.backend_logger.log_execute_task(task_id, mode, provider, model_id)
        
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
                if self._active_context is None or self._active_context.cancelled:
                    return

                ok, code, output = await self._run_agent_loop(self._active_context, websocket)
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
        self.backend_logger.log_interrupt(task_id)
        self._active_context.cancelled = True
        self.task_runner.interrupt(task_id)
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
            self.task_runner.interrupt(self._active_context.task_id)
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
            self.task_runner.interrupt(last_task_id)
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