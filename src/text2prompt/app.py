"""Main application: NSApplication + AppDelegate with streaming support."""

import sys
import os
import time
import subprocess
import pyperclip

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
from text2prompt.ui.styles import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MARGIN,
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    STATUS_HEIGHT,
    CORNER_RADIUS,
)


class FloatingPanel(NSPanel):
    """Borderless floating window."""

    def canBecomeKeyWindow(self):
        return True

    def canBecomeMainWindow(self):
        return True


class AppDelegate(NSObject):
    """Application delegate managing the prompt enhancement workflow."""

    def applicationDidFinishLaunching_(self, notification):
        """Initialize app on launch."""
        print("✅ App launched", flush=True)
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

        # Parse input
        args = sys.argv[1:]
        self.mode, self.original_text = parse_mode_and_text(args, pyperclip.paste())
        print(f"✅ Input parsed. Mode: {self.mode}, Text length: {len(self.original_text)}", flush=True)

        if not self.original_text:
            print("No text provided.")
            NSApp.terminate_(self)
            return

        # Initialize config and database
        self.config = get_config()
        self.conn = init_db(self.config.db_path)
        base_context = get_active_context()
        self.context_id = f"{base_context}:{self.mode}"
        print(f"✅ Context fetched: {self.context_id}", flush=True)

        # Handle clear memory command
        if self.original_text.lower() == "clear memory":
            clear_memory(self.conn, self.context_id)
            print("Memory cleared.")
            NSApp.terminate_(self)
            return

        # Initialize engine and templates
        self.engine = ModelEngine()
        self.registry = get_registry()

        # Build UI
        self.buildUI()

        # Start generation
        self.startGeneration()

    def buildUI(self):
        """Build the floating panel UI."""
        rect = NSMakeRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        mask = NSWindowStyleMaskBorderless | NSWindowStyleMaskResizable
        self.window = FloatingPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, mask, NSBackingStoreBuffered, False
        )
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.center()
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setMovableByWindowBackground_(True)

        # Blur view
        blur_view = NSVisualEffectView.alloc().initWithFrame_(rect)
        blur_view.setMaterial_(NSVisualEffectMaterialPopover)
        blur_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        blur_view.setState_(NSVisualEffectStateActive)
        blur_view.setWantsLayer_(True)
        blur_view.layer().setCornerRadius_(CORNER_RADIUS)
        blur_view.layer().setMasksToBounds_(True)
        blur_view.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
        self.window.setContentView_(blur_view)

        # Status label
        self.status_label = NSTextField.labelWithString_("Enhancing prompt...")
        self.status_label.setFrame_(NSMakeRect(MARGIN, WINDOW_HEIGHT - MARGIN - STATUS_HEIGHT, WINDOW_WIDTH - MARGIN * 2, STATUS_HEIGHT))
        blur_view.addSubview_(self.status_label)

        # Spinner
        self.spinner = NSProgressIndicator.alloc().initWithFrame_(NSMakeRect(WINDOW_WIDTH // 2 - 25, WINDOW_HEIGHT // 2 - 25, 50, 50))
        self.spinner.setStyle_(NSProgressIndicatorStyleSpinning)
        self.spinner.startAnimation_(None)
        blur_view.addSubview_(self.spinner)

        # Scroll view
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(MARGIN, MARGIN + BUTTON_HEIGHT + 10, WINDOW_WIDTH - MARGIN * 2, WINDOW_HEIGHT - MARGIN * 3 - BUTTON_HEIGHT - STATUS_HEIGHT))
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setDrawsBackground_(False)

        content_size = scroll_view.contentSize()
        self.text_view = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, content_size.width, content_size.height))
        self.text_view.setEditable_(False)
        self.text_view.setDrawsBackground_(False)
        scroll_view.setDocumentView_(self.text_view)
        scroll_view.setHidden_(True)
        blur_view.addSubview_(scroll_view)
        self.scroll_view = scroll_view

        # Replace button
        self.replace_btn = NSButton.alloc().initWithFrame_(NSMakeRect(WINDOW_WIDTH - MARGIN - BUTTON_WIDTH, MARGIN - BUTTON_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT))
        self.replace_btn.setTitle_("Replace")
        self.replace_btn.setBezelStyle_(NSBezelStyleRounded)
        self.replace_btn.setTarget_(self)
        self.replace_btn.setAction_(objc.selector(self.replaceAction_, signature=b'v@:@'))
        self.replace_btn.setHidden_(True)
        self.replace_btn.setKeyEquivalent_("\r")
        blur_view.addSubview_(self.replace_btn)

        # Copy button
        self.copy_btn = NSButton.alloc().initWithFrame_(NSMakeRect(WINDOW_WIDTH - MARGIN - BUTTON_WIDTH * 2 - 10, MARGIN - BUTTON_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT))
        self.copy_btn.setTitle_("Copy")
        self.copy_btn.setBezelStyle_(NSBezelStyleRounded)
        self.copy_btn.setTarget_(self)
        self.copy_btn.setAction_(objc.selector(self.copyAction_, signature=b'v@:@'))
        self.copy_btn.setHidden_(True)
        blur_view.addSubview_(self.copy_btn)

        # Cancel button
        self.cancel_btn = NSButton.alloc().initWithFrame_(NSMakeRect(MARGIN, MARGIN - BUTTON_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT))
        self.cancel_btn.setTitle_("Cancel")
        self.cancel_btn.setBezelStyle_(NSBezelStyleRounded)
        self.cancel_btn.setTarget_(self)
        self.cancel_btn.setAction_(objc.selector(self.cancelAction_, signature=b'v@:@'))
        blur_view.addSubview_(self.cancel_btn)

        # Mode indicator
        mode_label = self._get_mode_label()
        self.status_label.setStringValue_(f"Enhancing prompt... [{mode_label}]")

        self.window.setDelegate_(self)
        NSApp.activateIgnoringOtherApps_(True)
        self.window.makeKeyAndOrderFront_(None)

    def _get_mode_label(self) -> str:
        """Get mode label for UI."""
        labels = {
            "image": "🎨 Image",
            "code": "💻 Code",
            "creative": "✍️ Creative",
            "analysis": "🔍 Analysis",
        }
        return labels.get(self.mode, "⚡ General")

    def windowDidResignKey_(self, notification):
        """Terminate app when window loses focus."""
        NSApp.terminate_(self)

    def startGeneration(self):
        """Start prompt generation."""
        print("⏳ Running generation...", flush=True)
        self.generatePrompt()

    def generatePrompt(self):
        """Generate enhanced prompt using model."""
        try:
            # Check availability
            is_available, reason = self.engine.check_availability()
            if not is_available:
                self.showError_(f"Models not available: {reason}")
                return

            # Get history and format prompt
            history = get_history(self.conn, self.context_id)
            full_prompt = self.registry.format_prompt(history, self.original_text, self.mode)

            # Generate response
            print("🤖 Generating response...", flush=True)
            response = self.engine.generate_response(full_prompt)
            self.enhanced_text = response.strip()
            print("✅ Response generated!", flush=True)

            # Save interaction
            save_interaction(self.conn, self.context_id, self.original_text, self.enhanced_text)

            # Show result
            AppHelper.callAfter(self.showResult_)

        except Exception as e:
            print(f"❌ Exception in generation: {e}", flush=True)
            self.showError_(str(e))

    def showResult_(self, sender=None):
        """Show generated result in UI."""
        self.spinner.stopAnimation_(None)
        self.spinner.setHidden_(True)
        self.status_label.setStringValue_(f"Prompt Generated! [{self._get_mode_label()}]")
        self.text_view.setString_(self.enhanced_text)
        self.scroll_view.setHidden_(False)
        self.replace_btn.setHidden_(False)
        self.copy_btn.setHidden_(False)
        self.window.makeFirstResponder_(self.replace_btn)

    def showError_(self, error_msg, sender=None):
        """Show error in UI."""
        def update_ui():
            NSApp.activateIgnoringOtherApps_(True)
            self.window.makeKeyAndOrderFront_(None)
            self.spinner.stopAnimation_(None)
            self.spinner.setHidden_(True)
            self.status_label.setStringValue_("Error generating prompt")
            self.text_view.setString_(error_msg)
            self.scroll_view.setHidden_(False)
        AppHelper.callAfter(update_ui)

    def copyAction_(self, sender):
        """Copy enhanced text to clipboard."""
        pyperclip.copy(self.enhanced_text)
        NSApp.terminate_(self)

    def replaceAction_(self, sender):
        """Replace selected text with enhanced version."""
        pyperclip.copy(self.enhanced_text)
        self.window.orderOut_(None)
        time.sleep(0.1)

        script = '''
        tell application "System Events"
            keystroke "v" using command down
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.showError_("Paste failed. Please grant Accessibility permissions in System Settings > Privacy & Security > Accessibility.")
            return

        NSApp.terminate_(self)

    def cancelAction_(self, sender):
        """Cancel and terminate."""
        NSApp.terminate_(self)


class EnhancerApp(NSApplication):
    """Main application class."""
    pass


def run_app(args):
    """Run the application.

    Args:
        args: CLI arguments
    """
    # Update sys.argv for the app
    sys.argv = [sys.argv[0]] + args

    app = EnhancerApp.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()
