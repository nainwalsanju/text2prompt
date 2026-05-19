"""CLI argument and mode parsing."""

MODE_GENERAL = "general"
MODE_IMAGE = "image"
MODE_CODE = "code"
MODE_CREATIVE = "creative"
MODE_ANALYSIS = "analysis"

VALID_MODES = {MODE_GENERAL, MODE_IMAGE, MODE_CODE, MODE_CREATIVE, MODE_ANALYSIS}

MODE_FLAGS = {
    "--image": MODE_IMAGE,
    "--code": MODE_CODE,
    "--creative": MODE_CREATIVE,
    "--analysis": MODE_ANALYSIS,
}


def parse_mode_and_text(args: list[str], clipboard_text: str | None = None) -> tuple[str, str]:
    """Parse mode and text from CLI args or clipboard.

    Args:
        args: CLI arguments (sys.argv[1:])
        clipboard_text: Optional clipboard text fallback

    Returns:
        Tuple of (mode, text)
    """
    mode = MODE_GENERAL

    if args:
        # Check for mode flags
        if args[0] in MODE_FLAGS:
            mode = MODE_FLAGS[args[0]]
            text = " ".join(args[1:]).strip()
        else:
            text = " ".join(args).strip()
    else:
        text = (clipboard_text or "").strip()
        # Check for /image prefix in clipboard
        if text.lower().startswith("/image "):
            mode = MODE_IMAGE
            text = text[7:].strip()

    return mode, text
