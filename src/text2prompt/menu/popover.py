"""Popover window with modern prompt generation UI."""

import objc
import pyperclip
import subprocess
import time
import threading
from AppKit import *
from Foundation import *
from PyObjCTools import AppHelper


class PromptPopover(NSObject):
    """Popover for prompt generation with modern UI."""

    def init(self):
        """Initialize popover."""
        self = super(PromptPopover, self).init()
        if self:
            self.delegate = None
            self.enhanced_text = ""
            self.is_generating = False
            self.current_mode = "general"
            self._build_popover()
        return self

    def setDelegate_(self, delegate):
        """Set the app delegate."""
        self.delegate = delegate

    def _build_popover(self):
        """Build the popover content."""
        # Create popover
        self.popover = NSPopover.alloc().init()
        self.popover.setBehavior_(NSPopoverBehaviorTransient)
        
        # Create content view controller
        content_view = self._create_content_view()
        self.popover.setContentViewController_(content_view)

    def _create_content_view(self):
        """Create the main content view."""
        rect = NSMakeRect(0, 0, 500, 400)
        
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            NSWindowStyleMaskBorderless | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False
        )
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setLevel_(NSFloatingWindowLevel)
        
        # Blur view
        blur_view = NSVisualEffectView.alloc().initWithFrame_(rect)
        blur_view.setMaterial_(NSVisualEffectMaterialPopover)
        blur_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        blur_view.setState_(NSVisualEffectStateActive)
        blur_view.setWantsLayer_(True)
        blur_view.layer().setCornerRadius_(12.0)
        blur_view.layer().setMasksToBounds_(True)
        
        # Title label
        title_label = NSTextField.labelWithString_("text2prompt")
        title_label.setFrame_(NSMakeRect(20, 360, 200, 24))
        title_label.setFont_(NSFont.boldSystemFontOfSize_(16))
        blur_view.addSubview_(title_label)
        
        # Mode selector (segmented control)
        self.mode_selector = NSSegmentedControl.alloc().initWithFrame_(
            NSMakeRect(20, 320, 460, 30)
        )
        self.mode_selector.setSegmentCount_(5)
        self.mode_selector.setLabel_forSegment_("General", 0)
        self.mode_selector.setLabel_forSegment_("Image", 1)
        self.mode_selector.setLabel_forSegment_("Code", 2)
        self.mode_selector.setLabel_forSegment_("Creative", 3)
        self.mode_selector.setLabel_forSegment_("Analysis", 4)
        self.mode_selector.setSelectedSegment_(0)
        blur_view.addSubview_(self.mode_selector)
        
        # Input text field
        self.input_field = NSTextField.alloc().initWithFrame_(
            NSMakeRect(20, 270, 460, 40)
        )
        self.input_field.setPlaceholderString_("Enter your idea...")
        self.input_field.setFont_(NSFont.systemFontOfSize_(14))
        self.input_field.setBordered_(True)
        self.input_field.setBezeled_(True)
        blur_view.addSubview_(self.input_field)
        
        # Generate button
        self.generate_btn = NSButton.alloc().initWithFrame_(
            NSMakeRect(380, 220, 100, 30)
        )
        self.generate_btn.setTitle_("Generate")
        self.generate_btn.setBezelStyle_(NSBezelStyleRounded)
        self.generate_btn.setTarget_(self)
        self.generate_btn.setAction_("handleGenerate:")
        blur_view.addSubview_(self.generate_btn)
        
        # Spinner
        self.spinner = NSProgressIndicator.alloc().initWithFrame_(
            NSMakeRect(230, 150, 40, 40)
        )
        self.spinner.setStyle_(NSProgressIndicatorStyleSpinning)
        self.spinner.setHidden_(True)
        blur_view.addSubview_(self.spinner)
        
        # Status label
        self.status_label = NSTextField.labelWithString_("")
        self.status_label.setFrame_(NSMakeRect(20, 190, 460, 20))
        self.status_label.setFont_(NSFont.systemFontOfSize_(12))
        self.status_label.setTextColor_(NSColor.secondaryLabelColor())
        blur_view.addSubview_(self.status_label)
        
        # Output scroll view
        scroll_view = NSScrollView.alloc().initWithFrame_(
            NSMakeRect(20, 50, 460, 130)
        )
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
        
        # Action buttons
        self.copy_btn = NSButton.alloc().initWithFrame_(
            NSMakeRect(280, 10, 90, 30)
        )
        self.copy_btn.setTitle_("Copy")
        self.copy_btn.setBezelStyle_(NSBezelStyleRounded)
        self.copy_btn.setTarget_(self)
        self.copy_btn.setAction_("handleCopy:")
        self.copy_btn.setHidden_(True)
        blur_view.addSubview_(self.copy_btn)
        
        self.replace_btn = NSButton.alloc().initWithFrame_(
            NSMakeRect(380, 10, 100, 30)
        )
        self.replace_btn.setTitle_("Replace")
        self.replace_btn.setBezelStyle_(NSBezelStyleRounded)
        self.replace_btn.setTarget_(self)
        self.replace_btn.setAction_("handleReplace:")
        self.replace_btn.setHidden_(True)
        self.replace_btn.setKeyEquivalent_("\r")
        blur_view.addSubview_(self.replace_btn)
        
        self.history_btn = NSButton.alloc().initWithFrame_(
            NSMakeRect(20, 10, 100, 30)
        )
        self.history_btn.setTitle_("History")
        self.history_btn.setBezelStyle_(NSBezelStyleRounded)
        self.history_btn.setTarget_(self)
        self.history_btn.setAction_("handleHistory:")
        blur_view.addSubview_(self.history_btn)
        
        self.window.setContentView_(blur_view)
        return self.window

    def show_relative_to_(self, view):
        """Show popover relative to a view."""
        self.popover.showRelativeToRect_ofView_preferredEdge_(
            view.bounds(),
            view,
            NSMinYEdge
        )

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
        self.scroll_view.setHidden_(True)
        self.copy_btn.setHidden_(True)
        self.replace_btn.setHidden_(True)
        
        # Get mode
        segment = self.mode_selector.selectedSegment()
        modes = ["general", "image", "code", "creative", "analysis"]
        self.current_mode = modes[segment]
        
        # Generate in background
        if self.delegate:
            self.delegate.generate_prompt(input_text, self.current_mode, self)

    def updateOutput_(self, text):
        """Update output text (called from delegate)."""
        self.enhanced_text = text
        self.output_view.setString_(text)
        
        # Show output
        self.spinner.stopAnimation_(None)
        self.spinner.setHidden_(True)
        self.scroll_view.setHidden_(False)
        self.copy_btn.setHidden_(False)
        self.replace_btn.setHidden_(False)
        self.status_label.setStringValue_("Prompt generated!")
        self.generate_btn.setEnabled_(True)
        self.is_generating = False

    def showError_(self, error_msg):
        """Show error message."""
        self.spinner.stopAnimation_(None)
        self.spinner.setHidden_(True)
        self.status_label.setStringValue_("Error")
        self.status_label.setTextColor_(NSColor.systemRedColor())
        self.output_view.setString_(error_msg)
        self.scroll_view.setHidden_(False)
        self.generate_btn.setEnabled_(True)
        self.is_generating = False

    def handleCopy_(self, sender):
        """Copy to clipboard."""
        pyperclip.copy(self.enhanced_text)
        self.status_label.setStringValue_("Copied to clipboard!")
        # Close popover after copy
        self.popover.close()

    def handleReplace_(self, sender):
        """Replace selected text."""
        pyperclip.copy(self.enhanced_text)
        self.popover.close()
        time.sleep(0.1)
        
        script = '''
        tell application "System Events"
            keystroke "v" using command down
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Silently fail

    def handleHistory_(self, sender):
        """Show history."""
        if self.delegate:
            self.delegate.show_history()
