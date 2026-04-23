"""Gerenciador de credenciais do provider google_ai."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

from src.backend.runtime.paths import build_runtime_layout


@dataclass(slots=True)
class GoogleAICredential:
    credential_id: str
    provider: str = "google_ai"
    label: str | None = None
    api_key: str | None = None
    active: bool = False


class KeyManager:
    """Mantem cadastro e selecao da credencial ativa para google_ai."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._layout = build_runtime_layout(base_dir)
        self._base_dir = self._layout.runtime_dir
        self._file = self._layout.google_ai_keys_file
        self._credentials = self._load()

    def _load(self) -> dict[str, GoogleAICredential]:
        if not self._file.exists():
            return {}
        with self._file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return {k: GoogleAICredential(**v) for k, v in raw.items()}

    def reload(self) -> None:
        self._credentials = self._load()

    def _save(self) -> None:
        with self._file.open("w", encoding="utf-8") as f:
            json.dump({k: asdict(v) for k, v in self._credentials.items()}, f, ensure_ascii=False, indent=2)

    def upsert_credential(self, credential_id: str, api_key: str, label: str | None = None) -> None:
        if not credential_id.strip():
            raise ValueError("CREDENTIAL_ID_REQUIRED")
        self._credentials[credential_id] = GoogleAICredential(
            credential_id=credential_id,
            label=label,
            api_key=api_key,
            active=self._credentials.get(credential_id, GoogleAICredential(credential_id)).active,
        )
        self._save()

    def set_active(self, credential_id: str) -> None:
        if credential_id == "env:GOOGLE_API_KEY":
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
        active = next((cred.credential_id for cred in self._credentials.values() if cred.active), None)
        if active:
            return active
        return "env:GOOGLE_API_KEY" if os.getenv("GOOGLE_API_KEY") else None

    def get_api_key(self, credential_id: str) -> str | None:
        if credential_id == "env:GOOGLE_API_KEY":
            return os.getenv("GOOGLE_API_KEY")
        credential = self._credentials.get(credential_id)
        return credential.api_key if credential else None

    def get_active_api_key(self) -> str | None:
        for cred in self._credentials.values():
            if cred.active:
                return cred.api_key
        env_key = os.getenv("GOOGLE_API_KEY")
        return env_key if env_key else None

    def get_safe_status(self) -> dict[str, object]:
        active = next((c.credential_id for c in self._credentials.values() if c.active), None)
        env_key_present = bool(os.getenv("GOOGLE_API_KEY"))
        return {
            "configured": bool(self._credentials) or env_key_present,
            "active_credential_id": active or ("env:GOOGLE_API_KEY" if env_key_present else None),
            "credential_count": len(self._credentials) + (1 if env_key_present else 0),
        }

    @property
    def file_path(self) -> str:
        return str(self._file)
