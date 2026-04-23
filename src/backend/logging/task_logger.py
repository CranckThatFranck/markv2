"""Camada de logging do Mark Core v2."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class TaskLogger:
    """Registra eventos de execução de tarefas."""

    def __init__(self) -> None:
        self.log_dir = Path("/tmp/mark-core-v2-logs")
        self.log_dir.mkdir(exist_ok=True, parents=True)

    def log_task_execution(self, task_id: str, event_type: str, data: dict[str, object]) -> None:
        """Registra um evento de execução de tarefa."""

        log_file = self.log_dir / "task_execution.log"
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "task_id": task_id,
            "event_type": event_type,
            "data": data,
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_rule_application(self, task_id: str, mode: str, rules_applied: list[str], decision: str) -> None:
        """Registra quais regras foram aplicadas no decision making."""

        self.log_task_execution(
            task_id,
            "rule_application",
            {
                "mode": mode,
                "rules_applied": rules_applied,
                "decision": decision,
            },
        )

    def log_agent_decision(self, task_id: str, decision_type: str, tool_name: str | None, reason: str) -> None:
        """Registra a decisão do agente."""

        self.log_task_execution(
            task_id,
            "agent_decision",
            {
                "decision_type": decision_type,
                "tool_name": tool_name,
                "reason": reason,
            },
        )

    def log_tool_execution(
        self,
        task_id: str,
        tool_name: str,
        command: str,
        ok: bool,
        exit_code: int,
        duration_ms: int,
    ) -> None:
        """Registra a execução de uma ferramenta."""

        self.log_task_execution(
            task_id,
            "tool_execution",
            {
                "tool_name": tool_name,
                "command": command,
                "ok": ok,
                "exit_code": exit_code,
                "duration_ms": duration_ms,
            },
        )

    def log_provider_event(self, task_id: str, event_name: str, data: dict[str, object]) -> None:
        """Registra evento de provider, fallback ou rotação sem segredos."""

        self.log_task_execution(task_id, event_name, data)


class BackendLogger:
    """Registra eventos gerais do backend."""

    def __init__(self) -> None:
        self.log_dir = Path("/tmp/mark-core-v2-logs")
        self.log_dir.mkdir(exist_ok=True, parents=True)

    def log_startup(self, version: str, config_path: str, rules_path: str) -> None:
        """Registra o startup do backend."""

        log_file = self.log_dir / "backend.log"
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "event": "startup",
            "version": version,
            "config_path": config_path,
            "rules_path": rules_path,
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_execute_task(self, task_id: str, mode: str, provider: str, model_id: str) -> None:
        """Registra uma execução de tarefa."""

        log_file = self.log_dir / "backend.log"
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "event": "execute_task",
            "task_id": task_id,
            "mode": mode,
            "provider": provider,
            "model_id": model_id,
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_interrupt(self, task_id: str) -> None:
        """Registra uma interrupção."""

        log_file = self.log_dir / "backend.log"
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "event": "interrupt",
            "task_id": task_id,
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_error(self, error_code: str, message: str, context: dict[str, object] | None = None) -> None:
        """Registra um erro."""

        log_file = self.log_dir / "errors.log"
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "error_code": error_code,
            "message": message,
            "context": context or {},
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
