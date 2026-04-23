"""Cliente WebSocket assíncrono usado pelo frontend."""

from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import Callable
from concurrent.futures import Future
from typing import Any

import websockets
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed


EventCallback = Callable[[dict[str, Any]], None]
StateCallback = Callable[[str], None]
ErrorCallback = Callable[[str], None]


class BackendWebSocketClient:
    """Mantem conexao WebSocket em thread separada com reconexao automatica."""

    def __init__(
        self,
        url: str,
        on_event: EventCallback,
        on_state_change: StateCallback,
        on_error: ErrorCallback,
    ) -> None:
        self.url = url
        self.on_event = on_event
        self.on_state_change = on_state_change
        self.on_error = on_error
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop_event = threading.Event()
        self._ws: WebSocketClientProtocol | None = None
        self._ws_lock: asyncio.Lock | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="mark-core-v2-frontend-ws", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._loop is not None:
            if self._ws is not None:
                asyncio.run_coroutine_threadsafe(self._ws.close(), self._loop)
            self._loop.call_soon_threadsafe(lambda: None)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._thread = None

    def update_url(self, url: str) -> None:
        self.url = url
        self.restart()

    def restart(self) -> None:
        self.stop()
        self.start()

    def send_action(self, action: str, payload: dict[str, Any] | None = None) -> Future[Any] | None:
        if self._loop is None:
            self.on_error("Cliente WebSocket ainda nao inicializado.")
            return None

        return asyncio.run_coroutine_threadsafe(
            self._send_json(
                {
                    "protocol_version": "2.0",
                    "action": action,
                    "payload": payload or {},
                }
            ),
            self._loop,
        )

    def _run_loop(self) -> None:
        loop = asyncio.new_event_loop()
        self._loop = loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._connection_loop())
        finally:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.close()
            self._loop = None

    async def _connection_loop(self) -> None:
        while not self._stop_event.is_set():
            self.on_state_change("connecting")
            try:
                async with websockets.connect(self.url, open_timeout=10, close_timeout=10) as websocket:
                    self._ws = websocket
                    self._ws_lock = asyncio.Lock()
                    self.on_state_change("connected")
                    async for raw_message in websocket:
                        try:
                            message = json.loads(raw_message)
                        except json.JSONDecodeError:
                            self.on_error("Mensagem JSON invalida recebida do backend.")
                            continue
                        self.on_event(message)
            except Exception as exc:
                self.on_error(f"Falha na conexao WebSocket: {exc}")
                self.on_state_change("disconnected")
                await asyncio.sleep(2)
            finally:
                self._ws = None
                self._ws_lock = None

    async def _send_json(self, payload: dict[str, Any]) -> None:
        if self._ws is None or self._ws_lock is None:
            self.on_error("Backend desconectado.")
            return

        try:
            async with self._ws_lock:
                await self._ws.send(json.dumps(payload))
        except ConnectionClosed:
            self.on_error("Conexao WebSocket encerrada durante envio.")
        except Exception as exc:
            self.on_error(f"Falha ao enviar mensagem: {exc}")
