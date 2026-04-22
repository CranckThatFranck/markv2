"""Camada central de carregamento das regras iniciais do produto."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class RulesRuntime:
    rules_file: Path
    rules_text: str


def build_rules_runtime() -> RulesRuntime:
    rules_file = Path(__file__).resolve().parents[1] / "product_config" / "initial_rules.txt"
    rules_text = rules_file.read_text(encoding="utf-8") if rules_file.exists() else ""
    return RulesRuntime(rules_file=rules_file, rules_text=rules_text)