"""Camada central de estado seguro de credenciais do backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.backend.models.credentials.key_manager import KeyManager
from src.backend.models.credentials.vertex_credentials import VertexCredentialsManager
from src.backend.models.credentials.provider_store import ProviderStore


@dataclass(slots=True)
class CredentialRuntime:
    key_manager: KeyManager
    vertex_manager: VertexCredentialsManager
    provider_store: ProviderStore

    @classmethod
    def create(cls, base_dir: str | Path | None = None) -> "CredentialRuntime":
        key_manager = KeyManager(base_dir=base_dir)
        vertex_manager = VertexCredentialsManager(base_dir=base_dir)
        provider_store = ProviderStore(base_dir=base_dir)
        runtime = cls(key_manager=key_manager, vertex_manager=vertex_manager, provider_store=provider_store)
        runtime.refresh_status()
        return runtime

    def refresh_status(self) -> None:
        self.key_manager.reload()
        self.vertex_manager.reload()
        self.provider_store.update_provider_status(
            "google_ai",
            self.key_manager.get_safe_status()["active_credential_id"],
            self.key_manager.get_safe_status()["credential_count"],
            self.key_manager.get_safe_status()["configured"],
        )
        self.provider_store.update_provider_status(
            "vertex_ai",
            self.vertex_manager.get_safe_status()["active_credential_id"],
            self.vertex_manager.get_safe_status()["credential_count"],
            self.vertex_manager.get_safe_status()["configured"],
        )

    def get_credentials_status(self) -> dict[str, dict[str, object]]:
        self.refresh_status()
        return self.provider_store.get_credentials_status()

    def set_active_credential(self, provider: str, credential_id: str) -> dict[str, object]:
        self.refresh_status()
        if provider == "google_ai":
            self.key_manager.set_active(credential_id)
        elif provider == "vertex_ai":
            self.vertex_manager.set_active(credential_id)
        else:
            raise ValueError("PROVIDER_NOT_FOUND")
        self.refresh_status()
        return self.provider_store.get_credentials_status()[provider]
