"""Cliente Vertex AI para o Mark Core v2."""

from __future__ import annotations

import os
from dataclasses import dataclass

from google.api_core import exceptions as gax_exceptions
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel


@dataclass(slots=True)
class VertexAIResult:
    ok: bool
    provider: str = "vertex_ai"
    model_id: str | None = None
    text: str | None = None
    error_code: str | None = None
    message: str | None = None


class VertexAIClient:
    """Encapsula leitura de credenciais e chamada basica ao provider vertex_ai."""

    def __init__(
        self,
        credentials_path: str | None = None,
        project: str | None = None,
        location: str | None = None,
    ) -> None:
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.project = project or os.getenv("VERTEXAI_PROJECT")
        self.location = location or os.getenv("VERTEXAI_LOCATION")

    def validate_credentials(self) -> None:
        if not self.credentials_path:
            raise ValueError("CREDENTIAL_NOT_CONFIGURED")
        if not self.project:
            raise ValueError("PROJECT_NOT_CONFIGURED")
        if not self.location:
            raise ValueError("REGION_NOT_CONFIGURED")

    def generate_text(self, prompt: str, model_id: str = "vertex_ai/gemini-2.5-flash") -> VertexAIResult:
        """Executa chamada real no Vertex AI e normaliza a resposta."""

        try:
            self.validate_credentials()
        except ValueError as exc:
            code_map = {
                "CREDENTIAL_NOT_CONFIGURED": ("AUTHENTICATION_FAILED", "Credenciais Vertex AI ausentes."),
                "PROJECT_NOT_CONFIGURED": ("PROJECT_INVALID", "Projeto Vertex AI ausente ou invalido."),
                "REGION_NOT_CONFIGURED": ("REGION_INVALID", "Regiao Vertex AI ausente ou invalida."),
            }
            error_code, message = code_map.get(str(exc), ("PROVIDER_ERROR", str(exc)))
            return VertexAIResult(ok=False, model_id=model_id, error_code=error_code, message=message)

        try:
            credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
            vertexai.init(project=self.project, location=self.location, credentials=credentials)
            upstream_model = model_id.split("/", 1)[-1]
            model = GenerativeModel(upstream_model)
            response = model.generate_content(prompt)

            text = getattr(response, "text", None)
            if not text and getattr(response, "candidates", None):
                parts = response.candidates[0].content.parts if response.candidates[0].content else []
                text = "".join(getattr(part, "text", "") for part in parts).strip()
            if not text:
                text = "Resposta vazia do provider Vertex AI."

            return VertexAIResult(ok=True, model_id=model_id, text=text)
        except Exception as exc:  # pragma: no cover - depende de erro externo do provider
            mapped = self.map_provider_error(exc)
            mapped.model_id = model_id
            return mapped

    def map_provider_error(self, raw_error: Exception) -> VertexAIResult:
        lowered = str(raw_error).lower()

        if isinstance(raw_error, (DefaultCredentialsError, FileNotFoundError, PermissionError)):
            return VertexAIResult(ok=False, error_code="AUTHENTICATION_FAILED", message="Falha de autenticacao Vertex AI.")
        if isinstance(raw_error, (gax_exceptions.Unauthenticated, gax_exceptions.PermissionDenied)):
            return VertexAIResult(ok=False, error_code="AUTHENTICATION_FAILED", message="Falha de autenticacao Vertex AI.")
        if isinstance(raw_error, gax_exceptions.ResourceExhausted):
            if "quota" in lowered:
                return VertexAIResult(ok=False, error_code="QUOTA_EXCEEDED", message="Quota excedida no Vertex AI.")
            return VertexAIResult(ok=False, error_code="RATE_LIMIT", message="Rate limit no Vertex AI.")
        if isinstance(raw_error, gax_exceptions.NotFound):
            if "model" in lowered:
                return VertexAIResult(ok=False, error_code="MODEL_NOT_FOUND", message="Modelo indisponivel no Vertex AI.")
            if "location" in lowered or "region" in lowered:
                return VertexAIResult(ok=False, error_code="REGION_INVALID", message="Regiao Vertex AI invalida.")
            if "project" in lowered:
                return VertexAIResult(ok=False, error_code="PROJECT_INVALID", message="Projeto Vertex AI invalido.")
            return VertexAIResult(ok=False, error_code="MODEL_NOT_FOUND", message="Modelo indisponivel no Vertex AI.")
        if isinstance(raw_error, gax_exceptions.InvalidArgument):
            if "location" in lowered or "region" in lowered:
                return VertexAIResult(ok=False, error_code="REGION_INVALID", message="Regiao Vertex AI invalida.")
            if "project" in lowered:
                return VertexAIResult(ok=False, error_code="PROJECT_INVALID", message="Projeto Vertex AI invalido.")
            if "model" in lowered:
                return VertexAIResult(ok=False, error_code="MODEL_NOT_FOUND", message="Modelo indisponivel no Vertex AI.")

        if "project" in lowered:
            return VertexAIResult(ok=False, error_code="PROJECT_INVALID", message="Projeto Vertex AI invalido.")
        if "region" in lowered or "location" in lowered:
            return VertexAIResult(ok=False, error_code="REGION_INVALID", message="Regiao Vertex AI invalida.")
        if "quota" in lowered:
            return VertexAIResult(ok=False, error_code="QUOTA_EXCEEDED", message="Quota excedida no Vertex AI.")
        if "rate" in lowered or "429" in lowered:
            return VertexAIResult(ok=False, error_code="RATE_LIMIT", message="Rate limit no Vertex AI.")
        if "model" in lowered and "not" in lowered:
            return VertexAIResult(ok=False, error_code="MODEL_NOT_FOUND", message="Modelo indisponivel no Vertex AI.")
        return VertexAIResult(ok=False, error_code="PROVIDER_ERROR", message=str(raw_error))
