"""Gerenciamento do estado operacional do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RuntimePaths:
    """Caminhos relevantes expostos no estado sincronizado."""

    base_dir: str = "/var/lib/jarvis-mark"
    rules_file: str = "/opt/jarvis/backend/product_config/initial_rules.txt"
    rules_dir: str = "/opt/jarvis/backend/product_config"


@dataclass(slots=True)
class BackendState:
    """Estado atual em memoria do backend v2."""

    agent_name: str = "Mark Core v2"
    mode: str = "agent"
    status: str = "idle"
    provider: str = "google_ai"
    model: str = "gemini/gemini-2.5-flash"
    active_task_id: str | None = None
    history_revision: int = 0
    paths: RuntimePaths = field(default_factory=RuntimePaths)


class StateManager:
    """Controla leitura, atualização e serialização do estado atual."""

    def __init__(self, base_dir: str = "/var/lib/jarvis-mark/estado") -> None:
        self._state = BackendState()
        self._base_dir = Path(base_dir)

    @property
    def state(self) -> BackendState:
        return self._state

    def set_status(self, status: str) -> None:
        self._state.status = status

    def set_mode(self, mode: str) -> None:
        self._state.mode = mode

    def set_model_and_provider(self, model: str, provider: str) -> None:
        self._state.model = model
        self._state.provider = provider

    def set_active_task(self, task_id: str | None) -> None:
        self._state.active_task_id = task_id

    def bump_history_revision(self) -> int:
        self._state.history_revision += 1
        return self._state.history_revision

    def to_sync_state(
        self,
        providers: dict[str, Any] | None = None,
        models: dict[str, Any] | None = None,
        credentials_status: dict[str, Any] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Serializa o estado no formato esperado para evento sync_state."""

        return {
            "type": "sync_state",
            "protocol_version": "2.0",
            "state": {
                "agent_name": self._state.agent_name,
                "mode": self._state.mode,
                "status": self._state.status,
                "provider": self._state.provider,
                "model": self._state.model,
                "active_task_id": self._state.active_task_id,
                "history_revision": self._state.history_revision,
                "paths": {
                    "base_dir": self._state.paths.base_dir,
                    "rules_file": self._state.paths.rules_file,
                    "rules_dir": self._state.paths.rules_dir,
                },
            },
            "providers": providers or {"available": ["google_ai", "vertex_ai"], "active": self._state.provider},
            "models": models or {"builtin": [], "custom": [], "all": []},
            "credentials_status": credentials_status or {},
            "history": history or [],
        }
