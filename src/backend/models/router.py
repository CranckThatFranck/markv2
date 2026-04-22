"""Roteador de modelos/providers do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass

from src.backend.models.registry import ModelRegistry


@dataclass(slots=True)
class ModelTarget:
    """Representa resolucao de modelo para provider."""

    model_id: str
    provider: str


class ModelRouter:
    """Resolve provider a partir do model id e configuracao ativa."""

    def __init__(self, registry: ModelRegistry, default_provider: str = "google_ai") -> None:
        self.registry = registry
        self.default_provider = default_provider

    def register_model(self, model_id: str, provider: str) -> None:
        if not model_id.strip():
            raise ValueError("MODEL_ID_REQUIRED")
        if provider not in {"google_ai", "vertex_ai"}:
            raise ValueError("PROVIDER_NOT_SUPPORTED")
        if self.registry.is_valid_model(model_id):
            return
        self.registry.add_custom_model(model_id=model_id, provider=provider)

    def resolve_provider(self, model_id: str | None, configured_provider: str | None = None) -> str:
        if model_id and self.registry.is_valid_model(model_id):
            return self.registry.resolve_provider(model_id)
        if configured_provider:
            return configured_provider
        return self.default_provider

    def resolve_target(self, model_id: str, configured_provider: str | None = None) -> ModelTarget:
        provider = self.resolve_provider(model_id, configured_provider)
        return ModelTarget(model_id=model_id, provider=provider)

    def is_known_model(self, model_id: str) -> bool:
        return self.registry.is_valid_model(model_id)

    def list_models_by_provider(self, provider: str) -> list[str]:
        return self.registry.list_models_by_provider(provider)
