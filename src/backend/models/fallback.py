"""Politicas de fallback de modelos e credenciais do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FallbackLevel = Literal["model", "credential", "provider"]


@dataclass(slots=True)
class FallbackDecision:
    level: FallbackLevel
    from_value: str
    to_value: str
    reason: str


class FallbackPolicy:
    """Decide fallback entre modelo, credencial e provider de forma explicita."""

    def __init__(self, allow_cross_provider_fallback: bool = False) -> None:
        self.allow_cross_provider_fallback = allow_cross_provider_fallback

    @property
    def credential_failure_codes(self) -> set[str]:
        return {"AUTHENTICATION_FAILED", "RATE_LIMIT", "QUOTA_EXCEEDED", "CREDENTIAL_NOT_CONFIGURED"}

    @property
    def model_failure_codes(self) -> set[str]:
        return {"MODEL_NOT_FOUND", "MODEL_UNAVAILABLE"}

    def is_credential_failure(self, error_code: str | None) -> bool:
        return bool(error_code and error_code in self.credential_failure_codes)

    def is_model_failure(self, error_code: str | None) -> bool:
        return bool(error_code and error_code in self.model_failure_codes)

    def fallback_model(self, current_model: str, candidates: list[str], reason: str) -> FallbackDecision:
        if not candidates:
            raise ValueError("FALLBACK_MODEL_NOT_AVAILABLE")
        return FallbackDecision(
            level="model",
            from_value=current_model,
            to_value=candidates[0],
            reason=reason,
        )

    def fallback_credential(
        self,
        current_credential_id: str,
        candidates: list[str],
        reason: str,
    ) -> FallbackDecision:
        if not candidates:
            raise ValueError("FALLBACK_CREDENTIAL_NOT_AVAILABLE")
        return FallbackDecision(
            level="credential",
            from_value=current_credential_id,
            to_value=candidates[0],
            reason=reason,
        )

    def fallback_provider(
        self,
        current_provider: str,
        candidates: list[str],
        reason: str,
    ) -> FallbackDecision:
        if not self.allow_cross_provider_fallback:
            raise ValueError("FALLBACK_PROVIDER_DISABLED")
        if not candidates:
            raise ValueError("FALLBACK_PROVIDER_NOT_AVAILABLE")
        return FallbackDecision(
            level="provider",
            from_value=current_provider,
            to_value=candidates[0],
            reason=reason,
        )
