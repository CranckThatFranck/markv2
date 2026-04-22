"""Roteador minimo de ferramentas para o agent loop."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

ToolHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class ToolRouter:
    """Registra e despacha chamadas de ferramentas de forma controlada."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolHandler] = {}

    def register_tool(self, name: str, handler: ToolHandler) -> None:
        if not name.strip():
            raise ValueError("TOOL_NAME_REQUIRED")
        self._tools[name] = handler

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    async def dispatch(self, name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
        handler = self._tools.get(name)
        if handler is None:
            raise ValueError("TOOL_NOT_FOUND")
        return await handler(tool_input)
