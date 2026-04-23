"""Camada central de estado seguro de credenciais do backend."""

from __future__ import annotations

import os
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

    def list_google_credential_ids(self) -> list[str]:
        self.refresh_status()
        ids = self.key_manager.list_credential_ids()
        if os.getenv("GOOGLE_API_KEY"):
            ids.append("env:GOOGLE_API_KEY")
        return sorted(set(ids))

    def list_vertex_credential_ids(self) -> list[str]:
        self.refresh_status()
        ids = self.vertex_manager.list_credential_ids()
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and os.getenv("VERTEXAI_PROJECT") and os.getenv("VERTEXAI_LOCATION"):
            ids.append("env:VERTEXAI")
        return sorted(set(ids))

    def get_google_api_key_for_credential(self, credential_id: str) -> str | None:
        self.refresh_status()
        return self.key_manager.get_api_key(credential_id)

    def get_vertex_credential(self, credential_id: str) -> dict[str, str] | None:
        self.refresh_status()
        credential = self.vertex_manager.get_credential(credential_id)
        if credential is None:
            return None
        return {
            "credential_id": credential.credential_id,
            "service_account_path": credential.service_account_path,
            "project": credential.project,
            "location": credential.location,
        }

    def get_google_api_key(self) -> str | None:
        self.refresh_status()
        return self.key_manager.get_active_api_key()

    def get_vertex_active_credential(self) -> dict[str, str] | None:
        self.refresh_status()
        active = self.vertex_manager.get_active()
        if active is None:
            return None
        return {
            "credential_id": active.credential_id,
            "service_account_path": active.service_account_path,
            "project": active.project,
            "location": active.location,
        }
