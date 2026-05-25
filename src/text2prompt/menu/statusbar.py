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
        self.status_item.setHighlightMode_(True)

        # Use a custom handler to distinguish left and right clicks.
        self._click_handler = StatusItemHandler.alloc().initWithStatusBar_(self)
        self.status_item.button().setTarget_(self._click_handler)
        self.status_item.button().setAction_("handleClick:")

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
        """Show the prompt window."""
        if self.popover is None:
            from text2prompt.menu.popover import PromptWindow

            self.popover = PromptWindow.alloc().init()
            self.popover.setDelegate_(self.delegate)

        self.popover.show_window()

    def generatePrompt_(self, sender):
        """Menu action: generate prompt."""
        self._show_popover()

    def showHistory_(self, sender):
        """Menu action: show history."""
        if self.delegate:
            self.delegate.show_history()

    def showPreferences_(self, sender):
        """Menu action: show preferences."""
        if self.delegate:
            self.delegate.show_preferences()


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
        event = NSApp.currentEvent()
        if event is not None:
            if event.type() == NSEventTypeLeftMouseDown:
                self.status_bar._show_popover()
            elif event.type() == NSEventTypeRightMouseDown:
                self.status_bar.menu.popUpMenuPositioningItem_atLocation_inView_(
                    None, NSEvent.mouseLocation(), None
                )
