"""Tipos de eventos e helpers de construcao do protocolo v2."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from .schemas import PROTOCOL_VERSION


class EventType(StrEnum):
    SYNC_STATE = "sync_state"
    STATUS = "status"
    SYSTEM = "system"
    USER = "user"
    MESSAGE = "message"
    CODE = "code"
    CONSOLE = "console"
    PROVIDER_EVENT = "provider_event"


def build_system_event(message: str) -> dict[str, Any]:
    return {
        "type": EventType.SYSTEM.value,
        "protocol_version": PROTOCOL_VERSION,
        "message": message,
    }


def build_status_event(phase: str, action: str, task_id: str) -> dict[str, Any]:
    return {
        "type": EventType.STATUS.value,
        "protocol_version": PROTOCOL_VERSION,
        "phase": phase,
        "action": action,
        "task_id": task_id,
    }


def build_message_event(content: str) -> dict[str, Any]:
    return {
        "type": EventType.MESSAGE.value,
        "protocol_version": PROTOCOL_VERSION,
        "content": content,
    }


def build_console_event(stream: str, content: str) -> dict[str, Any]:
    return {
        "type": EventType.CONSOLE.value,
        "protocol_version": PROTOCOL_VERSION,
        "stream": stream,
        "content": content,
    }


def build_provider_event(event: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "type": EventType.PROVIDER_EVENT.value,
        "protocol_version": PROTOCOL_VERSION,
        "event": event,
    }
    if data:
        payload.update(data)
    return payload
