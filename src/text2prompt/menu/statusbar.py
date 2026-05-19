"""Menu bar status item and application menu."""

import objc
from AppKit import *
from Foundation import *


class StatusBarApp(NSObject):
    """Manages the menu bar status item and application menu."""

    def init(self):
        """Initialize status bar."""
        self = super(StatusBarApp, self).init()
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
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        
        # Use system icon
        self.status_item.button().setImage_(
            NSImage.imageWithSystemSymbolName_accessDescription_(
                "sparkles", None
            )
        )
        
        self.status_item.setToolTip_("text2prompt - AI Prompt Builder")
        self.status_item.setTarget_(self)
        self.status_item.setAction_("handleStatusItemClick:")

    def handleStatusItemClick_(self, sender):
        """Handle status item click."""
        event = NSApp.currentEvent()
        
        if event.type() == NSLeftMouseDown:
            self._show_popover()
        elif event.type() == NSRightMouseDown:
            self.menu.popUpMenuPositioningItem_atLocation_inView_(
                None,
                NSEvent.mouseLocation(),
                None
            )

    def _setup_menu(self):
        """Create the right-click menu."""
        self.menu = NSMenu.alloc().init()
        
        # Generate Prompt
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Generate Prompt", "generatePrompt:", ""
        )
        item.setTarget_(self)
        self.menu.addItem_(item)
        
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        # History
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Prompt History", "showHistory:", ""
        )
        item.setTarget_(self)
        self.menu.addItem_(item)
        
        # Preferences
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Preferences", "showPreferences:", ",")
        item.setTarget_(self)
        self.menu.addItem_(item)
        
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        # Quit
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "terminate:", "q")
        item.setTarget_(NSApp)
        self.menu.addItem_(item)
        
        self.status_item.setMenu_(self.menu)

    def _show_popover(self):
        """Show the popover window."""
        if self.popover is None:
            from text2prompt.menu.popover import PromptPopover
            self.popover = PromptPopover.alloc().init()
            self.popover.setDelegate_(self.delegate)
        
        self.popover.show_relative_to_(self.status_item.button())

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
