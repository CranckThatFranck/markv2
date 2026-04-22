"""Canal WebSocket principal do Mark Core v2."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Aceita conexao e responde um evento basico de sistema."""
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "system",
            "protocol_version": "2.0",
            "message": "Conexao WebSocket estabelecida.",
        }
    )

    try:
        while True:
            _ = await websocket.receive_text()
            await websocket.send_json(
                {
                    "type": "system",
                    "protocol_version": "2.0",
                    "message": "Mensagem recebida.",
                }
            )
    except WebSocketDisconnect:
        return
