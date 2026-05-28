"""UI style constants — single source of truth for dimensions, typography, and color tokens."""

from AppKit import NSColor, NSFont, NSVisualEffectMaterialDark, NSAppearanceNameDarkAqua

# Window dimensions
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 420
WINDOW_MIN_HEIGHT = 300

# Layout & Spacing
MARGIN = 20
ELEMENT_SPACING = 12
BUTTON_HEIGHT = 30
BUTTON_WIDTH = 100
STATUS_HEIGHT = 24

# Radii
WINDOW_CORNER_RADIUS = 16.0
ELEMENT_CORNER_RADIUS = 8.0

# Est menu bar height
MENU_BAR_HEIGHT = 25

# Color Tokens
# Frosted obsidian background (Material Dark)
BACKDROP_MATERIAL = NSVisualEffectMaterialDark

# Standard Dark Aqua appearance name
APPEARANCE_DARK_AQUA = NSAppearanceNameDarkAqua

# Sleek Spotlight-style dark translucency
COLOR_CONTAINER_BG = NSColor.colorWithCalibratedWhite_alpha_(0.08, 0.4)
COLOR_INPUT_BG = NSColor.colorWithCalibratedWhite_alpha_(0.15, 0.5)
COLOR_INPUT_FOCUS_BG = NSColor.colorWithCalibratedWhite_alpha_(0.20, 0.6)

# Neon Accent (Cyberpunk Purple/Indigo) for focus rings and action highlights
COLOR_ACCENT_GLOW = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.47, 0.38, 0.98, 1.0)

# High-contrast readable primary text
COLOR_TEXT_PRIMARY = NSColor.whiteColor()
# Muted secondary text
COLOR_TEXT_SECONDARY = NSColor.colorWithCalibratedWhite_alpha_(0.7, 1.0)

# Subtle border tint
COLOR_BORDER_LIGHT = NSColor.colorWithCalibratedWhite_alpha_(1.0, 0.1)

# Typography Tokens
FONT_TITLE = NSFont.boldSystemFontOfSize_(16)
FONT_BODY = NSFont.systemFontOfSize_(13)
FONT_INPUT = NSFont.systemFontOfSize_(14)
FONT_STATUS = NSFont.systemFontOfSize_(12)
