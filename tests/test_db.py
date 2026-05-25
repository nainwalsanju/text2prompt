"""Tests for database module."""

import os
import tempfile

import pytest

from text2prompt.memory.db import clear_memory, get_history, init_db, save_interaction


@pytest.fixture
def db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database = init_db(tmp.name)
        yield database
        database.close()
        os.unlink(tmp.name)


def test_init_db_creates_table(db):
    """init_db should create chat_history table."""
    conn = db
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
    assert cursor.fetchone() is not None


def test_save_and_get_history(db):
    """save_interaction should store and retrieve history."""
    save_interaction(db, "test_context", "user input", "assistant output")
    history = get_history(db, "test_context")
    assert len(history) == 2
    assert history[0] == ("user", "user input")
    assert history[1] == ("assistant", "assistant output")


def test_get_history_empty_context(db):
    """get_history should return empty list for unknown context."""
    history = get_history(db, "unknown_context")
    assert history == []


def test_get_history_ordered(db):
    """get_history should return history in insertion order."""
    save_interaction(db, "ctx", "input1", "output1")
    save_interaction(db, "ctx", "input2", "output2")
    save_interaction(db, "ctx", "input3", "output3")
    history = get_history(db, "ctx")
    assert len(history) == 6  # 3 interactions * 2 entries
    assert history[0][1] == "input1"
    assert history[1][1] == "output1"


def test_clear_memory(db):
    """clear_memory should delete all history for a context."""
    save_interaction(db, "ctx", "input", "output")
    clear_memory(db, "ctx")
    history = get_history(db, "ctx")
    assert history == []


def test_clear_memory_other_context_untouched(db):
    """clear_memory should not affect other contexts."""
    save_interaction(db, "ctx1", "input1", "output1")
    save_interaction(db, "ctx2", "input2", "output2")
    clear_memory(db, "ctx1")
    history = get_history(db, "ctx2")
    assert len(history) == 2


def test_history_limit(db):
    """get_history should return only last 10 entries."""
    for i in range(15):
        save_interaction(db, "ctx", f"input{i}", f"output{i}")
    history = get_history(db, "ctx")
    assert len(history) <= 10
