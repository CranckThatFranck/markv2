"""Schemas base do protocolo JSON/WebSocket do Mark Core v2."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

PROTOCOL_VERSION = "2.0"


class InputEnvelope(BaseModel):
    """Envelope de entrada das acoes enviadas pelo cliente."""

    protocol_version: str = Field(default=PROTOCOL_VERSION)
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ActionResponse(BaseModel):
    """Envelope de saida para respostas estruturadas de acoes."""

    type: Literal["action_response"] = "action_response"
    protocol_version: str = Field(default=PROTOCOL_VERSION)
    action: str
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    message: str | None = None


class BaseEvent(BaseModel):
    """Evento generico de stream no canal WebSocket."""

    type: str
    protocol_version: str = Field(default=PROTOCOL_VERSION)


class SystemEvent(BaseEvent):
    type: Literal["system"] = "system"
    message: str


class StatusEvent(BaseEvent):
    type: Literal["status"] = "status"
    phase: Literal["START", "END"]
    action: str
    task_id: str


class MessageEvent(BaseEvent):
    type: Literal["message"] = "message"
    content: str


class ConsoleEvent(BaseEvent):
    type: Literal["console"] = "console"
    stream: Literal["stdout", "stderr"]
    content: str


class ProviderEvent(BaseEvent):
    type: Literal["provider_event"] = "provider_event"
    event: str
    provider: str | None = None
    from_provider: str | None = None
    to_provider: str | None = None
    from_model: str | None = None
    to_model: str | None = None
    from_credential_id: str | None = None
    to_credential_id: str | None = None
    level: str | None = None
    reason: str | None = None


class SyncStateEvent(BaseEvent):
    type: Literal["sync_state"] = "sync_state"
    state: dict[str, Any]
    providers: dict[str, Any]
    models: dict[str, Any]
    credentials_status: dict[str, Any]
    history: list[dict[str, Any]] = Field(default_factory=list)


def success_response(action: str, data: dict[str, Any] | None = None) -> ActionResponse:
    """Gera resposta de sucesso padronizada."""

    return ActionResponse(action=action, success=True, data=data or {})


def error_response(action: str, error_code: str, message: str) -> ActionResponse:
    """Gera resposta de erro padronizada."""

    return ActionResponse(
        action=action,
        success=False,
        error_code=error_code,
        message=message,
    )
