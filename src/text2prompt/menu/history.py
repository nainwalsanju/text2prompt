"""History browser window for viewing past prompts."""

import objc
import pyperclip
from AppKit import *
from Foundation import *

from text2prompt.app import MODE_SEPARATOR
from text2prompt.ui.styles import (
    APPEARANCE_DARK_AQUA,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_TITLE,
)
from text2prompt.ui.components import (
    PremiumFrostedGlassView,
    PremiumScrollView,
    PremiumButton,
    PremiumPrimaryButton,
    PremiumWindow,
)


class KeyHistoryWindow(PremiumWindow):
    """Custom NSWindow subclass to allow borderless windows to receive keyboard focus."""
    pass


class HistoryWindow(NSObject):
    """Frosted-glass window displaying prompt history."""

    def init(self):
        """Initialize history window."""
        self = objc.super(HistoryWindow, self).init()
        if self:
            self.conn = None
            self.history_data = []
            self._build_window()
        return self

    def setConnection_(self, conn):
        """Set database connection."""
        self.conn = conn

    def _build_window(self):
        """Build the borderless glassmorphism history window UI."""
        rect = NSMakeRect(0, 0, 700, 500)

        # Style mask matches borderless popover
        self.window = KeyHistoryWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setReleasedWhenClosed_(False)
        self.window.setAppearance_(NSAppearance.appearanceNamed_(APPEARANCE_DARK_AQUA))
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setHasShadow_(True)
        self.window.setMovableByWindowBackground_(True)

        # Frosted glass background using Design System component
        blur_view = PremiumFrostedGlassView.alloc().initWithFrame_(rect)

        # Title
        title_label = NSTextField.labelWithString_("Prompt History")
        title_label.setFrame_(NSMakeRect(24, 452, 300, 28))
        title_label.setFont_(NSFont.boldSystemFontOfSize_(20))
        title_label.setTextColor_(COLOR_TEXT_PRIMARY)
        blur_view.addSubview_(title_label)

        # Table scroll view using Design System components
        scroll_view = PremiumScrollView.alloc().initWithFrame_(NSMakeRect(20, 64, 660, 372))

        self.table_view = NSTableView.alloc().initWithFrame_(NSMakeRect(0, 0, 660, 372))
        self.table_view.setUsesAlternatingRowBackgroundColors_(True)
        self.table_view.setGridStyleMask_(NSTableViewGridSolidHorizontal)
        self.table_view.setBackgroundColor_(NSColor.clearColor())
        self.table_view.setRowHeight_(40)

        # Table columns
        col_date = NSTableColumn.alloc().initWithIdentifier_("date")
        col_date.setHeaderCell_(NSTableHeaderCell.alloc().initWithTextCell_("Date"))
        col_date.setWidth_(110)
        self.table_view.addTableColumn_(col_date)

        col_mode = NSTableColumn.alloc().initWithIdentifier_("mode")
        col_mode.setHeaderCell_(NSTableHeaderCell.alloc().initWithTextCell_("Mode"))
        col_mode.setWidth_(80)
        self.table_view.addTableColumn_(col_mode)

        col_input = NSTableColumn.alloc().initWithIdentifier_("input")
        col_input.setHeaderCell_(NSTableHeaderCell.alloc().initWithTextCell_("Input"))
        col_input.setWidth_(220)
        self.table_view.addTableColumn_(col_input)

        col_output = NSTableColumn.alloc().initWithIdentifier_("output")
        col_output.setHeaderCell_(NSTableHeaderCell.alloc().initWithTextCell_("Output"))
        col_output.setWidth_(220)
        self.table_view.addTableColumn_(col_output)

        self.table_view.setDelegate_(self)
        self.table_view.setDataSource_(self)
        scroll_view.setDocumentView_(self.table_view)
        blur_view.addSubview_(scroll_view)

        # Clear All button
        self.clear_btn = PremiumButton.alloc().initWithFrame_(NSMakeRect(20, 16, 100, 32))
        self.clear_btn.setTitle_("Clear All")
        self.clear_btn.setTarget_(self)
        self.clear_btn.setAction_("clearAll:")
        blur_view.addSubview_(self.clear_btn)

        # Close button
        self.close_btn = PremiumButton.alloc().initWithFrame_(NSMakeRect(580, 16, 100, 32))
        self.close_btn.setTitle_("Close")
        self.close_btn.setTarget_(self)
        self.close_btn.setAction_("close:")
        blur_view.addSubview_(self.close_btn)

        # Copy Selected button styled as glowing accent Primary Button
        self.copy_btn = PremiumPrimaryButton.alloc().initWithFrame_(NSMakeRect(450, 16, 120, 32))
        self.copy_btn.setTitle_("Copy Selected")
        self.copy_btn.setTarget_(self)
        self.copy_btn.setAction_("copySelected:")
        blur_view.addSubview_(self.copy_btn)

        self.window.setContentView_(blur_view)

    def show(self):
        """Show the history window."""
        self._load_history()
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def close_(self, sender):
        """Close history window."""
        self.window.close()

    def _load_history(self):
        """Load history from database, pairing user inputs with assistant outputs."""
        if self.conn is None:
            return

        try:
            cursor = self.conn.cursor()
            # Pair each user row with the next assistant row (same context_id, next id).
            cursor.execute("""
                SELECT u.context_id, u.content, a.content, u.timestamp
                FROM chat_history u
                LEFT JOIN chat_history a
                    ON a.context_id = u.context_id
                    AND a.role = 'assistant'
                    AND a.id = (
                        SELECT MIN(id) FROM chat_history
                        WHERE context_id = u.context_id
                          AND role = 'assistant'
                          AND id > u.id
                    )
                WHERE u.role = 'user'
                ORDER BY u.timestamp DESC
            """)
            self.history_data = cursor.fetchall()
        except Exception:
            self.history_data = []

        self.table_view.reloadData()

    def numberOfRowsInTableView_(self, table_view):
        """Return number of rows."""
        return len(self.history_data)

    def tableView_viewForTableColumn_row_(self, table_view, table_column, row):
        """Create cell view for table row."""
        if row >= len(self.history_data):
            return None

        item = self.history_data[row]
        # item = (context_id, user_content, assistant_content, timestamp)
        col_id = table_column.identifier()

        if col_id == "date":
            text = item[3][:19] if item[3] else ""
        elif col_id == "mode":
            context = item[0]
            # context_id uses ``|`` as separator: "prefix|mode"
            mode = context.rsplit(MODE_SEPARATOR, 1)[-1] if MODE_SEPARATOR in context else context
            text = mode.capitalize()
        elif col_id == "input":
            content = item[1] or ""
            text = (content[:50] + "...") if len(content) > 50 else content
        elif col_id == "output":
            content = item[2] or ""
            text = (content[:50] + "...") if len(content) > 50 else content
        else:
            text = ""

        cell = NSTextField.labelWithString_(text)
        cell.setEditable_(False)
        cell.setBordered_(False)
        cell.setDrawsBackground_(False)
        cell.setFont_(NSFont.systemFontOfSize_(12))

        return cell

    def copySelected_(self, sender):
        """Copy selected row's output to clipboard."""
        row = self.table_view.selectedRow()
        if row < 0 or row >= len(self.history_data):
            return

        # Prefer copying the assistant output; fall back to user input
        output = self.history_data[row][2]
        content = output if output else self.history_data[row][1]
        if content:
            pyperclip.copy(content)

    def clearAll_(self, sender):
        """Clear all history."""
        if self.conn is None:
            return

        alert = NSAlert.alloc().init()
        alert.setMessageText_("Clear All History?")
        alert.setInformativeText_("This action cannot be undone.")
        alert.addButtonWithTitle_("Clear")
        alert.addButtonWithTitle_("Cancel")
        alert.setAlertStyle_(NSAlertStyleWarning)

        response = alert.runModal()
        if response == NSAlertFirstButtonReturn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM chat_history")
                self.conn.commit()
                self._load_history()
            except Exception as e:
                print(f"Error clearing history: {e}")
