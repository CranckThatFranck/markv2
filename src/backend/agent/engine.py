"""Motor agentico minimo do Mark Core v2."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal


DecisionType = Literal["final_answer", "use_tool"]


@dataclass(slots=True)
class AgentDecision:
    """Estrutura de decisao retornada pelo modelo para o loop agentico."""

    mode: str
    decision: DecisionType
    reason: str | None = None
    message: str | None = None
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None


class AgentEngine:
    """Executa parse e validacao das decisoes estruturadas do agente."""

    def __init__(self, default_mode: str = "agent", max_iterations: int = 8) -> None:
        self.default_mode = default_mode
        self.max_iterations = max_iterations

    def parse_model_output(self, output: str) -> AgentDecision:
        """Converte resposta JSON do modelo em estrutura validada de decisao."""

        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            raise ValueError(f"MODEL_JSON_INVALID: {exc.msg}") from exc

        decision = payload.get("decision")
        if decision not in {"final_answer", "use_tool"}:
            raise ValueError("MODEL_DECISION_INVALID")

        mode = payload.get("mode") or self.default_mode

        if decision == "final_answer":
            message = payload.get("message")
            if not isinstance(message, str) or not message.strip():
                raise ValueError("MODEL_MESSAGE_REQUIRED")
            return AgentDecision(
                mode=mode,
                decision="final_answer",
                message=message.strip(),
                reason=payload.get("reason"),
            )

        tool_name = payload.get("tool_name")
        tool_input = payload.get("tool_input")
        if not isinstance(tool_name, str) or not tool_name.strip():
            raise ValueError("MODEL_TOOL_NAME_REQUIRED")
        if not isinstance(tool_input, dict):
            raise ValueError("MODEL_TOOL_INPUT_REQUIRED")

        return AgentDecision(
            mode=mode,
            decision="use_tool",
            tool_name=tool_name.strip(),
            tool_input=tool_input,
            reason=payload.get("reason"),
        )

    def build_iteration_guard(self, iteration: int) -> None:
        """Interrompe loop quando excede limite de iteracoes configurado."""

        if iteration >= self.max_iterations:
            raise RuntimeError("AGENT_MAX_ITERATIONS_REACHED")

    def fallback_failure_message(self, error: Exception) -> str:
        """Retorna mensagem legivel para falhas do loop agentico."""

        return f"Falha no loop agentico: {error}"
