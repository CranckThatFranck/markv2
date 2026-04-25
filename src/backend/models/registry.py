"""Registry de modelos do Mark Core v2."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from src.backend.runtime.paths import build_runtime_layout


@dataclass(slots=True)
class ModelEntry:
    model_id: str
    provider: str
    enabled: bool = True
    builtin: bool = True
    supports_tools: bool = True
    supports_plan: bool = True
    supports_agent: bool = True
    priority: int = 100


class ModelRegistry:
    """Mantem catalogo de modelos builtin e customizados."""

    DEFAULT_MODEL_ID = "gemini/gemini-3.1-pro-preview-customtools"

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._layout = build_runtime_layout(base_dir)
        self._base_dir = self._layout.runtime_dir
        self._custom_models_file = self._layout.custom_models_file
        self._builtin: dict[str, ModelEntry] = self._build_builtin_catalog()
        self._custom: dict[str, ModelEntry] = self._load_custom_models()

    def _build_builtin_catalog(self) -> dict[str, ModelEntry]:
        entries = [
            ModelEntry(
                model_id="gemini/gemini-3.1-pro-preview-customtools",
                provider="google_ai",
                priority=1,
            ),
            ModelEntry(model_id="gemini/gemini-3.1-pro-preview", provider="google_ai", priority=2),
            ModelEntry(model_id="gemini/gemini-3-flash-preview", provider="google_ai", priority=3),
            ModelEntry(model_id="gemini/gemini-3.1-flash-lite-preview", provider="google_ai", priority=4),
            ModelEntry(model_id="gemini/gemini-2.5-pro", provider="google_ai", priority=5),
            ModelEntry(
                model_id="vertex_ai/meta/llama-4-maverick-17b-128e-instruct-maas",
                provider="vertex_ai",
                priority=1,
            ),
            ModelEntry(
                model_id="vertex_ai/meta/llama-4-scout-17b-16e-instruct-maas",
                provider="vertex_ai",
                priority=2,
            ),
            ModelEntry(model_id="vertex_ai/google/gemini-3.1-pro-preview", provider="vertex_ai", priority=3),
            ModelEntry(
                model_id="vertex_ai/google/gemini-3.1-pro-preview-customtools",
                provider="vertex_ai",
                priority=4,
            ),
            ModelEntry(model_id="vertex_ai/google/gemini-3-pro-preview", provider="vertex_ai", priority=5),
        ]
        return {entry.model_id: entry for entry in entries}

    @staticmethod
    def _sort_entries(entries: list[ModelEntry]) -> list[ModelEntry]:
        return sorted(entries, key=lambda entry: (entry.priority, entry.model_id))

    def _load_custom_models(self) -> dict[str, ModelEntry]:
        if not self._custom_models_file.exists():
            return {}

        with self._custom_models_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        loaded: dict[str, ModelEntry] = {}
        for model_id, payload in raw.items():
            loaded[model_id] = ModelEntry(**payload)
        return loaded

    def _persist_custom_models(self) -> None:
        serialized = {model_id: asdict(entry) for model_id, entry in self._custom.items()}
        with self._custom_models_file.open("w", encoding="utf-8") as f:
            json.dump(serialized, f, ensure_ascii=False, indent=2)

    def list_builtin(self) -> list[str]:
        return [entry.model_id for entry in self._builtin.values()]

    def list_custom(self) -> list[str]:
        return sorted(self._custom.keys())

    def list_all(self) -> list[str]:
        return [*self.list_builtin(), *self.list_custom()]

    def list_models_by_provider(self, provider: str) -> list[str]:
        models = [entry for entry in {**self._builtin, **self._custom}.values() if entry.provider == provider]
        return [entry.model_id for entry in self._sort_entries(models)]

    def fallback_models_for_provider(self, provider: str, current_model_id: str) -> list[str]:
        candidates = [
            entry
            for entry in {**self._builtin, **self._custom}.values()
            if entry.provider == provider and entry.enabled and entry.model_id != current_model_id
        ]
        candidates.sort(key=lambda entry: (entry.priority, entry.model_id))
        return [entry.model_id for entry in candidates]

    def default_model_for_provider(self, provider: str) -> str | None:
        candidates = [entry for entry in {**self._builtin, **self._custom}.values() if entry.provider == provider and entry.enabled]
        if not candidates:
            return None
        candidates.sort(key=lambda entry: (entry.priority, entry.model_id))
        return candidates[0].model_id

    def resolve_provider(self, model_id: str) -> str:
        entry = self.get_entry(model_id)
        if entry is None:
            raise ValueError("MODEL_NOT_FOUND")
        return entry.provider

    def get_entry(self, model_id: str) -> ModelEntry | None:
        if model_id in self._builtin:
            return self._builtin[model_id]
        return self._custom.get(model_id)

    def is_valid_model(self, model_id: str) -> bool:
        return model_id in self._builtin or model_id in self._custom

    def add_custom_model(self, model_id: str, provider: str, priority: int = 100) -> None:
        if not model_id.strip():
            raise ValueError("MODEL_ID_REQUIRED")
        if provider not in {"google_ai", "vertex_ai"}:
            raise ValueError("PROVIDER_NOT_SUPPORTED")
        if model_id in self._builtin:
            raise ValueError("MODEL_ALREADY_BUILTIN")

        self._custom[model_id] = ModelEntry(
            model_id=model_id,
            provider=provider,
            builtin=False,
            priority=priority,
        )
        self._persist_custom_models()

    def remove_custom_model(self, model_id: str) -> None:
        if model_id not in self._custom:
            raise ValueError("MODEL_NOT_FOUND")
        del self._custom[model_id]
        self._persist_custom_models()

    @property
    def custom_models_file(self) -> str:
        return str(self._custom_models_file)
