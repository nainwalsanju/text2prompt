"""Layout helpers for panel geometry.

These functions provide reusable layout calculations based on the
constants in ``ui.styles``.  The main popover window (``menu/popover.py``)
can use these to avoid duplicating magic numbers.
"""

from text2prompt.ui.styles import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    MARGIN,
    MENU_BAR_HEIGHT,
    STATUS_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


def get_window_rect() -> tuple[float, float, float, float]:
    """Get default window rectangle (x, y, width, height).

    Returns:
        Tuple of (x, y, width, height)
    """
    return (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)


def get_centered_origin(screen_width: float, screen_height: float) -> tuple[float, float]:
    """Get centered x, y origin below the menu bar.

    Args:
        screen_width: Width of the main screen.
        screen_height: Height of the main screen.

    Returns:
        Tuple of (x, y) for ``setFrameOrigin_``.
    """
    x = (screen_width - WINDOW_WIDTH) / 2
    y = screen_height - MENU_BAR_HEIGHT - WINDOW_HEIGHT - 10
    return (x, y)


def get_button_positions() -> dict[str, tuple[float, float]]:
    """Get standard button positions.

    Returns:
        Dict mapping button name to (x, y) position
    """
    return {
        "history": (MARGIN, MARGIN - BUTTON_HEIGHT + 10),
        "copy": (WINDOW_WIDTH - MARGIN - BUTTON_WIDTH * 2 - 10, MARGIN - BUTTON_HEIGHT + 10),
        "replace": (WINDOW_WIDTH - MARGIN - BUTTON_WIDTH, MARGIN - BUTTON_HEIGHT + 10),
    }


def get_text_view_rect() -> tuple[float, float, float, float]:
    """Get text view rectangle.

    Returns:
        Tuple of (x, y, width, height)
    """
    return (
        MARGIN,
        MARGIN + BUTTON_HEIGHT + 10,
        WINDOW_WIDTH - MARGIN * 2,
        WINDOW_HEIGHT - MARGIN * 3 - BUTTON_HEIGHT - STATUS_HEIGHT,
    )


def get_status_label_rect() -> tuple[float, float, float, float]:
    """Get status label rectangle.

    Returns:
        Tuple of (x, y, width, height)
    """
    return (
        MARGIN,
        WINDOW_HEIGHT - MARGIN - STATUS_HEIGHT,
        WINDOW_WIDTH - MARGIN * 2,
        STATUS_HEIGHT,
    )
