"""Main application: Menu bar app with modern UI."""

import sys
import os
import time
import subprocess
import pyperclip
import threading

import objc
from AppKit import *
from Foundation import *
from PyObjCTools import AppHelper

from text2prompt.config import get_config
from text2prompt.utils.parser import parse_mode_and_text
from text2prompt.utils.system import get_active_context
from text2prompt.memory.db import init_db, get_history, save_interaction, clear_memory
from text2prompt.engine.templates import get_registry
from text2prompt.engine.model import ModelEngine, ModelError
from text2prompt.menu.statusbar import StatusBarApp


class Text2PromptApp(NSApplication):
    """Main application class."""
    pass


class AppDelegate(NSObject):
    """Application delegate managing the prompt enhancement workflow."""

    def applicationDidFinishLaunching_(self, notification):
        """Initialize app on launch."""
        print("✅ text2prompt v2.0 launched", flush=True)
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
        
        # Handle CLI args if provided
        args = sys.argv[1:]
        if args:
            self._handle_cli_args(args)

    def _handle_cli_args(self, args):
        """Handle command-line arguments."""
        mode, text = parse_mode_and_text(args)
        if text:
            # Show popover with pre-filled text
            self.statusbar._show_popover()
            # Wait for popover to be ready
            AppHelper.callAfter(self._fill_and_generate, text, mode)

    def _fill_and_generate(self, text, mode):
        """Fill input and trigger generation."""
        if hasattr(self.statusbar, 'popover') and self.statusbar.popover:
            popover = self.statusbar.popover
            popover.input_field.setStringValue_(text)
            # Set mode
            modes = ["general", "image", "code", "creative", "analysis"]
            if mode in modes:
                popover.mode_selector.setSelectedSegment_(modes.index(mode))
            # Trigger generation
            popover.on_generate_(None)

    def generate_prompt(self, input_text, mode, popover):
        """Generate prompt in background thread."""
        def do_generate():
            try:
                # Check availability
                is_available, reason = self.engine.check_availability()
                if not is_available:
                    AppHelper.callAfter(popover.show_error, f"Model not available: {reason}")
                    return

                # Get context and history
                base_context = get_active_context()
                context_id = f"{base_context}:{mode}"
                history = get_history(self.conn, context_id)
                
                # Format prompt
                full_prompt = self.registry.format_prompt(history, input_text, mode)
                
                # Generate response
                print("🤖 Generating response...", flush=True)
                response = self.engine.generate_response(full_prompt)
                enhanced_text = response.strip()
                print("✅ Response generated!", flush=True)
                
                # Save interaction
                save_interaction(self.conn, context_id, input_text, enhanced_text)
                
                # Update UI
                AppHelper.callAfter(popover.update_output, enhanced_text)
                
            except Exception as e:
                print(f"❌ Exception: {e}", flush=True)
                AppHelper.callAfter(popover.show_error, str(e))
        
        # Run in background thread
        thread = threading.Thread(target=do_generate, daemon=True)
        thread.start()

    def show_history(self):
        """Show prompt history."""
        # TODO: Implement history window
        print("History view not yet implemented", flush=True)

    def show_preferences(self):
        """Show preferences panel."""
        # TODO: Implement preferences window
        print("Preferences view not yet implemented", flush=True)


def run_app(args):
    """Run the application.

    Args:
        args: CLI arguments
    """
    sys.argv = [sys.argv[0]] + args

    app = Text2PromptApp.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()
