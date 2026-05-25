"""Layout helpers for panel geometry.

These functions are available for reuse but the main popover window
(currently in menu/popover.py) uses hardcoded frame values.
"""

from text2prompt.ui.styles import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    MARGIN,
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


def get_button_positions() -> dict[str, tuple[float, float]]:
    """Get standard button positions.

    Returns:
        Dict mapping button name to (x, y) position
    """
    return {
        "cancel": (MARGIN, MARGIN - BUTTON_HEIGHT + 10),
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
