"""Main application: Menu bar app with modern UI.

Supports two modes:
- **CLI mode**: When text arguments are provided, generates a prompt
  synchronously, prints it to stdout, and exits.
- **GUI mode**: When launched with no arguments (or ``--gui``), starts
  a macOS menu bar app with popover, hotkey, and history.
"""

import sys
import threading

import pyperclip

from text2prompt.config import get_config
from text2prompt.engine.model import ModelEngine, ModelError
from text2prompt.engine.templates import get_registry
from text2prompt.memory.db import get_history, init_db, save_interaction
from text2prompt.utils.parser import parse_mode_and_text
from text2prompt.utils.system import get_active_context

# Separator between context prefix and mode in context_id.
# Using ``|`` avoids ambiguity with the ``::`` inside the app/window prefix.
MODE_SEPARATOR = "|"


# ---------------------------------------------------------------------------
# CLI mode
# ---------------------------------------------------------------------------

def run_cli(text: str, mode: str) -> None:
    """Run in CLI mode — generate, print, exit.

    Args:
        text: The raw idea text from the user.
        mode: Prompt mode (general, image, code, creative, analysis).
    """
    config = get_config()
    engine = ModelEngine()
    registry = get_registry()

    is_available, reason = engine.check_availability()
    if not is_available:
        print(f"Error: Model not available — {reason}", file=sys.stderr)
        sys.exit(1)

    conn = init_db(config.db_path)
    context_id = f"cli{MODE_SEPARATOR}{mode}"
    history = get_history(conn, context_id)
    
    custom_rule = config.custom_rules.get(mode, "") if config.custom_rules else ""
    full_prompt = registry.format_prompt(history, text, mode, custom_rule)

    try:
        response = engine.generate_response(full_prompt)
        if config.redact_sensitive_info:
            from text2prompt.utils.redactor import redact_text
            response = redact_text(response)
    except ModelError as e:
        print(f"Error: {e}", file=sys.stderr)
        conn.close()
        sys.exit(1)

    print(response)

    if config.auto_copy:
        pyperclip.copy(response)
    if config.save_history:
        save_interaction(conn, context_id, text, response)
    conn.close()


# ---------------------------------------------------------------------------
# GUI mode
# ---------------------------------------------------------------------------

def run_gui(args: list[str]) -> None:
    """Run as macOS menu bar application.

    Args:
        args: CLI arguments to forward into the GUI.

    The GUI module is imported lazily so that CLI mode never
    touches Cocoa / PyObjC.
    """
    from text2prompt.gui import start_gui

    start_gui(args)


# ---------------------------------------------------------------------------
# Entry dispatcher
# ---------------------------------------------------------------------------

def run_app(args: list[str]) -> None:
    """Dispatch to CLI or GUI mode.

    Args:
        args: CLI arguments (sys.argv[1:]).
    """
    # Explicit --gui flag always opens the menu bar app
    if "--gui" in args:
        gui_args = [a for a in args if a != "--gui"]
        run_gui(gui_args)
        return

    mode, text = parse_mode_and_text(args)

    if text:
        # Text provided → fast CLI path (no Cocoa event loop)
        run_cli(text, mode)
    else:
        # No text → launch menu bar app
        run_gui(args)
