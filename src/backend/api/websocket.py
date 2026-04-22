"""Canal WebSocket principal do Mark Core v2."""

from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.backend.models.registry import ModelRegistry
from src.backend.models.credentials.provider_store import ProviderStore
from src.backend.protocol.actions import ActionName, is_valid_action
from src.backend.protocol.schemas import (
    InputEnvelope,
    error_response,
    success_response,
)
from src.backend.session.history_store import HistoryStore
from src.backend.session.session_store import SessionStore
from src.backend.session.state_manager import StateManager
from src.backend.runtime.paths import build_runtime_layout

router = APIRouter(tags=["websocket"])


_runtime_layout = build_runtime_layout()
state_manager = StateManager(base_dir=_runtime_layout.runtime_dir)
session_store = SessionStore(base_dir=_runtime_layout.runtime_dir)
history_store = HistoryStore(base_dir=_runtime_layout.runtime_dir)
model_registry = ModelRegistry(base_dir=_runtime_layout.runtime_dir)
provider_store = ProviderStore(base_dir=_runtime_layout.runtime_dir)


def _build_models_payload() -> dict[str, list[str]]:
    return {
        "builtin": model_registry.list_builtin(),
        "custom": model_registry.list_custom(),
        "all": model_registry.list_all(),
    }


def _build_sync_state() -> dict[str, object]:
    return state_manager.to_sync_state(
        providers=provider_store.to_sync_providers_payload(),
        models=_build_models_payload(),
        credentials_status=provider_store.get_credentials_status(),
        history=history_store.list_events(limit=50),
    )


async def _send_sync_state(websocket: WebSocket) -> None:
    await websocket.send_json(_build_sync_state())


async def _handle_action(websocket: WebSocket, envelope: InputEnvelope) -> None:
    action = envelope.action

    if not is_valid_action(action):
        await websocket.send_json(
            error_response(action=action, error_code="ACTION_NOT_FOUND", message="Ação desconhecida.").model_dump()
        )
        return

    if action == ActionName.HEALTHCHECK.value:
        await websocket.send_json(success_response(action, {"status": "ok"}).model_dump())
        return

    if action == ActionName.GET_STATUS.value:
        await websocket.send_json(
            success_response(
                action,
                {
                    "state": _build_sync_state()["state"],
                },
            ).model_dump()
        )
        return

    if action == ActionName.GET_CONFIG.value:
        await websocket.send_json(
            success_response(
                action,
                {
                    "state": _build_sync_state()["state"],
                    "providers": provider_store.to_sync_providers_payload(),
                    "models": _build_models_payload(),
                    "session": session_store.load(),
                },
            ).model_dump()
        )
        return

    if action == ActionName.GET_HISTORY.value:
        await websocket.send_json(
            success_response(action, {"items": history_store.list_events(limit=100)}).model_dump()
        )
        return

    if action == ActionName.CLEAR_SESSION.value:
        session_store.clear()
        state_manager.set_active_task(None)
        await websocket.send_json(success_response(action, {"cleared": True}).model_dump())
        await _send_sync_state(websocket)
        return

    await websocket.send_json(
        error_response(
            action=action,
            error_code="ACTION_NOT_IMPLEMENTED",
            message="Ação reconhecida, mas ainda não implementada.",
        ).model_dump()
    )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Aceita conexao e processa o contrato JSON do backend."""

    await websocket.accept()
    await websocket.send_json(
        {
            "type": "system",
            "protocol_version": "2.0",
            "message": "Conexao WebSocket estabelecida.",
        }
    )
    await _send_sync_state(websocket)

    try:
        while True:
            payload = await websocket.receive_text()

            try:
                raw_payload = json.loads(payload)
                envelope = InputEnvelope.model_validate(raw_payload)
            except Exception:
                await websocket.send_json(
                    error_response(
                        action="unknown",
                        error_code="INVALID_PAYLOAD",
                        message="Payload invalido para o protocolo JSON.",
                    ).model_dump()
                )
                continue

            await _handle_action(websocket, envelope)
    except WebSocketDisconnect:
        return
