"""Rotas HTTP de healthcheck do Mark Core v2."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    """Retorna status basico para verificacao de vida do backend."""
    return {"status": "ok", "service": "mark-core-v2"}
