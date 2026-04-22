"""Camada central de resolucao de diretórios de runtime do Mark Core v2."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_RUNTIME_DIR = Path("/var/lib/jarvis-mark/estado")
FALLBACK_RUNTIME_DIR = Path.cwd() / ".mark-runtime" / "estado"


def _ensure_writable(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    probe_file = directory / ".write_probe"
    probe_file.write_text("", encoding="utf-8")
    probe_file.unlink(missing_ok=True)
    return directory


def resolve_runtime_dir(base_dir: str | Path | None = None) -> Path:
    """Resolve o diretório de runtime com fallback local se necessario."""

    candidate = Path(base_dir).expanduser() if base_dir is not None else Path(
        os.getenv("MARK_STATE_DIR", str(DEFAULT_RUNTIME_DIR))
    ).expanduser()

    try:
        return _ensure_writable(candidate)
    except OSError:
        return _ensure_writable(FALLBACK_RUNTIME_DIR)


@dataclass(frozen=True, slots=True)
class RuntimeLayout:
    """Arquivos persistentes da camada de runtime do backend."""

    runtime_dir: Path
    config_file: Path
    session_file: Path
    tasks_db_file: Path
    providers_file: Path
    custom_models_file: Path
    google_ai_keys_file: Path
    vertex_credentials_file: Path


def build_runtime_layout(base_dir: str | Path | None = None) -> RuntimeLayout:
    runtime_dir = resolve_runtime_dir(base_dir)
    return RuntimeLayout(
        runtime_dir=runtime_dir,
        config_file=runtime_dir / "config.json",
        session_file=runtime_dir / "session.json",
        tasks_db_file=runtime_dir / "tasks.db",
        providers_file=runtime_dir / "providers.json",
        custom_models_file=runtime_dir / "custom_models.json",
        google_ai_keys_file=runtime_dir / "google_ai_keys.json",
        vertex_credentials_file=runtime_dir / "vertex_credentials.json",
    )