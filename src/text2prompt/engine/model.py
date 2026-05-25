"""Apple Foundation Models SDK wrapper."""

import asyncio
import concurrent.futures

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
            raise ModelError(
                "apple-fm-sdk is not installed. Install with: pip install apple-fm-sdk"
            )

    def check_availability(self) -> tuple[bool, str | None]:
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

        session = fm.LanguageModelSession(model=self._model)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop — straightforward case
            try:
                response = asyncio.run(session.respond(prompt))
            except Exception as e:
                raise ModelError(str(e)) from e
        else:
            # Already in a running loop — run in separate thread to avoid
            # "This event loop is already running" errors.
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                try:
                    response = pool.submit(asyncio.run, session.respond(prompt)).result()
                except Exception as e:
                    raise ModelError(str(e)) from e

        return response.strip()
