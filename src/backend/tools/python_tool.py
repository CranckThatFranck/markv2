"""Ferramenta Python controlada do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PythonToolResult:
    ok: bool
    output: Any
    error: str | None = None


class PythonTool:
    """Executa snippets Python em ambiente controlado e retornando resultado simples."""

    def run_expression(self, expression: str, context: dict[str, Any] | None = None) -> PythonToolResult:
        if not expression.strip():
            return PythonToolResult(ok=False, output=None, error="EXPRESSION_REQUIRED")

        safe_globals = {"__builtins__": {"len": len, "str": str, "int": int, "float": float, "bool": bool, "dict": dict, "list": list, "set": set, "tuple": tuple}}
        safe_locals = dict(context or {})
        try:
            result = eval(expression, safe_globals, safe_locals)
        except Exception as exc:  # noqa: BLE001
            return PythonToolResult(ok=False, output=None, error=str(exc))
        return PythonToolResult(ok=True, output=result)
