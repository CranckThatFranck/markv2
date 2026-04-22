"""Persistencia de estado de provider e metadados seguros de credenciais."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.backend.runtime.paths import build_runtime_layout


class ProviderStore:
    """Mantem provider ativo e status seguro de credenciais por provider."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._layout = build_runtime_layout(base_dir)
        self._base_dir = self._layout.runtime_dir
        self._file = self._layout.providers_file
        self._data = self._load()

    def _default(self) -> dict[str, Any]:
        return {
            "active_provider": "google_ai",
            "providers": {
                "google_ai": {
                    "active_credential_id": None,
                    "credential_count": 0,
                    "configured": False,
                },
                "vertex_ai": {
                    "active_credential_id": None,
                    "credential_count": 0,
                    "configured": False,
                },
            },
        }

    def _load(self) -> dict[str, Any]:
        if not self._file.exists():
            return self._default()
        with self._file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self) -> None:
        with self._file.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get_active_provider(self) -> str:
        return self._data["active_provider"]

    def set_active_provider(self, provider: str) -> None:
        if provider not in {"google_ai", "vertex_ai"}:
            raise ValueError("PROVIDER_NOT_FOUND")
        self._data["active_provider"] = provider
        self._save()

    def update_provider_status(
        self,
        provider: str,
        active_credential_id: str | None,
        credential_count: int,
        configured: bool,
    ) -> None:
        if provider not in self._data["providers"]:
            raise ValueError("PROVIDER_NOT_FOUND")

        self._data["providers"][provider] = {
            "active_credential_id": active_credential_id,
            "credential_count": credential_count,
            "configured": configured,
        }
        self._save()

    def get_credentials_status(self) -> dict[str, dict[str, Any]]:
        return self._data["providers"]

    def to_sync_providers_payload(self) -> dict[str, Any]:
        return {
            "available": ["google_ai", "vertex_ai"],
            "active": self.get_active_provider(),
        }

    @property
    def file_path(self) -> str:
        return str(self._file)
