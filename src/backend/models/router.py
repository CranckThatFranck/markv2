"""Roteador de modelos/providers do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ModelTarget:
    """Representa resolucao de modelo para provider."""

    model_id: str
    provider: str


class ModelRouter:
    """Resolve provider a partir do model id e configuracao ativa."""

    def __init__(self, default_provider: str = "google_ai") -> None:
        self.default_provider = default_provider
        self._model_provider_map: dict[str, str] = {
            "gemini/gemini-2.5-flash": "google_ai",
            "gemini/gemini-2.5-pro": "google_ai",
            "vertex_ai/gemini-2.5-flash": "vertex_ai",
            "vertex_ai/gemini-2.5-pro": "vertex_ai",
        }

    def register_model(self, model_id: str, provider: str) -> None:
        if not model_id.strip():
            raise ValueError("MODEL_ID_REQUIRED")
        if provider not in {"google_ai", "vertex_ai"}:
            raise ValueError("PROVIDER_NOT_SUPPORTED")
        self._model_provider_map[model_id] = provider

    def resolve_provider(self, model_id: str | None, configured_provider: str | None = None) -> str:
        if model_id and model_id in self._model_provider_map:
            return self._model_provider_map[model_id]
        if configured_provider:
            return configured_provider
        return self.default_provider

    def resolve_target(self, model_id: str, configured_provider: str | None = None) -> ModelTarget:
        provider = self.resolve_provider(model_id, configured_provider)
        return ModelTarget(model_id=model_id, provider=provider)

    def is_known_model(self, model_id: str) -> bool:
        return model_id in self._model_provider_map

    def list_models_by_provider(self, provider: str) -> list[str]:
        return sorted([m for m, p in self._model_provider_map.items() if p == provider])
