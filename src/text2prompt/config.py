"""Configuration management for text2prompt."""

import json
import os
from dataclasses import dataclass

DEFAULT_DB_PATH = os.path.expanduser("~/.text2prompt/memory.db")
DEFAULT_PREFS_PATH = os.path.expanduser("~/.text2prompt/preferences.json")


@dataclass
class Config:
    """Application configuration."""

    db_path: str = DEFAULT_DB_PATH
    prefs_path: str = DEFAULT_PREFS_PATH
    max_history: int = 100
    streaming_enabled: bool = True
    default_mode: str = "general"
    auto_copy: bool = False
    include_context: bool = True
    save_history: bool = True
    launch_at_login: bool = False

    def ensure_db_dir(self) -> None:
        """Ensure the parent directory for the database exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)


def get_config(
    db_path: str | None = None,
    prefs_path: str | None = None,
    max_history: int | None = None,
    streaming_enabled: bool | None = None,
    default_mode: str | None = None,
    auto_copy: bool | None = None,
    include_context: bool | None = None,
    save_history: bool | None = None,
    launch_at_login: bool | None = None,
) -> Config:
    """Get application configuration with optional overrides."""
    config = Config()

    # Apply overrides
    if db_path is not None:
        config.db_path = db_path
    if prefs_path is not None:
        config.prefs_path = prefs_path
    if max_history is not None:
        config.max_history = max_history
    if streaming_enabled is not None:
        config.streaming_enabled = streaming_enabled
    if default_mode is not None:
        config.default_mode = default_mode
    if auto_copy is not None:
        config.auto_copy = auto_copy
    if include_context is not None:
        config.include_context = include_context
    if save_history is not None:
        config.save_history = save_history
    if launch_at_login is not None:
        config.launch_at_login = launch_at_login

    # Ensure directories exist
    config.ensure_db_dir()

    # Try to load saved preferences
    _load_saved_config(config)
    return config


def _load_saved_config(config: Config) -> None:
    """Load saved preferences from file."""
    if not os.path.exists(config.prefs_path):
        return
    try:
        with open(config.prefs_path) as f:
            saved = json.load(f)
        for key, value in saved.items():
            if hasattr(config, key):
                setattr(config, key, value)
    except Exception:
        pass


def save_config(config: Config) -> None:
    """Save configuration to file."""
    os.makedirs(os.path.dirname(config.prefs_path), exist_ok=True)
    with open(config.prefs_path, "w") as f:
        json.dump(
            {
                "default_mode": config.default_mode,
                "auto_copy": config.auto_copy,
                "include_context": config.include_context,
                "save_history": config.save_history,
                "launch_at_login": config.launch_at_login,
            },
            f,
            indent=2,
        )
