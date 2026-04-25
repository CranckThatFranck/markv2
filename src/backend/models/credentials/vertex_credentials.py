"""Gerenciador de metadados de credenciais do provider vertex_ai."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

from src.backend.runtime.paths import build_runtime_layout


@dataclass(slots=True)
class VertexCredential:
    credential_id: str
    provider: str = "vertex_ai"
    service_account_path: str = ""
    project: str = ""
    location: str = ""
    active: bool = False


class VertexCredentialsManager:
    """Mantem cadastro e selecao de credencial ativa para vertex_ai."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._layout = build_runtime_layout(base_dir)
        self._base_dir = self._layout.runtime_dir
        self._file = self._layout.vertex_credentials_file
        self._credentials = self._load()

    def _load(self) -> dict[str, VertexCredential]:
        if not self._file.exists():
            return {}
        with self._file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return {k: VertexCredential(**v) for k, v in raw.items()}

    def reload(self) -> None:
        self._credentials = self._load()

    def _save(self) -> None:
        with self._file.open("w", encoding="utf-8") as f:
            json.dump({k: asdict(v) for k, v in self._credentials.items()}, f, ensure_ascii=False, indent=2)

    def upsert_credential(
        self,
        credential_id: str,
        service_account_path: str,
        project: str,
        location: str,
    ) -> None:
        if not credential_id.strip():
            raise ValueError("CREDENTIAL_ID_REQUIRED")
        self._credentials[credential_id] = VertexCredential(
            credential_id=credential_id,
            service_account_path=service_account_path,
            project=project,
            location=location,
            active=self._credentials.get(credential_id, VertexCredential(credential_id)).active,
        )
        self._save()

    def set_active(self, credential_id: str) -> None:
        if credential_id == "env:VERTEXAI":
            if not (
                os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                and os.getenv("VERTEXAI_PROJECT")
                and os.getenv("VERTEXAI_LOCATION")
            ):
                raise ValueError("CREDENTIAL_NOT_FOUND")
            for key in self._credentials:
                self._credentials[key].active = False
            self._save()
            return
        if credential_id not in self._credentials:
            raise ValueError("CREDENTIAL_NOT_FOUND")
        for key in self._credentials:
            self._credentials[key].active = key == credential_id
        self._save()

    def list_credential_ids(self) -> list[str]:
        return sorted(self._credentials.keys())

    def get_active_credential_id(self) -> str | None:
        active = self.get_active()
        return active.credential_id if active else None

    def get_credential(self, credential_id: str) -> VertexCredential | None:
        if credential_id == "env:VERTEXAI":
            env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            env_project = os.getenv("VERTEXAI_PROJECT")
            env_location = os.getenv("VERTEXAI_LOCATION")
            if env_path and env_project and env_location:
                return VertexCredential(
                    credential_id="env:VERTEXAI",
                    service_account_path=env_path,
                    project=env_project,
                    location=env_location,
                    active=True,
                )
            return None
        return self._credentials.get(credential_id)

    def get_active(self) -> VertexCredential | None:
        for cred in self._credentials.values():
            if cred.active:
                return cred
        env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        env_project = os.getenv("VERTEXAI_PROJECT")
        env_location = os.getenv("VERTEXAI_LOCATION")
        if env_path and env_project and env_location:
            return VertexCredential(
                credential_id="env:VERTEXAI",
                service_account_path=env_path,
                project=env_project,
                location=env_location,
                active=True,
            )
        return None

    def get_safe_status(self) -> dict[str, object]:
        active = self.get_active()
        env_configured = bool(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            and os.getenv("VERTEXAI_PROJECT")
            and os.getenv("VERTEXAI_LOCATION")
        )
        return {
            "configured": bool(self._credentials) or env_configured,
            "active_credential_id": active.credential_id if active else None,
            "credential_count": len(self._credentials) + (1 if env_configured else 0),
        }

    def list_safe_credentials(self) -> list[dict[str, object]]:
        active = self.get_active()
        active_id = active.credential_id if active else None
        credentials = [
            {
                "credential_id": credential.credential_id,
                "label": credential.credential_id,
                "source_type": "stored",
                "is_active": credential.credential_id == active_id,
            }
            for credential in self._credentials.values()
        ]
        if (
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            and os.getenv("VERTEXAI_PROJECT")
            and os.getenv("VERTEXAI_LOCATION")
        ):
            credentials.append(
                {
                    "credential_id": "env:VERTEXAI",
                    "label": "Vertex AI environment",
                    "source_type": "env",
                    "is_active": active_id == "env:VERTEXAI",
                }
            )
        return sorted(credentials, key=lambda item: (not bool(item["is_active"]), str(item["credential_id"])))

    @property
    def file_path(self) -> str:
        return str(self._file)
