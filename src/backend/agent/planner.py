"""Planejador minimo para modo Plan do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PlanStep:
    index: int
    title: str


class Planner:
    """Converte uma tarefa em uma sequencia simples de passos."""

    def build_plan(self, prompt: str) -> list[PlanStep]:
        text = (prompt or "").strip()
        if not text:
            return [PlanStep(index=1, title="Coletar contexto da tarefa"), PlanStep(index=2, title="Definir abordagem")]

        return [
            PlanStep(index=1, title="Entender objetivo e restricoes"),
            PlanStep(index=2, title="Executar analise orientada por evidencia"),
            PlanStep(index=3, title=f"Concluir tarefa: {text}"),
        ]

    def render_plan_message(self, prompt: str) -> str:
        steps = self.build_plan(prompt)
        lines = ["Plano proposto:"]
        for step in steps:
            lines.append(f"{step.index}. {step.title}")
        return "\n".join(lines)
