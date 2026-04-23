"""Motor agentico minimo do Mark Core v2."""

from __future__ import annotations

import json
import re
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

    def _extract_shell_command(self, prompt: str) -> str | None:
        text = (prompt or "").strip()
        if not text:
            return None

        prefixed = re.match(r"^(?:shell|run|cmd)\s*:\s*(.+)$", text, flags=re.IGNORECASE)
        if prefixed:
            return prefixed.group(1).strip()

        quoted = re.search(r"(?:comando|command)\s+[\"'`]([^\"'`]+)[\"'`]", text, flags=re.IGNORECASE)
        if quoted:
            return quoted.group(1).strip()

        direct_keywords = (
            " ls",
            " pwd",
            " whoami",
            " uname",
            " echo ",
            " cat ",
            " date",
            " sleep ",
            " ps ",
        )
        lowered = f" {text.lower()}"
        if any(k in lowered for k in direct_keywords):
            return text
        return None

    def decide(self, prompt: str, mode: str, rules_text: str | None = None) -> AgentDecision:
        """Decide entre resposta direta e uso de ferramenta via payload estruturado.
        
        Aplica regras iniciais para governar decisoes no modo Agent e Plan.
        Plan mode nunca executa ferramentas sensiveis conforme a regra:
        'O modo Plan nao executa acoes sensiveis.'
        """

        if mode == "plan":
            payload = {
                "mode": mode,
                "decision": "final_answer",
                "message": "__PLAN_RESPONSE__",
                "reason": "Modo plan responde sem executar ferramentas sensiveis.",
            }
            return self.parse_model_output(json.dumps(payload, ensure_ascii=False))

        shell_command = self._extract_shell_command(prompt)
        if shell_command:
            payload = {
                "mode": mode,
                "decision": "use_tool",
                "tool_name": "shell_tool",
                "tool_input": {"command": shell_command},
                "reason": "Prompt indica necessidade de execucao de comando shell.",
            }
            return self.parse_model_output(json.dumps(payload, ensure_ascii=False))

        payload = {
            "mode": mode,
            "decision": "final_answer",
            "message": "__PROVIDER_RESPONSE__",
            "reason": "Prompt elegivel para resposta direta do provider ativo.",
        }
        return self.parse_model_output(json.dumps(payload, ensure_ascii=False))
