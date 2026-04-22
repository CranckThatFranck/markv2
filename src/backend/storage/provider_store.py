"""Persistencia de provider no storage do Mark Core v2."""

from __future__ import annotations

from src.backend.models.credentials.provider_store import ProviderStore as CredentialProviderStore


class ProviderStore(CredentialProviderStore):
    """Alias de storage para manter separacao de camada e compatibilidade."""

    pass
