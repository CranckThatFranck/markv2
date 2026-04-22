"""Cliente Google AI API para o Mark Core v2."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class GoogleAIResult:
    ok: bool
    text: str | None = None
    error_code: str | None = None
    message: str | None = None


class GoogleAIClient:
    """Encapsula leitura de credencial e chamada basica ao provider google_ai."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

    def validate_credentials(self) -> None:
        if not self.api_key:
            raise ValueError("CREDENTIAL_NOT_CONFIGURED")

    def generate_text(self, prompt: str, model_id: str = "gemini/gemini-2.5-flash") -> GoogleAIResult:
        """Chamada basica normalizada.

        Nesta fase inicial, a integracao real com SDK sera plugada depois do bootstrap completo.
        """

        try:
            self.validate_credentials()
        except ValueError:
            return GoogleAIResult(
                ok=False,
                error_code="AUTHENTICATION_FAILED",
                message="GOOGLE_API_KEY ausente ou invalida.",
            )

        text = f"[google_ai:{model_id}] resposta simulada para: {prompt.strip()}"
        return GoogleAIResult(ok=True, text=text)

    def map_provider_error(self, raw_error: str) -> GoogleAIResult:
        lowered = raw_error.lower()
        if "rate" in lowered or "429" in lowered:
            return GoogleAIResult(ok=False, error_code="RATE_LIMIT", message="Rate limit do Google AI API.")
        if "quota" in lowered:
            return GoogleAIResult(ok=False, error_code="QUOTA_EXCEEDED", message="Quota excedida no Google AI API.")
        if "auth" in lowered or "key" in lowered or "401" in lowered:
            return GoogleAIResult(
                ok=False,
                error_code="AUTHENTICATION_FAILED",
                message="Falha de autenticacao no Google AI API.",
            )
        return GoogleAIResult(ok=False, error_code="PROVIDER_ERROR", message=raw_error)
