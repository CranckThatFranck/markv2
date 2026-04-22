"""Templates de prompt do Mark Core v2."""

from __future__ import annotations


def build_system_prompt(initial_rules: str, mode: str) -> str:
    """Monta prompt de sistema com regras iniciais e modo cognitivo."""

    rules = (initial_rules or "").strip()
    return (
        "Voce e o motor agentico do Mark Core v2. "
        "Responda sempre em JSON estruturado com decision=final_answer ou use_tool.\n"
        f"Modo atual: {mode}.\n"
        "Regras iniciais:\n"
        f"{rules}"
    )


def build_user_prompt(task_prompt: str) -> str:
    """Normaliza a entrada de tarefa do usuario para o loop agentico."""

    return (task_prompt or "").strip()
