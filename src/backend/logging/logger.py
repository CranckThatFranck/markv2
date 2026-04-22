"""Logger base do Mark Core v2."""

from __future__ import annotations

import logging
from pathlib import Path


class BackendLogger:
    """Configura logs basicos em /var/log/jarvis."""

    def __init__(self, log_dir: str = "/var/log/jarvis") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.backend_log = self.log_dir / "backend.log"
        self.events_log = self.log_dir / "events.log"
        self.errors_log = self.log_dir / "errors.log"
        self._logger = logging.getLogger("mark_core_v2")
        self._logger.setLevel(logging.INFO)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def error(self, message: str) -> None:
        self._logger.error(message)
