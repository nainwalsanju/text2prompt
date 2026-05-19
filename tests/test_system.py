"""Tests for system utilities."""

from text2prompt.utils.system import get_active_context


def test_get_active_context_returns_string():
    """get_active_context should return a string."""
    result = get_active_context()
    assert isinstance(result, str)


def test_get_active_context_contains_separator():
    """get_active_context should return 'App::WindowTitle' format."""
    result = get_active_context()
    assert "::" in result
