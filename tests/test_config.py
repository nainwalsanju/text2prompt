"""Tests for config module."""

import os
import tempfile

from text2prompt.config import DEFAULT_DB_PATH, get_config


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
