"""Construtor explícito do contexto de tarefa para o loop agentico."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TaskContextData:
    """Dados construídos explicitamente para executar uma tarefa."""

    task_id: str
    prompt: str
    rules_text: str
    mode: str
    provider: str
    model_id: str
    rules_applied: list[str]


class TaskContextBuilder:
    """Monta o contexto de tarefa de forma explícita e previsível."""

    def build(
        self,
        task_id: str,
        prompt: str,
        rules_text: str,
        mode: str,
        provider: str,
        model_id: str,
    ) -> TaskContextData:
        """Constrói o contexto da tarefa aplicando as regras iniciais.

        Retorna estrutura com:
        - task_id: identificador único
        - prompt: pergunta/instrução do usuário
        - rules_text: conteúdo do initial_rules.txt
        - mode: "plan" ou "agent"
        - provider: nome do provider de modelo
        - model_id: id do modelo
        - rules_applied: lista de regras extraídas e consideradas
        """

        rules_applied = self._extract_rules(rules_text, mode)

        return TaskContextData(
            task_id=task_id,
            prompt=prompt,
            rules_text=rules_text,
            mode=mode,
            provider=provider,
            model_id=model_id,
            rules_applied=rules_applied,
        )

    def _extract_rules(self, rules_text: str, mode: str) -> list[str]:
        """Extrai as regras relevantes do arquivo de regras inicial."""

        if not rules_text:
            return []

        lines = rules_text.strip().split("\n")
        rules = []

        for line in lines:
            line = line.strip()
            if line and line.startswith("-"):
                rule = line.lstrip("- ").strip()
                if rule:
                    # Filtra regras relevantes ao modo
                    if mode == "plan" and "Plan" in rule:
                        rules.append(rule)
                    elif mode == "agent" and "Agent" in rule:
                        rules.append(rule)
                    elif "backend" in rule.lower() or "credencial" in rule.lower() or "provider" in rule.lower():
                        rules.append(rule)

        return rules
