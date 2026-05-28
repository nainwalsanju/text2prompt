"""Menu bar status item and application menu."""

import objc
from AppKit import *
from Foundation import *


class StatusBarApp(NSObject):
    """Manages the menu bar status item and application menu."""

    def init(self):
        """Initialize status bar."""
        self = objc.super(StatusBarApp, self).init()
        if self:
            self.status_item = None
            self.menu = None
            self.popover = None
            self.delegate = None
            self._setup_status_item()
            self._setup_menu()
        return self

    def setDelegate_(self, delegate):
        """Set the app delegate."""
        self.delegate = delegate

    def _setup_status_item(self):
        """Create the status bar item."""
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )

        self.status_item.button().setTitle_("✦")
        self.status_item.button().setFont_(NSFont.systemFontOfSize_weight_(16, NSFontWeightMedium))

        self.status_item.setToolTip_("text2prompt - AI Prompt Builder")

        # Use a custom handler to distinguish left and right clicks.
        self._click_handler = StatusItemHandler.alloc().initWithStatusBar_(self)
        self.status_item.button().setTarget_(self._click_handler)
        self.status_item.button().setAction_("handleClick:")
        self.status_item.button().sendActionOn_(
            (1 << NSEventTypeLeftMouseUp) | (1 << NSEventTypeRightMouseUp)
        )

    def _setup_menu(self):
        """Create the context menu."""
        self.menu = NSMenu.alloc().init()

        item = self.menu.addItemWithTitle_action_keyEquivalent_(
            "Generate Prompt", "generatePrompt:", ""
        )
        item.setTarget_(self)

        self.menu.addItem_(NSMenuItem.separatorItem())

        item = self.menu.addItemWithTitle_action_keyEquivalent_(
            "Prompt History", "showHistory:", ""
        )
        item.setTarget_(self)

        item = self.menu.addItemWithTitle_action_keyEquivalent_(
            "Preferences", "showPreferences:", ","
        )
        item.setTarget_(self)

        self.menu.addItem_(NSMenuItem.separatorItem())

        item = self.menu.addItemWithTitle_action_keyEquivalent_("Quit", "terminate:", "q")
        item.setTarget_(NSApp)

    def _show_popover(self):
        """Show or toggle the prompt window popover."""
        print("[StatusBarApp] _show_popover called", flush=True)
        try:
            if self.popover is None:
                print("[StatusBarApp] Creating popover...", flush=True)
                from text2prompt.menu.popover import PromptWindow

                self.popover = PromptWindow.alloc().init()
                self.popover.setDelegate_(self.delegate)
                print("[StatusBarApp] Popover created successfully.", flush=True)

            print(f"[StatusBarApp] popover.window.isVisible(): {self.popover.window.isVisible()}, isKeyWindow: {self.popover.window.isKeyWindow()}", flush=True)
            if self.popover.window.isVisible() and self.popover.window.isKeyWindow():
                print("[StatusBarApp] Closing popover", flush=True)
                self.popover.close()
            else:
                print("[StatusBarApp] Showing popover window", flush=True)
                self.popover.show_window()
        except Exception as e:
            print(f"[StatusBarApp] Exception in _show_popover: {e}", flush=True)


    def generatePrompt_(self, sender):
        """Menu action: generate prompt."""
        from PyObjCTools import AppHelper
        AppHelper.callAfter(self._show_popover)

    def showHistory_(self, sender):
        """Menu action: show history."""
        if self.delegate:
            from PyObjCTools import AppHelper
            AppHelper.callAfter(self.delegate.show_history)

    def showPreferences_(self, sender):
        """Menu action: show preferences."""
        if self.delegate:
            from PyObjCTools import AppHelper
            AppHelper.callAfter(self.delegate.show_preferences)


class StatusItemHandler(NSObject):
    """Handles clicks on the status bar button."""

    def initWithStatusBar_(self, status_bar):
        """Initialize with reference to status bar."""
        self = objc.super(StatusItemHandler, self).init()
        if self:
            self.status_bar = status_bar
        return self

    def handleClick_(self, sender):
        """Handle click - check event type to distinguish left vs right."""
        print("[StatusItemHandler] handleClick_ entered", flush=True)
        event = NSApp.currentEvent()
        print(f"[StatusItemHandler] currentEvent: {event}", flush=True)
        is_right = False
        if event is not None:
            type_ = event.type()
            print(f"[StatusItemHandler] event type: {type_}", flush=True)
            if type_ in (NSEventTypeRightMouseUp, NSEventTypeRightMouseDown):
                is_right = True
            elif type_ in (NSEventTypeLeftMouseUp, NSEventTypeLeftMouseDown) and (
                event.modifierFlags() & NSEventModifierFlagControl
            ):
                is_right = True

        print(f"[StatusItemHandler] is_right: {is_right}", flush=True)
        if is_right:
            print("[StatusItemHandler] Showing status item menu", flush=True)
            self.status_bar.status_item.popUpStatusItemMenu_(self.status_bar.menu)
        else:
            print("[StatusItemHandler] Directing to _show_popover", flush=True)
            self.status_bar._show_popover()


