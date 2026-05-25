"""Main application: Menu bar app with modern UI."""

import sys
import threading

import pyperclip
from AppKit import *
from Foundation import *
from PyObjCTools import AppHelper

from text2prompt.config import get_config
from text2prompt.engine.model import ModelEngine
from text2prompt.engine.templates import get_registry
from text2prompt.memory.db import get_history, init_db, save_interaction
from text2prompt.menu.history import HistoryWindow
from text2prompt.menu.hotkey import HotkeyManager
from text2prompt.menu.preferences import PreferencesWindow
from text2prompt.menu.statusbar import StatusBarApp
from text2prompt.utils.parser import parse_mode_and_text
from text2prompt.utils.system import get_active_context


class AppDelegate(NSObject):
    """Application delegate managing the prompt enhancement workflow."""

    def applicationDidFinishLaunching_(self, notification):
        """Initialize app on launch."""
        print("text2prompt v2.0 launched", flush=True)
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

        # Initialize config and database
        self.config = get_config()
        self.conn = init_db(self.config.db_path)

        # Initialize engine and templates
        self.engine = ModelEngine()
        self.registry = get_registry()

        # Setup status bar
        self.statusbar = StatusBarApp.alloc().init()
        self.statusbar.setDelegate_(self)

        # Initialize windows (lazy)
        self.history_window = None
        self.preferences_window = None

        # Setup global hotkey (Cmd+Shift+Space)
        self.hotkey_manager = HotkeyManager.alloc().init()
        self.hotkey_manager.setDelegate_(self)
        self.hotkey_manager.start_monitoring()

        # Handle CLI args if provided
        args = sys.argv[1:]
        if args:
            self._handle_cli_args(args)

    def _handle_cli_args(self, args):
        """Handle command-line arguments."""
        mode, text = parse_mode_and_text(args)
        if text:
            self.statusbar._show_popover()
            AppHelper.callAfter(self._fill_and_generate, text, mode)

    def on_hotkey_pressed(self):
        """Handle global hotkey press."""
        AppHelper.callAfter(self.statusbar._show_popover)

    def _fill_and_generate(self, text, mode):
        """Fill input and trigger generation."""
        if hasattr(self.statusbar, "popover") and self.statusbar.popover:
            popover = self.statusbar.popover
            popover.input_field.setStringValue_(text)
            modes = ["general", "image", "code", "creative", "analysis"]
            if mode in modes:
                popover.mode_selector.setSelectedSegment_(modes.index(mode))
            popover.handleGenerate_(None)

    def generate_prompt(self, input_text, mode, popover):
        """Generate prompt in background thread."""

        def do_generate():
            try:
                is_available, reason = self.engine.check_availability()
                if not is_available:
                    AppHelper.callAfter(
                        lambda: popover.showError_("Model not available: " + reason)
                    )
                    return

                base_context = get_active_context() if self.config.include_context else "standalone"
                context_id = base_context + ":" + mode
                history = get_history(self.conn, context_id)

                full_prompt = self.registry.format_prompt(history, input_text, mode)

                print("Generating response...", flush=True)
                response = self.engine.generate_response(full_prompt)
                enhanced_text = response.strip()
                print("Response generated!", flush=True)

                if self.config.save_history:
                    save_interaction(self.conn, context_id, input_text, enhanced_text)

                if self.config.auto_copy:
                    AppHelper.callAfter(self._auto_copy, enhanced_text)

                AppHelper.callAfter(lambda: popover.updateOutput_(enhanced_text))

            except Exception as e:
                print("Exception: " + str(e), flush=True)
                AppHelper.callAfter(lambda: popover.showError_(str(e)))

        thread = threading.Thread(target=do_generate, daemon=True)
        thread.start()

    def _auto_copy(self, text):
        """Auto-copy text to clipboard."""
        pyperclip.copy(text)

    def show_history(self):
        """Show prompt history."""
        if self.history_window is None:
            self.history_window = HistoryWindow.alloc().init()
            self.history_window.setConnection_(self.conn)
        self.history_window.show()

    def show_preferences(self):
        """Show preferences panel."""
        if self.preferences_window is None:
            self.preferences_window = PreferencesWindow.alloc().init()
        self.preferences_window.show()


def run_app(args):
    """Run the application."""
    sys.argv = [sys.argv[0]] + args

    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)

    AppHelper.runEventLoop()
