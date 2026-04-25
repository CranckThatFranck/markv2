"""Cliente Google AI API para o Mark Core v2."""

from __future__ import annotations

import os
from dataclasses import dataclass

from google.api_core import exceptions as gax_exceptions
import google.generativeai as genai


@dataclass(slots=True)
class GoogleAIResult:
    ok: bool
    provider: str = "google_ai"
    model_id: str | None = None
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

    def generate_text(self, prompt: str, model_id: str = "gemini/gemini-3.1-pro-preview-customtools") -> GoogleAIResult:
        """Executa chamada real no Google AI API e normaliza a resposta."""

        try:
            self.validate_credentials()
        except ValueError:
            return GoogleAIResult(
                ok=False,
                model_id=model_id,
                error_code="AUTHENTICATION_FAILED",
                message="GOOGLE_API_KEY ausente ou invalida.",
            )

        try:
            genai.configure(api_key=self.api_key)
            upstream_model = model_id.split("/", 1)[-1]
            model = genai.GenerativeModel(model_name=upstream_model)
            response = model.generate_content(prompt)

            text = getattr(response, "text", None)
            if not text and getattr(response, "candidates", None):
                parts = response.candidates[0].content.parts if response.candidates[0].content else []
                text = "".join(getattr(part, "text", "") for part in parts).strip()
            if not text:
                text = "Resposta vazia do provider Google AI API."

            return GoogleAIResult(ok=True, model_id=model_id, text=text)
        except Exception as exc:  # pragma: no cover - depende de erro externo do provider
            mapped = self.map_provider_error(exc)
            mapped.model_id = model_id
            return mapped

    def map_provider_error(self, raw_error: Exception) -> GoogleAIResult:
        lowered = str(raw_error).lower()

        if isinstance(raw_error, (gax_exceptions.Unauthenticated, gax_exceptions.PermissionDenied)):
            return GoogleAIResult(
                ok=False,
                error_code="AUTHENTICATION_FAILED",
                message="Falha de autenticacao no Google AI API.",
            )
        if isinstance(raw_error, gax_exceptions.ResourceExhausted):
            if "quota" in lowered:
                return GoogleAIResult(
                    ok=False,
                    error_code="QUOTA_EXCEEDED",
                    message="Quota excedida no Google AI API.",
                )
            return GoogleAIResult(ok=False, error_code="RATE_LIMIT", message="Rate limit do Google AI API.")
        if isinstance(raw_error, gax_exceptions.NotFound):
            return GoogleAIResult(
                ok=False,
                error_code="MODEL_NOT_FOUND",
                message="Modelo indisponivel no Google AI API.",
            )
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
        if "model" in lowered and "not" in lowered:
            return GoogleAIResult(
                ok=False,
                error_code="MODEL_NOT_FOUND",
                message="Modelo indisponivel no Google AI API.",
            )
        return GoogleAIResult(ok=False, error_code="PROVIDER_ERROR", message=str(raw_error))
