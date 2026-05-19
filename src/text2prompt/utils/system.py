"""System utilities: osascript, app detection."""

import subprocess


def get_active_context() -> str:
    """Get the active application context.

    Returns:
        String in format 'AppName::WindowTitle'
    """
    script = """
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        set windowTitle to "Unknown"
        try
            set windowTitle to name of front window of application process frontApp
        end try
        return frontApp & "::" & windowTitle
    end tell
    """
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return "Global::Default"
