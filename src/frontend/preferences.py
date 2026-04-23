"""Persistencia local de preferencias do frontend."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_BACKEND_URL = "ws://127.0.0.1:8000/ws"
PREFERENCES_DIR = Path.home() / ".config" / "mark-core-v2-frontend"
PREFERENCES_FILE = PREFERENCES_DIR / "preferences.json"


@dataclass(slots=True)
class FrontendPreferences:
    backend_url: str = DEFAULT_BACKEND_URL
    window_geometry: str = "1200x780"
    theme: str = "default"


def load_preferences() -> FrontendPreferences:
    if not PREFERENCES_FILE.exists():
        return FrontendPreferences()

    try:
        payload = json.loads(PREFERENCES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return FrontendPreferences()

    return FrontendPreferences(
        backend_url=str(payload.get("backend_url", DEFAULT_BACKEND_URL)),
        window_geometry=str(payload.get("window_geometry", "1200x780")),
        theme=str(payload.get("theme", "default")),
    )


def save_preferences(preferences: FrontendPreferences) -> None:
    PREFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    PREFERENCES_FILE.write_text(
        json.dumps(asdict(preferences), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
