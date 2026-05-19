"""Apple Foundation Models SDK wrapper."""

import asyncio
from typing import Optional

try:
    import apple_fm_sdk as fm
except ImportError:
    fm = None


class ModelError(Exception):
    """Error during model operation."""
    pass


class ModelEngine:
    """Wrapper around Apple's Foundation Models SDK."""

    def __init__(self):
        self._model = None

    def _ensure_sdk_imported(self):
        """Verify SDK is available."""
        if fm is None:
            raise ModelError("apple-fm-sdk is not installed. Install with: pip install apple-fm-sdk")

    def check_availability(self) -> tuple[bool, Optional[str]]:
        """Check if the on-device model is available.

        Returns:
            Tuple of (is_available, reason_if_not)
        """
        self._ensure_sdk_imported()
        try:
            self._model = fm.SystemLanguageModel()
            return self._model.is_available()
        except Exception as e:
            return False, str(e)

    def generate_response(self, prompt: str) -> str:
        """Generate a response from the model.

        Args:
            prompt: The prompt to send to the model

        Returns:
            Model response text

        Raises:
            ModelError: If generation fails
        """
        self._ensure_sdk_imported()
        if self._model is None:
            self._model = fm.SystemLanguageModel()

        try:
            session = fm.LanguageModelSession(model=self._model)
            response = session.respond(prompt)
            return response.strip()
        except Exception as e:
            raise ModelError(str(e)) from e


