"""Prompt template registry."""

from text2prompt.templates.analysis import SYSTEM_INSTRUCTION as ANALYSIS_INSTRUCTION
from text2prompt.templates.code import SYSTEM_INSTRUCTION as CODE_INSTRUCTION
from text2prompt.templates.creative import SYSTEM_INSTRUCTION as CREATIVE_INSTRUCTION
from text2prompt.templates.general import SYSTEM_INSTRUCTION as GENERAL_INSTRUCTION
from text2prompt.templates.image import SYSTEM_INSTRUCTION as IMAGE_INSTRUCTION
from text2prompt.templates.music import SYSTEM_INSTRUCTION as MUSIC_INSTRUCTION
from text2prompt.utils.parser import (
    MODE_ANALYSIS,
    MODE_CODE,
    MODE_CREATIVE,
    MODE_GENERAL,
    MODE_IMAGE,
    MODE_MUSIC,
)

_INSTRUCTIONS = {
    MODE_GENERAL: GENERAL_INSTRUCTION,
    MODE_IMAGE: IMAGE_INSTRUCTION,
    MODE_CODE: CODE_INSTRUCTION,
    MODE_CREATIVE: CREATIVE_INSTRUCTION,
    MODE_ANALYSIS: ANALYSIS_INSTRUCTION,
    MODE_MUSIC: MUSIC_INSTRUCTION,
}


class TemplateRegistry:
    """Registry of prompt templates by mode."""

    def __init__(self):
        self._instructions = dict(_INSTRUCTIONS)

    @property
    def modes(self) -> set[str]:
        """Return all registered modes."""
        return set(self._instructions.keys())

    def get_system_instruction(self, mode: str) -> str:
        """Get system instruction for a mode. Falls back to general."""
        return self._instructions.get(mode, _INSTRUCTIONS[MODE_GENERAL])

    def format_prompt(
        self, history: list[tuple[str, str]], new_text: str, mode: str, custom_rule: str = ""
    ) -> str:
        """Format a complete prompt with history, new input, and custom rules.

        Args:
            history: List of (role, content) tuples
            new_text: New user input
            mode: Prompt mode
            custom_rule: Optional user custom rules to append

        Returns:
            Formatted prompt string
        """
        instruction = self.get_system_instruction(mode)
        if custom_rule:
            instruction += (
                f"\n\nCUSTOM USER RULES (CRITICAL - YOU MUST ADHERE STRICTLY TO THESE RULES):\n{custom_rule}"
            )

        if not history:
            return f"{instruction}\n\nUSER INPUT: {new_text}"

        formatted = f"{instruction}\n\nPREVIOUS CONVERSATION CONTEXT FOR THIS WINDOW:\n"
        for role, content in history:
            formatted += f"[{role.upper()}]: {content}\n\n"

        formatted += f"NEW USER INPUT: {new_text}\n"
        formatted += "Please update or generate a new prompt taking the previous context and the new input into account."
        return formatted


_registry: TemplateRegistry | None = None


def get_registry() -> TemplateRegistry:
    """Get the singleton template registry."""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
    return _registry

