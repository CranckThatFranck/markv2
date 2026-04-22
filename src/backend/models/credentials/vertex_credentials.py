"""Gerenciador de metadados de credenciais do provider vertex_ai."""

from __future__ import annotations

import json
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
        if credential_id not in self._credentials:
            raise ValueError("CREDENTIAL_NOT_FOUND")
        for key in self._credentials:
            self._credentials[key].active = key == credential_id
        self._save()

    def get_active(self) -> VertexCredential | None:
        for cred in self._credentials.values():
            if cred.active:
                return cred
        return None

    def get_safe_status(self) -> dict[str, object]:
        active = self.get_active()
        return {
            "configured": bool(self._credentials),
            "active_credential_id": active.credential_id if active else None,
            "credential_count": len(self._credentials),
        }

    @property
    def file_path(self) -> str:
        return str(self._file)
