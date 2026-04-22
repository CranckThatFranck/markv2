"""Ponto de entrada inicial do Mark Core v2 backend."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Cria a instancia base da aplicacao FastAPI para o backend v2."""
    app = FastAPI(title="Mark Core v2", version="2.0.0")
    return app


app = create_app()
