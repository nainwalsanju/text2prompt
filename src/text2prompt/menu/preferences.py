"""Preferences panel for app configuration."""

import objc
from AppKit import *
from Foundation import *

from text2prompt.config import get_config, save_config


class PreferencesWindow(NSObject):
    """Window for app preferences."""

    def init(self):
        """Initialize preferences window."""
        self = objc.super(PreferencesWindow, self).init()
        if self:
            self.config = None
            self._build_window()
        return self

    def _build_window(self):
        """Build the preferences window UI."""
        rect = NSMakeRect(0, 0, 400, 350)

        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setTitle_("Preferences")
        self.window.setMinSize_(NSSize(400, 350))
        self.window.setResizable_(False)

        # Content view
        content_view = NSView.alloc().initWithFrame_(rect)

        # Default mode
        mode_label = NSTextField.labelWithString_("Default Mode:")
        mode_label.setFrame_(NSMakeRect(20, 300, 120, 20))
        mode_label.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(mode_label)

        self.mode_popup = NSPopUpButton.alloc().initWithFrame_pullsDown_(
            NSMakeRect(150, 295, 200, 26), False
        )
        for mode in ["General", "Image", "Code", "Creative", "Analysis"]:
            self.mode_popup.addItemWithTitle_(mode)
        content_view.addSubview_(self.mode_popup)

        # Auto-copy to clipboard
        self.autocopy_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 260, 300, 20))
        self.autocopy_checkbox.setButtonType_(NSSwitchButton)
        self.autocopy_checkbox.setTitle_("Auto-copy to clipboard after generation")
        self.autocopy_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.autocopy_checkbox)

        # Include app context
        self.context_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 230, 300, 20))
        self.context_checkbox.setButtonType_(NSSwitchButton)
        self.context_checkbox.setTitle_("Include active app context in prompts")
        self.context_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.context_checkbox)

        # Save history
        self.history_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 200, 300, 20))
        self.history_checkbox.setButtonType_(NSSwitchButton)
        self.history_checkbox.setTitle_("Save prompt history")
        self.history_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.history_checkbox)

        # Launch at login
        self.login_checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(20, 170, 300, 20))
        self.login_checkbox.setButtonType_(NSSwitchButton)
        self.login_checkbox.setTitle_("Launch at login")
        self.login_checkbox.setFont_(NSFont.systemFontOfSize_(13))
        content_view.addSubview_(self.login_checkbox)

        # Save button
        self.save_btn = NSButton.alloc().initWithFrame_(NSMakeRect(280, 20, 100, 30))
        self.save_btn.setTitle_("Save")
        self.save_btn.setBezelStyle_(NSBezelStyleRounded)
        self.save_btn.setTarget_(self)
        self.save_btn.setAction_("savePreferences:")
        content_view.addSubview_(self.save_btn)

        # Cancel button
        self.cancel_btn = NSButton.alloc().initWithFrame_(NSMakeRect(170, 20, 100, 30))
        self.cancel_btn.setTitle_("Cancel")
        self.cancel_btn.setBezelStyle_(NSBezelStyleRounded)
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

        # Set mode
        modes = ["general", "image", "code", "creative", "analysis"]
        default_mode = self.config.default_mode
        if default_mode in modes:
            self.mode_popup.selectItemWithTitle_(default_mode.capitalize())

        # Set checkboxes
        self.autocopy_checkbox.setState_(NSOnState if self.config.auto_copy else NSOffState)
        self.context_checkbox.setState_(NSOnState if self.config.include_context else NSOffState)
        self.history_checkbox.setState_(NSOnState if self.config.save_history else NSOffState)
        self.login_checkbox.setState_(NSOnState if self.config.launch_at_login else NSOffState)

    def savePreferences_(self, sender):
        """Save preferences."""
        if self.config is None:
            return

        # Get mode
        mode_title = self.mode_popup.titleOfSelectedItem()
        modes = ["general", "image", "code", "creative", "analysis"]
        mode_map = {m.capitalize(): m for m in modes}
        self.config.default_mode = mode_map.get(mode_title, "general")

        # Get checkboxes
        self.config.auto_copy = self.autocopy_checkbox.state() == NSOnState
        self.config.include_context = self.context_checkbox.state() == NSOnState
        self.config.save_history = self.history_checkbox.state() == NSOnState
        self.config.launch_at_login = self.login_checkbox.state() == NSOnState

        # Save
        save_config(self.config)

        # Handle launch at login
        self._update_login_item(self.config.launch_at_login)

        # Close window
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
                delete login item "{2}"
            end if
        end tell
        """.format("true" if enabled else "false", "/Applications/text2prompt.app", "text2prompt")

        try:
            import subprocess

            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        except Exception:
            pass  # Silently fail if permission denied
