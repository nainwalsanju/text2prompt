"""Tests for config module."""

import json
import os
import tempfile

from text2prompt.config import DEFAULT_DB_PATH, Config, get_config, save_config


def test_default_db_path():
    """Default DB path should be in ~/.text2prompt/"""
    assert "text2prompt" in DEFAULT_DB_PATH
    assert DEFAULT_DB_PATH.endswith("memory.db")


def test_config_default_values():
    """Config should have sensible defaults."""
    config = get_config()
    assert config.db_path is not None
    assert config.max_history == 100
    assert config.streaming_enabled is True


def test_config_custom_db_path():
    """Config should allow custom DB path."""
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        config = get_config(db_path=tmp.name)
        assert config.db_path == tmp.name


def test_config_ensure_db_dir():
    """Config should create parent directories for DB path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "subdir", "test.db")
        config = get_config(db_path=db_path)
        config.ensure_db_dir()
        assert os.path.exists(os.path.dirname(db_path))


def test_overrides_win_over_saved_preferences():
    """Explicit overrides should take precedence over saved preferences.

    Bug 3: Previously, _load_saved_config() ran last and clobbered overrides.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_path = os.path.join(tmpdir, "prefs.json")
        db_path = os.path.join(tmpdir, "test.db")

        # Write preferences that disagree with our overrides
        with open(prefs_path, "w") as f:
            json.dump(
                {
                    "default_mode": "image",
                    "auto_copy": True,
                    "include_context": False,
                },
                f,
            )

        # Override with explicit values — these MUST win
        config = get_config(
            db_path=db_path,
            prefs_path=prefs_path,
            default_mode="code",
            auto_copy=False,
            include_context=True,
        )

        assert config.default_mode == "code", "Explicit override should win"
        assert config.auto_copy is False, "Explicit override should win"
        assert config.include_context is True, "Explicit override should win"


def test_saved_preferences_loaded_when_no_override():
    """Saved preferences should apply when no explicit override is given."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_path = os.path.join(tmpdir, "prefs.json")
        db_path = os.path.join(tmpdir, "test.db")

        with open(prefs_path, "w") as f:
            json.dump({"default_mode": "analysis", "auto_copy": True}, f)

        config = get_config(db_path=db_path, prefs_path=prefs_path)

        assert config.default_mode == "analysis"
        assert config.auto_copy is True


def test_save_and_reload_config():
    """save_config should persist and reload correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_path = os.path.join(tmpdir, "prefs.json")
        db_path = os.path.join(tmpdir, "test.db")

        config = get_config(db_path=db_path, prefs_path=prefs_path)
        config.default_mode = "creative"
        config.auto_copy = True
        save_config(config)

        # Reload without overrides — should pick up saved values
        reloaded = get_config(db_path=db_path, prefs_path=prefs_path)
        assert reloaded.default_mode == "creative"
        assert reloaded.auto_copy is True
