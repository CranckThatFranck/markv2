"""Cliente Vertex AI para o Mark Core v2."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class VertexAIResult:
    ok: bool
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
        """Chamada basica normalizada para fase inicial do backend."""

        try:
            self.validate_credentials()
        except ValueError as exc:
            code_map = {
                "CREDENTIAL_NOT_CONFIGURED": ("AUTHENTICATION_FAILED", "Credenciais Vertex AI ausentes."),
                "PROJECT_NOT_CONFIGURED": ("PROJECT_INVALID", "Projeto Vertex AI ausente ou invalido."),
                "REGION_NOT_CONFIGURED": ("REGION_INVALID", "Regiao Vertex AI ausente ou invalida."),
            }
            error_code, message = code_map.get(str(exc), ("PROVIDER_ERROR", str(exc)))
            return VertexAIResult(ok=False, error_code=error_code, message=message)

        text = f"[vertex_ai:{model_id}@{self.location}] resposta simulada para: {prompt.strip()}"
        return VertexAIResult(ok=True, text=text)

    def map_provider_error(self, raw_error: str) -> VertexAIResult:
        lowered = raw_error.lower()
        if "auth" in lowered or "401" in lowered or "permission" in lowered:
            return VertexAIResult(ok=False, error_code="AUTHENTICATION_FAILED", message="Falha de autenticacao Vertex AI.")
        if "project" in lowered:
            return VertexAIResult(ok=False, error_code="PROJECT_INVALID", message="Projeto Vertex AI invalido.")
        if "region" in lowered or "location" in lowered:
            return VertexAIResult(ok=False, error_code="REGION_INVALID", message="Regiao Vertex AI invalida.")
        if "model" in lowered and "not" in lowered:
            return VertexAIResult(ok=False, error_code="MODEL_NOT_FOUND", message="Modelo indisponivel no Vertex AI.")
        return VertexAIResult(ok=False, error_code="PROVIDER_ERROR", message=raw_error)
