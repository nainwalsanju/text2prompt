"""Configuration management for text2prompt."""

import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_DB_PATH = os.path.expanduser("~/.text2prompt/memory.db")
DEFAULT_PREFS_PATH = os.path.expanduser("~/.text2prompt/preferences.json")


@dataclass
class Config:
    """Application configuration."""

    db_path: str = DEFAULT_DB_PATH
    prefs_path: str = DEFAULT_PREFS_PATH
    max_history: int = 100
    streaming_enabled: bool = True

    def ensure_db_dir(self) -> None:
        """Ensure the parent directory for the database exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)


def get_config(
    db_path: str | None = None,
    prefs_path: str | None = None,
    max_history: int | None = None,
    streaming_enabled: bool | None = None,
) -> Config:
    """Get application configuration with optional overrides."""
    return Config(
        db_path=db_path or DEFAULT_DB_PATH,
        prefs_path=prefs_path or DEFAULT_PREFS_PATH,
        max_history=max_history if max_history is not None else 100,
        streaming_enabled=streaming_enabled if streaming_enabled is not None else True,
    )
