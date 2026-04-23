"""Planejador minimo para modo Plan do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PlanStep:
    index: int
    title: str


class Planner:
    """Converte uma tarefa em uma sequencia simples de passos."""

    def build_plan(self, prompt: str, mode: str = "plan", rules: list[str] | None = None) -> list[PlanStep]:
        text = (prompt or "").strip()
        if not text:
            return [
                PlanStep(index=1, title="Coletar contexto da tarefa"),
                PlanStep(index=2, title="Definir abordagem"),
            ]

        steps = [
            PlanStep(index=1, title="Entender objetivo e restricoes"),
            PlanStep(index=2, title="Executar analise orientada por evidencia"),
            PlanStep(index=3, title=f"Concluir tarefa: {text}"),
        ]

        # Add a step about tool availability if in plan mode with rules
        if mode == "plan" and rules:
            for rule in rules:
                if "Plan" in rule and "sensiveis" in rule.lower():
                    steps.append(PlanStep(index=len(steps) + 1, title="[Limitacao] Ferramentas sensiveis nao disponiveis neste modo"))
                    break

        return steps

    def render_plan_message(self, prompt: str, mode: str = "plan", rules: list[str] | None = None) -> str:
        steps = self.build_plan(prompt, mode, rules)
        lines = ["Plano proposto:"]
        for step in steps:
            lines.append(f"{step.index}. {step.title}")

        if mode == "plan":
            lines.append("\n[MODO PLAN] Este plano nao sera executado agora.")
            lines.append("Para executar com seguranca, mude para modo 'agent' e execute novamente.")

        return "\n".join(lines)
