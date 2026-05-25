"""Floating window with modern prompt generation UI."""

import subprocess
import time

import objc
import pyperclip
from AppKit import *
from Foundation import *


class PromptWindow(NSObject):
    """Floating frosted-glass window for prompt generation."""

    def init(self):
        """Initialize window."""
        self = objc.super(PromptWindow, self).init()
        if self:
            self.delegate = None
            self.enhanced_text = ""
            self.is_generating = False
            self.current_mode = "general"
            self._build_window()
        return self

    def setDelegate_(self, delegate):
        """Set the app delegate."""
        self.delegate = delegate
        if delegate and hasattr(delegate, "config"):
            modes = ["general", "image", "code", "creative", "analysis"]
            default = delegate.config.default_mode
            if default in modes:
                self.mode_selector.setSelectedSegment_(modes.index(default))

    def _build_window(self):
        """Build the floating window."""
        win_width = 500
        win_height = 420

        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, win_width, win_height),
            NSWindowStyleMaskBorderless | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setHasShadow_(True)
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
            | NSWindowCollectionBehaviorFullScreenAuxiliary
        )

        # Blur background
        blur_view = NSVisualEffectView.alloc().initWithFrame_(
            NSMakeRect(0, 0, win_width, win_height)
        )
        blur_view.setMaterial_(NSVisualEffectMaterialPopover)
        blur_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        blur_view.setState_(NSVisualEffectStateActive)
        blur_view.setWantsLayer_(True)
        blur_view.layer().setCornerRadius_(12.0)
        blur_view.layer().setMasksToBounds_(True)

        # Title
        title_label = NSTextField.labelWithString_("text2prompt")
        title_label.setFrame_(NSMakeRect(20, 376, 200, 24))
        title_label.setFont_(NSFont.boldSystemFontOfSize_(16))
        blur_view.addSubview_(title_label)

        # Mode selector
        self.mode_selector = NSSegmentedControl.alloc().initWithFrame_(NSMakeRect(20, 336, 460, 30))
        self.mode_selector.setSegmentCount_(5)
        self.mode_selector.setLabel_forSegment_("General", 0)
        self.mode_selector.setLabel_forSegment_("Image", 1)
        self.mode_selector.setLabel_forSegment_("Code", 2)
        self.mode_selector.setLabel_forSegment_("Creative", 3)
        self.mode_selector.setLabel_forSegment_("Analysis", 4)
        self.mode_selector.setSelectedSegment_(0)
        blur_view.addSubview_(self.mode_selector)

        # Input field (with Enter key to generate)
        self.input_field = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 286, 460, 40))
        self.input_field.setPlaceholderString_("Enter your idea...")
        self.input_field.setFont_(NSFont.systemFontOfSize_(14))
        self.input_field.setBordered_(True)
        self.input_field.setBezeled_(True)
        self.input_field.setTarget_(self)
        self.input_field.setAction_("handleGenerate:")
        blur_view.addSubview_(self.input_field)

        # Generate button
        self.generate_btn = NSButton.alloc().initWithFrame_(NSMakeRect(380, 236, 100, 30))
        self.generate_btn.setTitle_("Generate")
        self.generate_btn.setBezelStyle_(NSBezelStyleRounded)
        self.generate_btn.setTarget_(self)
        self.generate_btn.setAction_("handleGenerate:")
        blur_view.addSubview_(self.generate_btn)

        # Spinner
        self.spinner = NSProgressIndicator.alloc().initWithFrame_(NSMakeRect(230, 160, 40, 40))
        self.spinner.setStyle_(NSProgressIndicatorStyleSpinning)
        self.spinner.setHidden_(True)
        blur_view.addSubview_(self.spinner)

        # Status label
        self.status_label = NSTextField.labelWithString_("")
        self.status_label.setFrame_(NSMakeRect(20, 200, 460, 20))
        self.status_label.setFont_(NSFont.systemFontOfSize_(12))
        self.status_label.setTextColor_(NSColor.secondaryLabelColor())
        blur_view.addSubview_(self.status_label)

        # Output scroll view
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 60, 460, 130))
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setDrawsBackground_(False)
        scroll_view.setHidden_(True)

        content_size = scroll_view.contentSize()
        self.output_view = NSTextView.alloc().initWithFrame_(
            NSMakeRect(0, 0, content_size.width, content_size.height)
        )
        self.output_view.setEditable_(False)
        self.output_view.setDrawsBackground_(False)
        self.output_view.setFont_(NSFont.systemFontOfSize_(13))
        scroll_view.setDocumentView_(self.output_view)
        blur_view.addSubview_(scroll_view)
        self.scroll_view = scroll_view

        # Copy button
        self.copy_btn = NSButton.alloc().initWithFrame_(NSMakeRect(280, 16, 90, 30))
        self.copy_btn.setTitle_("Copy")
        self.copy_btn.setBezelStyle_(NSBezelStyleRounded)
        self.copy_btn.setTarget_(self)
        self.copy_btn.setAction_("handleCopy:")
        self.copy_btn.setHidden_(True)
        blur_view.addSubview_(self.copy_btn)

        # Replace button
        self.replace_btn = NSButton.alloc().initWithFrame_(NSMakeRect(380, 16, 100, 30))
        self.replace_btn.setTitle_("Replace")
        self.replace_btn.setBezelStyle_(NSBezelStyleRounded)
        self.replace_btn.setTarget_(self)
        self.replace_btn.setAction_("handleReplace:")
        self.replace_btn.setHidden_(True)
        self.replace_btn.setKeyEquivalent_("\r")
        blur_view.addSubview_(self.replace_btn)

        # History button
        self.history_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 16, 100, 30))
        self.history_btn.setTitle_("History")
        self.history_btn.setBezelStyle_(NSBezelStyleRounded)
        self.history_btn.setTarget_(self)
        self.history_btn.setAction_("handleHistory:")
        blur_view.addSubview_(self.history_btn)

        self.window.setContentView_(blur_view)

    def show_window(self):
        """Position and show window below the status item button."""
        screen_frame = NSScreen.mainScreen().frame()
        win_width = 500
        win_height = 420
        menu_bar_height = 25

        x = (screen_frame.size.width - win_width) / 2
        y = screen_frame.size.height - menu_bar_height - win_height - 10

        self.window.setFrameOrigin_(NSMakePoint(x, y))
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
        self.window.makeFirstResponder_(self.input_field)

    def close(self):
        """Close the window."""
        self.window.close()

    def handleGenerate_(self, sender):
        """Handle generate button click."""
        input_text = self.input_field.stringValue().strip()
        if not input_text:
            return

        self.is_generating = True
        self.generate_btn.setEnabled_(False)
        self.spinner.setHidden_(False)
        self.spinner.startAnimation_(None)
        self.status_label.setStringValue_("Generating prompt...")
        self.status_label.setTextColor_(NSColor.secondaryLabelColor())
        self.scroll_view.setHidden_(True)
        self.copy_btn.setHidden_(True)
        self.replace_btn.setHidden_(True)

        segment = self.mode_selector.selectedSegment()
        modes = ["general", "image", "code", "creative", "analysis"]
        self.current_mode = modes[segment]

        if self.delegate:
            self.delegate.generate_prompt(input_text, self.current_mode, self)

    def updateOutput_(self, text):
        """Update output text."""
        self.enhanced_text = text
        self.output_view.setString_(text)

        self.spinner.stopAnimation_(None)
        self.spinner.setHidden_(True)
        self.scroll_view.setHidden_(False)
        self.copy_btn.setHidden_(False)
        self.replace_btn.setHidden_(False)
        self.status_label.setStringValue_("Prompt generated!")
        self.status_label.setTextColor_(NSColor.secondaryLabelColor())
        self.generate_btn.setEnabled_(True)
        self.is_generating = False

    def showError_(self, error_msg):
        """Show error message."""
        self.spinner.stopAnimation_(None)
        self.spinner.setHidden_(True)
        self.status_label.setStringValue_("Error: " + str(error_msg))
        self.status_label.setTextColor_(NSColor.systemRedColor())
        self.output_view.setString_(str(error_msg))
        self.scroll_view.setHidden_(False)
        self.generate_btn.setEnabled_(True)
        self.is_generating = False

    def handleCopy_(self, sender):
        """Copy to clipboard."""
        pyperclip.copy(self.enhanced_text)
        self.status_label.setStringValue_("Copied to clipboard!")
        self.window.close()

    def _send_paste_(self, timer):
        """Send Cmd+V via AppleScript after window closes."""
        script = """
        tell application "System Events"
            keystroke "v" using command down
        end tell
        """
        try:
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass

    def handleReplace_(self, sender):
        """Replace selected text."""
        pyperclip.copy(self.enhanced_text)
        self.window.close()

        # Send paste after a short delay so the window has closed
        # and focus returns to the previous app.
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.15, self, "_send_paste:", None, False
        )

    def handleHistory_(self, sender):
        """Show history."""
        if self.delegate:
            self.delegate.show_history()
