"""Ponto de entrada do frontend minimo do Mark Core v2."""

from __future__ import annotations

from src.frontend.app import FrontendApp


def main() -> None:
    app = FrontendApp()
    app.run()


if __name__ == "__main__":
    main()
