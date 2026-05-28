"""Floating window with modern prompt generation UI."""

import subprocess
import threading

import objc
import pyperclip
from AppKit import *
from Foundation import *
from PyObjCTools import AppHelper

from text2prompt.ui.styles import (
    MENU_BAR_HEIGHT as menu_bar_height,
    WINDOW_HEIGHT as win_height,
    WINDOW_WIDTH as win_width,
    APPEARANCE_DARK_AQUA,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_TITLE,
    FONT_STATUS,
)
from text2prompt.ui.components import (
    PremiumFrostedGlassView,
    PremiumTextField,
    PremiumScrollView,
    PremiumTextView,
    PremiumButton,
    PremiumPrimaryButton,
    PremiumWindow,
)


class KeyPopoverWindow(PremiumWindow):
    """Custom NSWindow subclass to allow borderless windows to receive keyboard focus."""
    pass


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
            modes = ["general", "image", "code", "creative", "analysis", "music"]
            default = delegate.config.default_mode
            if default in modes:
                self.mode_selector.setSelectedSegment_(modes.index(default))

    def _build_window(self):
        """Build the floating window."""

        self.window = KeyPopoverWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, win_width, win_height),
            NSWindowStyleMaskBorderless | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setReleasedWhenClosed_(False)
        self.window.setAppearance_(NSAppearance.appearanceNamed_(APPEARANCE_DARK_AQUA))
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setHasShadow_(True)
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
            | NSWindowCollectionBehaviorFullScreenAuxiliary
        )

        # Blur background using our Design System frosted glass component
        blur_view = PremiumFrostedGlassView.alloc().initWithFrame_(
            NSMakeRect(0, 0, win_width, win_height)
        )

        # Title
        logo_label = NSTextField.labelWithString_("✦")
        logo_label.setFrame_(NSMakeRect(20, 382, 24, 24))
        logo_label.setFont_(NSFont.systemFontOfSize_weight_(16, NSFontWeightMedium))
        logo_label.setTextColor_(COLOR_TEXT_PRIMARY)
        blur_view.addSubview_(logo_label)

        title_label = NSTextField.labelWithString_("text2prompt")
        title_label.setFrame_(NSMakeRect(40, 383, 200, 24))
        title_label.setFont_(FONT_TITLE)
        title_label.setTextColor_(COLOR_TEXT_PRIMARY)
        blur_view.addSubview_(title_label)

        # Elegant top-right close button (✕)
        self.top_close_btn = PremiumButton.alloc().initWithFrame_(NSMakeRect(454, 381, 26, 26))
        self.top_close_btn.setTitle_("✕")
        self.top_close_btn.setTarget_(self)
        self.top_close_btn.setAction_("handleCloseBtn:")
        blur_view.addSubview_(self.top_close_btn)

        # Mode selector (styled with rounded/flat segments)
        self.mode_selector = NSSegmentedControl.alloc().initWithFrame_(NSMakeRect(20, 344, 460, 26))
        self.mode_selector.setSegmentCount_(6)
        self.mode_selector.setSegmentStyle_(NSSegmentStyleRoundRect)
        self.mode_selector.setLabel_forSegment_("General", 0)
        self.mode_selector.setLabel_forSegment_("Image", 1)
        self.mode_selector.setLabel_forSegment_("Code", 2)
        self.mode_selector.setLabel_forSegment_("Creative", 3)
        self.mode_selector.setLabel_forSegment_("Analysis", 4)
        self.mode_selector.setLabel_forSegment_("Music", 5)
        self.mode_selector.setSelectedSegment_(0)
        blur_view.addSubview_(self.mode_selector)

        # Design system thin separator
        divider = NSBox.alloc().initWithFrame_(NSMakeRect(20, 331, 460, 1))
        divider.setBoxType_(NSBoxSeparator)
        blur_view.addSubview_(divider)

        # Input field using our design system PremiumTextField (Spotlight look, 48px height)
        self.input_field = PremiumTextField.alloc().initWithFrame_(NSMakeRect(20, 270, 460, 48))
        self.input_field.setPlaceholderString_("Enter your idea...")
        self.input_field.setTarget_(self)
        self.input_field.setAction_("handleGenerate:")
        blur_view.addSubview_(self.input_field)

        # Generate button styled with accent neon coloring
        self.generate_btn = PremiumPrimaryButton.alloc().initWithFrame_(NSMakeRect(360, 224, 120, 34))
        self.generate_btn.setTitle_("Generate")
        self.generate_btn.setTarget_(self)
        self.generate_btn.setAction_("handleGenerate:")
        blur_view.addSubview_(self.generate_btn)

        # Spinner
        self.spinner = NSProgressIndicator.alloc().initWithFrame_(NSMakeRect(230, 150, 40, 40))
        self.spinner.setStyle_(NSProgressIndicatorStyleSpinning)
        self.spinner.setHidden_(True)
        blur_view.addSubview_(self.spinner)

        # Status label
        self.status_label = NSTextField.labelWithString_("")
        self.status_label.setFrame_(NSMakeRect(20, 231, 330, 20))
        self.status_label.setFont_(FONT_STATUS)
        self.status_label.setTextColor_(COLOR_TEXT_SECONDARY)
        blur_view.addSubview_(self.status_label)

        # Output scroll view & text container from design system (adjusted size)
        scroll_view = PremiumScrollView.alloc().initWithFrame_(NSMakeRect(20, 64, 460, 146))
        scroll_view.setHidden_(True)

        content_size = scroll_view.contentSize()
        self.output_view = PremiumTextView.alloc().initWithFrame_(
            NSMakeRect(0, 0, content_size.width, content_size.height)
        )
        scroll_view.setDocumentView_(self.output_view)
        blur_view.addSubview_(scroll_view)
        self.scroll_view = scroll_view

        # History button
        self.history_btn = PremiumButton.alloc().initWithFrame_(NSMakeRect(20, 16, 100, 32))
        self.history_btn.setTitle_("History")
        self.history_btn.setTarget_(self)
        self.history_btn.setAction_("handleHistory:")
        blur_view.addSubview_(self.history_btn)

        # Refine button (post-generation operations)
        self.refine_btn = PremiumButton.alloc().initWithFrame_(NSMakeRect(130, 16, 90, 32))
        self.refine_btn.setTitle_("Refine")
        self.refine_btn.setTarget_(self)
        self.refine_btn.setAction_("handleRefineMenu:")
        self.refine_btn.setHidden_(True)
        blur_view.addSubview_(self.refine_btn)

        # Copy button
        self.copy_btn = PremiumButton.alloc().initWithFrame_(NSMakeRect(250, 16, 100, 32))
        self.copy_btn.setTitle_("Copy")
        self.copy_btn.setTarget_(self)
        self.copy_btn.setAction_("handleCopy:")
        self.copy_btn.setHidden_(True)
        blur_view.addSubview_(self.copy_btn)

        # Replace button (Primary)
        self.replace_btn = PremiumPrimaryButton.alloc().initWithFrame_(NSMakeRect(360, 16, 120, 32))
        self.replace_btn.setTitle_("Replace")
        self.replace_btn.setTarget_(self)
        self.replace_btn.setAction_("handleReplace:")
        self.replace_btn.setHidden_(True)
        self.replace_btn.setKeyEquivalent_("\r")
        blur_view.addSubview_(self.replace_btn)

        self.window.setContentView_(blur_view)

    def show_window(self):
        """Position and show window below the status item button."""
        screen_frame = NSScreen.mainScreen().frame()

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
        self.refine_btn.setHidden_(True)

        segment = self.mode_selector.selectedSegment()
        modes = ["general", "image", "code", "creative", "analysis", "music"]
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
        self.refine_btn.setHidden_(False)
        self.refine_btn.setEnabled_(True)
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
        self.refine_btn.setEnabled_(True)
        self.is_generating = False

    def handleCopy_(self, sender):
        """Copy to clipboard."""
        # Grab from the live editable output_view
        self.enhanced_text = self.output_view.string()
        pyperclip.copy(self.enhanced_text)
        self.status_label.setStringValue_("Copied to clipboard!")
        self.window.close()

    def sendPaste_(self, timer):
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
        # Grab from the live editable output_view
        self.enhanced_text = self.output_view.string()
        pyperclip.copy(self.enhanced_text)
        self.window.close()

        # Send paste after a short delay so the window has closed
        # and focus returns to the previous app.
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.15, self, "sendPaste:", None, False
        )

    def handleHistory_(self, sender):
        """Show history."""
        if self.delegate:
            self.window.close()
            AppHelper.callAfter(self.delegate.show_history)

    def handleRefineMenu_(self, sender):
        """Show context menu for quick local AFM prompt refinements."""
        menu = NSMenu.alloc().init()

        item = menu.addItemWithTitle_action_keyEquivalent_("Shorten (Token-Optimize)", "refineShorten:", "")
        item.setTarget_(self)

        item = menu.addItemWithTitle_action_keyEquivalent_("Make Professional", "refineProfessional:", "")
        item.setTarget_(self)

        item = menu.addItemWithTitle_action_keyEquivalent_("Improve Clarity & Grammar", "refineClarity:", "")
        item.setTarget_(self)

        frame = sender.frame()
        menu.popUpMenuPositioningItem_atLocation_inView_(
            None,
            NSMakePoint(frame.origin.x, frame.origin.y - 5),
            sender.superview()
        )

    def refineShorten_(self, sender):
        self._trigger_refinement("Shorten the following text to be ultra-concise, removing fluff while retaining all core requirements. Output only the shortened version, no conversational intro/outro text.")

    def refineProfessional_(self, sender):
        self._trigger_refinement("Rewrite the following text in a highly professional, clear, and technical corporate tone. Output only the rewritten version, no conversational intro/outro text.")

    def refineClarity_(self, sender):
        self._trigger_refinement("Rewrite the following text to maximize clarity, logical flow, and correct any grammatical or spelling mistakes. Output only the improved version, no conversational intro/outro text.")

    def _trigger_refinement(self, instruction):
        """Run a local on-device prompt rewrite/refinement using AFM."""
        current_text = self.output_view.string()
        if not current_text or self.is_generating:
            return

        self.is_generating = True
        self.generate_btn.setEnabled_(False)
        self.refine_btn.setEnabled_(False)
        self.spinner.setHidden_(False)
        self.spinner.startAnimation_(None)
        self.status_label.setStringValue_("Refining prompt...")

        def do_refinement():
            try:
                full_prompt = f"{instruction}\n\nTEXT TO REFINE:\n{current_text}"
                print("Refining text...", flush=True)
                response = self.delegate.engine.generate_response(full_prompt)
                enhanced_text = response.strip()

                if self.delegate.config.redact_sensitive_info:
                    from text2prompt.utils.redactor import redact_text
                    enhanced_text = redact_text(enhanced_text)

                print("Refinement completed!", flush=True)
                AppHelper.callAfter(self.updateOutput_, enhanced_text)
            except Exception as e:
                print("Exception: " + str(e), flush=True)
                AppHelper.callAfter(self.showError_, str(e))

        thread = threading.Thread(target=do_refinement, daemon=True)
        thread.start()

    def handleCloseBtn_(self, sender):
        """Close popover window."""
        self.close()
