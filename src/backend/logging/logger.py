"""Logger base do Mark Core v2."""

from __future__ import annotations

import logging
import os
from pathlib import Path


DEFAULT_LOG_DIR = "/var/log/jarvis"


def resolve_log_dir(log_dir: str | None = None) -> Path:
    """Resolve o diretório oficial de logs com suporte a override por ambiente."""

    directory = Path(log_dir or os.getenv("MARK_LOG_DIR", DEFAULT_LOG_DIR))
    directory.mkdir(parents=True, exist_ok=True)
    return directory


class BackendLogger:
    """Configura logs basicos em /var/log/jarvis."""

    def __init__(self, log_dir: str | None = None) -> None:
        self.log_dir = resolve_log_dir(log_dir)
        self.backend_log = self.log_dir / "backend.log"
        self.events_log = self.log_dir / "events.log"
        self.errors_log = self.log_dir / "errors.log"
        self._logger = logging.getLogger("mark_core_v2")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        if not self._logger.handlers:
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

            backend_handler = logging.FileHandler(self.backend_log, encoding="utf-8")
            backend_handler.setLevel(logging.INFO)
            backend_handler.setFormatter(formatter)

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            stream_handler.setFormatter(formatter)

            self._logger.addHandler(backend_handler)
            self._logger.addHandler(stream_handler)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def error(self, message: str) -> None:
        self._logger.error(message)
