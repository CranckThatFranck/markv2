"""Politica de modelos do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ModelPolicyDecision:
    model_id: str
    allowed: bool
    reason: str | None = None


class ModelPolicy:
    """Valida modelos builtin, customizados e compatibilidade de fallback."""

    def __init__(self, allow_custom_models: bool = True) -> None:
        self.allow_custom_models = allow_custom_models

    def validate(self, model_id: str, known_models: set[str]) -> ModelPolicyDecision:
        if model_id in known_models:
            return ModelPolicyDecision(model_id=model_id, allowed=True)
        if self.allow_custom_models:
            return ModelPolicyDecision(model_id=model_id, allowed=True, reason="CUSTOM_MODEL_ALLOWED")
        return ModelPolicyDecision(model_id=model_id, allowed=False, reason="MODEL_NOT_FOUND")

    def can_add_custom_model(self) -> bool:
        return self.allow_custom_models
