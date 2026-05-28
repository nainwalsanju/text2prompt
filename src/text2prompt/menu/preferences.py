"""Preferences panel for app configuration."""

import objc
from AppKit import *
from Foundation import *

from text2prompt.config import get_config, save_config
from text2prompt.ui.styles import (
    APPEARANCE_DARK_AQUA,
)
from text2prompt.ui.components import (
    PremiumScrollView,
    PremiumTextView,
    PremiumButton,
    PremiumPrimaryButton,
)


class PreferencesWindow(NSObject):
    """Window for app preferences with custom rules editor and privacy controls."""

    def init(self):
        """Initialize preferences window."""
        self = objc.super(PreferencesWindow, self).init()
        if self:
            self.config = None
            self.temp_rules = {}
            self.last_selected_segment = 0
            self._build_window()
        return self

    def _build_window(self):
        """Build the preferences window UI."""
        rect = NSMakeRect(0, 0, 500, 500)

        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setReleasedWhenClosed_(False)
        self.window.setAppearance_(NSAppearance.appearanceNamed_(APPEARANCE_DARK_AQUA))
        self.window.setTitle_("Preferences")
        self.window.setMinSize_(NSSize(500, 500))

        # Content view
        content_view = NSView.alloc().initWithFrame_(rect)

        # Default mode label and pop-up
        mode_label = NSTextField.labelWithString_("Default Mode:")
        mode_label.setFrame_(NSMakeRect(20, 455, 120, 20))
        mode_label.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(mode_label)

        self.mode_popup = NSPopUpButton.alloc().initWithFrame_pullsDown_(
            NSMakeRect(150, 450, 200, 26), False
        )
        for mode in ["General", "Image", "Code", "Creative", "Analysis", "Music"]:
            self.mode_popup.addItemWithTitle_(mode)
        content_view.addSubview_(self.mode_popup)

        # Base checkboxes
        self.autocopy_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 415, 460, 20))
        self.autocopy_checkbox.setButtonType_(NSSwitchButton)
        self.autocopy_checkbox.setTitle_("Auto-copy to clipboard after generation")
        self.autocopy_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.autocopy_checkbox)

        self.context_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 385, 460, 20))
        self.context_checkbox.setButtonType_(NSSwitchButton)
        self.context_checkbox.setTitle_("Include active app context in prompts")
        self.context_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.context_checkbox)

        self.history_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 355, 460, 20))
        self.history_checkbox.setButtonType_(NSSwitchButton)
        self.history_checkbox.setTitle_("Save prompt history")
        self.history_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.history_checkbox)

        self.login_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 325, 460, 20))
        self.login_checkbox.setButtonType_(NSSwitchButton)
        self.login_checkbox.setTitle_("Launch at login")
        self.login_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.login_checkbox)

        self.redact_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 295, 460, 20))
        self.redact_checkbox.setButtonType_(NSSwitchButton)
        self.redact_checkbox.setTitle_("Redact sensitive data (API keys, emails, secrets)")
        self.redact_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.redact_checkbox)

        # Divider line
        divider = NSBox.alloc().initWithFrame_(NSMakeRect(20, 275, 460, 2))
        divider.setBoxType_(NSBoxSeparator)
        content_view.addSubview_(divider)

        # Custom rules header
        rules_label = NSTextField.labelWithString_("Custom Prompt Guidelines per Mode:")
        rules_label.setFrame_(NSMakeRect(20, 245, 400, 20))
        rules_label.setFont_(NSFont.boldSystemFontOfSize_(13))
        content_view.addSubview_(rules_label)

        # Custom rules mode selector segment bar (flat round rect style)
        self.rules_mode_selector = NSSegmentedControl.alloc().initWithFrame_(
            NSMakeRect(20, 212, 460, 26)
        )
        self.rules_mode_selector.setSegmentCount_(6)
        self.rules_mode_selector.setSegmentStyle_(NSSegmentStyleRoundRect)
        self.rules_mode_selector.setLabel_forSegment_("General", 0)
        self.rules_mode_selector.setLabel_forSegment_("Image", 1)
        self.rules_mode_selector.setLabel_forSegment_("Code", 2)
        self.rules_mode_selector.setLabel_forSegment_("Creative", 3)
        self.rules_mode_selector.setLabel_forSegment_("Analysis", 4)
        self.rules_mode_selector.setLabel_forSegment_("Music", 5)
        self.rules_mode_selector.setSelectedSegment_(0)
        self.rules_mode_selector.setTarget_(self)
        self.rules_mode_selector.setAction_("modeChanged:")
        content_view.addSubview_(self.rules_mode_selector)

        # Custom rules editor (scrollable multiline NSTextView) using Design System
        scroll_view = PremiumScrollView.alloc().initWithFrame_(NSMakeRect(20, 70, 460, 130))

        content_size = scroll_view.contentSize()
        self.rules_text_view = PremiumTextView.alloc().initWithFrame_(
            NSMakeRect(0, 0, content_size.width, content_size.height)
        )
        scroll_view.setDocumentView_(self.rules_text_view)
        content_view.addSubview_(scroll_view)

        # Save button (Primary neon styled, aligned at 32px height)
        self.save_btn = PremiumPrimaryButton.alloc().initWithFrame_(NSMakeRect(370, 16, 110, 32))
        self.save_btn.setTitle_("Save")
        self.save_btn.setTarget_(self)
        self.save_btn.setAction_("savePreferences:")
        content_view.addSubview_(self.save_btn)

        # Cancel button (Secondary styled, aligned at 32px height)
        self.cancel_btn = PremiumButton.alloc().initWithFrame_(NSMakeRect(250, 16, 110, 32))
        self.cancel_btn.setTitle_("Cancel")
        self.cancel_btn.setTarget_(self)
        self.cancel_btn.setAction_("cancel:")
        content_view.addSubview_(self.cancel_btn)

        self.window.setContentView_(content_view)

    def show(self):
        """Show the preferences window."""
        self._load_preferences()
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def _load_preferences(self):
        """Load current preferences into UI."""
        self.config = get_config()

        # Set default mode dropdown
        modes = ["general", "image", "code", "creative", "analysis", "music"]
        default_mode = self.config.default_mode
        if default_mode in modes:
            self.mode_popup.selectItemWithTitle_(default_mode.capitalize())

        # Set checkboxes
        self.autocopy_checkbox.setState_(
            NSControlStateValueOn if self.config.auto_copy else NSControlStateValueOff
        )
        self.context_checkbox.setState_(
            NSControlStateValueOn if self.config.include_context else NSControlStateValueOff
        )
        self.history_checkbox.setState_(
            NSControlStateValueOn if self.config.save_history else NSControlStateValueOff
        )
        self.login_checkbox.setState_(
            NSControlStateValueOn if self.config.launch_at_login else NSControlStateValueOff
        )
        self.redact_checkbox.setState_(
            NSControlStateValueOn if self.config.redact_sensitive_info else NSControlStateValueOff
        )

        # Load guidelines cache
        self.temp_rules = dict(self.config.custom_rules or {})
        self.last_selected_segment = 0
        self.rules_mode_selector.setSelectedSegment_(0)
        self.rules_text_view.setString_(self.temp_rules.get("general", ""))

    def modeChanged_(self, sender):
        """Handle segment index switch in custom rules selector."""
        # 1. Save guidelines of the old segment to the temp dict
        old_segment = self.last_selected_segment
        modes = ["general", "image", "code", "creative", "analysis", "music"]
        old_mode = modes[old_segment]
        current_text = self.rules_text_view.string()
        self.temp_rules[old_mode] = current_text

        # 2. Update to new segment
        new_segment = sender.selectedSegment()
        self.last_selected_segment = new_segment
        new_mode = modes[new_segment]

        # 3. Load rules of the new segment to editor
        new_text = self.temp_rules.get(new_mode, "")
        self.rules_text_view.setString_(new_text)

    def savePreferences_(self, sender):
        """Save preference configurations."""
        if self.config is None:
            return

        # 1. Cache the guidelines of the active tab segment
        active_segment = self.rules_mode_selector.selectedSegment()
        modes = ["general", "image", "code", "creative", "analysis", "music"]
        active_mode = modes[active_segment]
        self.temp_rules[active_mode] = self.rules_text_view.string()

        # 2. Map default mode pop-up selection
        mode_title = self.mode_popup.titleOfSelectedItem()
        mode_map = {m.capitalize(): m for m in modes}
        self.config.default_mode = mode_map.get(mode_title, "general")

        # 3. Update checkbox configs
        self.config.auto_copy = self.autocopy_checkbox.state() == NSControlStateValueOn
        self.config.include_context = self.context_checkbox.state() == NSControlStateValueOn
        self.config.save_history = self.history_checkbox.state() == NSControlStateValueOn
        self.config.launch_at_login = self.login_checkbox.state() == NSControlStateValueOn
        self.config.redact_sensitive_info = self.redact_checkbox.state() == NSControlStateValueOn

        # 4. Save rules dictionary
        self.config.custom_rules = self.temp_rules

        # 5. Persist to file and update macOS system components
        save_config(self.config)
        self._update_login_item(self.config.launch_at_login)

        # 6. Close Preferences view
        self.window.close()

    def cancel_(self, sender):
        """Cancel and close."""
        self.window.close()

    def _update_login_item(self, enabled):
        """Update launch at login setting."""
        script = """
        tell application "System Events"
            set loginItems to get every login item
            set appName to "text2prompt"
            set found to false
            repeat with anItem in loginItems
                if name of anItem contains appName then
                    set found to true
                    exit repeat
                end if
            end repeat
            if {0} and not found then
                make login item at end with properties {{path:"{1}", hidden:false}}
            else if not {0} and found then
                repeat with anItem in loginItems
                    if name of anItem contains appName then
                        delete anItem
                        exit repeat
                    end if
                end repeat
            end if
        end tell
        """.format("true" if enabled else "false", "/Applications/text2prompt.app")

        try:
            import subprocess

            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        except (subprocess.CalledProcessError, OSError):
            pass
