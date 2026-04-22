"""Ponto de entrada do Mark Core v2 backend."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.backend.api.health import router as health_router
from src.backend.api.websocket import router as websocket_router
from src.backend.logging.logger import BackendLogger

logger = BackendLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Mark Core v2 startup")
    yield
    logger.info("Mark Core v2 shutdown")


def create_app() -> FastAPI:
    """Cria a instancia principal do backend com rotas basicas."""

    app = FastAPI(title="Mark Core v2", version="2.0.0", lifespan=lifespan)
    app.state.shutdown_requested = False
    app.include_router(health_router)
    app.include_router(websocket_router)
    return app


app = create_app()
