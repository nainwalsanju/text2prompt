"""Tests for parser module."""

from text2prompt.utils.parser import (
    MODE_ANALYSIS,
    MODE_CODE,
    MODE_CREATIVE,
    MODE_GENERAL,
    MODE_IMAGE,
    VALID_MODES,
    parse_mode_and_text,
)


def test_parse_general_from_args():
    """Parse general mode from CLI args."""
    mode, text = parse_mode_and_text(["hello world"])
    assert mode == MODE_GENERAL
    assert text == "hello world"


def test_parse_image_mode_flag():
    """Parse image mode from --image flag."""
    mode, text = parse_mode_and_text(["--image", "a cat drinking coffee"])
    assert mode == MODE_IMAGE
    assert text == "a cat drinking coffee"


def test_parse_image_mode_prefix():
    """Parse image mode from /image prefix in clipboard text."""
    mode, text = parse_mode_and_text([], clipboard_text="/image a sunset")
    assert mode == MODE_IMAGE
    assert text == "a sunset"


def test_parse_code_mode_flag():
    """Parse code mode from --code flag."""
    mode, text = parse_mode_and_text(["--code", "explain this function"])
    assert mode == MODE_CODE
    assert text == "explain this function"


def test_parse_creative_mode_flag():
    """Parse creative mode from --creative flag."""
    mode, text = parse_mode_and_text(["--creative", "write a poem about rain"])
    assert mode == MODE_CREATIVE
    assert text == "write a poem about rain"


def test_parse_analysis_mode_flag():
    """Parse analysis mode from --analysis flag."""
    mode, text = parse_mode_and_text(["--analysis", "analyze this data"])
    assert mode == MODE_ANALYSIS
    assert text == "analyze this data"


def test_parse_from_clipboard_fallback():
    """Fall back to clipboard text when no args provided."""
    mode, text = parse_mode_and_text([], clipboard_text="some idea")
    assert mode == MODE_GENERAL
    assert text == "some idea"


def test_parse_empty_input():
    """Return empty text when no input provided."""
    mode, text = parse_mode_and_text([])
    assert mode == MODE_GENERAL
    assert text == ""


def test_parse_multiple_args():
    """Join multiple args into single text."""
    mode, text = parse_mode_and_text(["hello", "world", "test"])
    assert text == "hello world test"


def test_valid_modes_contains_all():
    """VALID_MODES should contain all modes."""
    assert MODE_GENERAL in VALID_MODES
    assert MODE_IMAGE in VALID_MODES
    assert MODE_CODE in VALID_MODES
    assert MODE_CREATIVE in VALID_MODES
    assert MODE_ANALYSIS in VALID_MODES
