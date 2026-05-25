"""Global hotkey support for quick access."""

import objc
from AppKit import *
from Foundation import *


class HotkeyMonitor(NSObject):
    """Monitors keyboard events for hotkey combinations."""

    def init(self):
        """Initialize monitor."""
        self = objc.super(HotkeyMonitor, self).init()
        if self:
            self.delegate = None
        return self

    def setDelegate_(self, delegate):
        """Set delegate to notify on hotkey."""
        self.delegate = delegate

    def monitorEvent_(self, event):
        """Handle keyboard event."""
        if event is None:
            return event

        if (
            event.type() == NSKeyDown
            and event.keyCode() == 49
            and event.modifierFlags() & NSCommandKeyMask
            and event.modifierFlags() & NSShiftKeyMask
        ):
            if self.delegate and hasattr(self.delegate, "on_hotkey_pressed"):
                self.delegate.on_hotkey_pressed()
                return None

        return event


class HotkeyManager(NSObject):
    """Manages global hotkeys using NSEvent monitoring."""

    def init(self):
        """Initialize hotkey manager."""
        self = objc.super(HotkeyManager, self).init()
        if self:
            self.delegate = None
            self.monitor = None
            self.local_monitor = None
            self._monitor_obj = None
        return self

    def setDelegate_(self, delegate):
        """Set the delegate to notify on hotkey press."""
        self.delegate = delegate

    def start_monitoring(self):
        """Start monitoring for global hotkeys."""
        self._monitor_obj = HotkeyMonitor.alloc().init()
        self._monitor_obj.setDelegate_(self.delegate)

        self.monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
            NSKeyDownMask, self._monitor_obj.monitorEvent_
        )

        self.local_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            NSKeyDownMask, self._monitor_obj.monitorEvent_
        )

    def stop_monitoring(self):
        """Stop monitoring for global hotkeys."""
        if self.monitor:
            NSEvent.removeMonitor_(self.monitor)
            self.monitor = None
        if self.local_monitor:
            NSEvent.removeMonitor_(self.local_monitor)
            self.local_monitor = None
