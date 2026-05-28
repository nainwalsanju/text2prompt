"""Tests for template system."""

from text2prompt.engine.templates import get_registry
from text2prompt.utils.parser import (
    MODE_ANALYSIS,
    MODE_CODE,
    MODE_CREATIVE,
    MODE_GENERAL,
    MODE_IMAGE,
    MODE_MUSIC,
)


def test_registry_has_all_modes():
    """Registry should have templates for all modes."""
    registry = get_registry()
    assert MODE_GENERAL in registry.modes
    assert MODE_IMAGE in registry.modes
    assert MODE_CODE in registry.modes
    assert MODE_CREATIVE in registry.modes
    assert MODE_ANALYSIS in registry.modes
    assert MODE_MUSIC in registry.modes


def test_get_system_instruction_general():
    """General mode should return system instruction."""
    registry = get_registry()
    instruction = registry.get_system_instruction(MODE_GENERAL)
    assert "Prompt Engineer" in instruction or "expert" in instruction.lower()


def test_get_system_instruction_image():
    """Image mode should return image-specific instruction."""
    registry = get_registry()
    instruction = registry.get_system_instruction(MODE_IMAGE)
    assert "image" in instruction.lower() or "visual" in instruction.lower()


def test_get_system_instruction_code():
    """Code mode should return code-specific instruction."""
    registry = get_registry()
    instruction = registry.get_system_instruction(MODE_CODE)
    assert "code" in instruction.lower() or "programming" in instruction.lower()


def test_get_system_instruction_creative():
    """Creative mode should return creative-specific instruction."""
    registry = get_registry()
    instruction = registry.get_system_instruction(MODE_CREATIVE)
    assert len(instruction) > 50


def test_get_system_instruction_analysis():
    """Analysis mode should return analysis-specific instruction."""
    registry = get_registry()
    instruction = registry.get_system_instruction(MODE_ANALYSIS)
    assert len(instruction) > 50


def test_get_system_instruction_music():
    """Music mode should return music-specific instruction."""
    registry = get_registry()
    instruction = registry.get_system_instruction(MODE_MUSIC)
    assert "music" in instruction.lower() or "audio" in instruction.lower()


def test_format_prompt_no_history():
    """Format prompt without history should include instruction and input."""
    registry = get_registry()
    result = registry.format_prompt([], "test input", MODE_GENERAL)
    assert "test input" in result
    assert len(result) > len("test input")


def test_format_prompt_with_history():
    """Format prompt with history should include conversation context."""
    registry = get_registry()
    history = [("user", "previous input"), ("assistant", "previous output")]
    result = registry.format_prompt(history, "new input", MODE_GENERAL)
    assert "new input" in result
    assert "previous input" in result
    assert "previous output" in result


def test_format_prompt_invalid_mode():
    """Invalid mode should fall back to general."""
    registry = get_registry()
    result = registry.format_prompt([], "test", "invalid_mode")
    assert "test" in result


def test_format_prompt_with_custom_rule():
    """Format prompt should merge the custom guideline at the end."""
    registry = get_registry()
    result = registry.format_prompt([], "my theme", MODE_GENERAL, "Always write in French")
    assert "my theme" in result
    assert "Always write in French" in result
    assert "CUSTOM USER RULES" in result


def test_registry_singleton():
    """get_registry should return same instance."""
    r1 = get_registry()
    r2 = get_registry()
    assert r1 is r2

