"""History browser window for viewing past prompts."""

import objc
import pyperclip
from AppKit import *
from Foundation import *


class HistoryWindow(NSObject):
    """Window displaying prompt history."""

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
        """Build the history window UI."""
        rect = NSMakeRect(0, 0, 600, 500)

        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            NSWindowStyleMaskTitled
            | NSWindowStyleMaskClosable
            | NSWindowStyleMaskResizable
            | NSWindowStyleMaskMiniaturizable,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setTitle_("Prompt History")
        self.window.setMinSize_(NSSize(400, 300))

        # Content view
        content_view = NSView.alloc().initWithFrame_(rect)

        # Table view for history
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 40, 600, 460))
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setHasHorizontalScroller_(False)
        scroll_view.setBorderType_(NSNoBorder)

        self.table_view = NSTableView.alloc().initWithFrame_(NSMakeRect(0, 0, 600, 460))
        self.table_view.setUsesAlternatingRowBackgroundColors_(True)
        self.table_view.setGridStyleMask_(NSTableViewGridSolidHorizontal)

        # Columns
        col1 = NSTableColumn.alloc().initWithIdentifier_("date")
        col1.setHeaderCell_(NSTableCellCell.alloc().initWithTextCell_("Date"))
        col1.setWidth_(120)
        self.table_view.addTableColumn_(col1)

        col2 = NSTableColumn.alloc().initWithIdentifier_("mode")
        col2.setHeaderCell_(NSTableCellCell.alloc().initWithTextCell_("Mode"))
        col2.setWidth_(80)
        self.table_view.addTableColumn_(col2)

        col3 = NSTableColumn.alloc().initWithIdentifier_("input")
        col3.setHeaderCell_(NSTableCellCell.alloc().initWithTextCell_("Input"))
        col3.setWidth_(200)
        self.table_view.addTableColumn_(col3)

        col4 = NSTableColumn.alloc().initWithIdentifier_("output")
        col4.setHeaderCell_(NSTableCellCell.alloc().initWithTextCell_("Output"))
        col4.setWidth_(200)
        self.table_view.addTableColumn_(col4)

        self.table_view.setDelegate_(self)
        self.table_view.setDataSource_(self)
        scroll_view.setDocumentView_(self.table_view)
        content_view.addSubview_(scroll_view)

        # Bottom bar
        self.copy_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 5, 100, 30))
        self.copy_btn.setTitle_("Copy")
        self.copy_btn.setBezelStyle_(NSBezelStyleRounded)
        self.copy_btn.setTarget_(self)
        self.copy_btn.setAction_("copySelected:")
        content_view.addSubview_(self.copy_btn)

        self.clear_btn = NSButton.alloc().initWithFrame_(NSMakeRect(480, 5, 100, 30))
        self.clear_btn.setTitle_("Clear All")
        self.clear_btn.setBezelStyle_(NSBezelStyleRounded)
        self.clear_btn.setTarget_(self)
        self.clear_btn.setAction_("clearAll:")
        content_view.addSubview_(self.clear_btn)

        self.window.setContentView_(content_view)

    def show(self):
        """Show the history window."""
        self._load_history()
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def _load_history(self):
        """Load history from database."""
        if self.conn is None:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT context_id, input_text, output_text, created_at FROM interactions ORDER BY created_at DESC"
            )
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
        col_id = table_column.identifier()

        if col_id == "date":
            text = item[3][:19] if item[3] else ""
        elif col_id == "mode":
            context = item[0]
            mode = context.split(":")[-1] if ":" in context else context
            text = mode.capitalize()
        elif col_id == "input":
            text = (item[1][:50] + "...") if len(item[1]) > 50 else item[1]
        elif col_id == "output":
            text = (item[2][:50] + "...") if len(item[2]) > 50 else item[2]
        else:
            text = ""

        cell = NSTextField.alloc().initWithString_(text)
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

        output = self.history_data[row][2]
        pyperclip.copy(output)

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
                cursor.execute("DELETE FROM interactions")
                self.conn.commit()
                self._load_history()
            except Exception as e:
                print(f"Error clearing history: {e}")
