"""Premium reusable AppKit component subclasses for native macOS Dark-Glass UI."""

import objc
from AppKit import *
from Foundation import *


class PremiumWindow(NSWindow):
    """Custom NSWindow that supports keyboard focus (for borderless windows)
    and automatic routing of standard Command shortcuts (Copy, Paste, Undo, etc.)
    which are usually missing in accessory menu bar apps.
    """

    def canBecomeKeyWindow(self):
        return True

    def performKeyEquivalent_(self, event):
        if event.type() == NSEventTypeKeyDown:
            flags = event.modifierFlags()
            if flags & NSEventModifierFlagCommand:
                key = event.charactersIgnoringModifiers()
                responder = self.firstResponder()
                if responder:
                    if key == "v":
                        if responder.tryToPerform_with_("paste:", None):
                            return True
                    elif key == "c":
                        if responder.tryToPerform_with_("copy:", None):
                            return True
                    elif key == "x":
                        if responder.tryToPerform_with_("cut:", None):
                            return True
                    elif key == "a":
                        if responder.tryToPerform_with_("selectAll:", None):
                            return True
                    elif key == "z":
                        if flags & NSEventModifierFlagShift:
                            if responder.tryToPerform_with_("redo:", None):
                                return True
                        else:
                            if responder.tryToPerform_with_("undo:", None):
                                return True
        return objc.super(PremiumWindow, self).performKeyEquivalent_(event)


class PremiumFrostedGlassView(NSVisualEffectView):
    """Custom NSVisualEffectView that applies Dark vibrant frosted glass."""

    def initWithFrame_(self, frame):
        self = objc.super(PremiumFrostedGlassView, self).initWithFrame_(frame)
        if self:
            from text2prompt.ui.styles import BACKDROP_MATERIAL, WINDOW_CORNER_RADIUS, COLOR_BORDER_LIGHT
            self.setMaterial_(BACKDROP_MATERIAL)
            self.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
            self.setState_(NSVisualEffectStateActive)
            self.setWantsLayer_(True)
            self.layer().setCornerRadius_(WINDOW_CORNER_RADIUS)
            self.layer().setMasksToBounds_(True)
            
            # Add thin elegant border glow
            self.layer().setBorderColor_(COLOR_BORDER_LIGHT.CGColor())
            self.layer().setBorderWidth_(1.0)
        return self


class PremiumTextFieldCell(NSTextFieldCell):
    """Custom NSTextFieldCell subclass that adds horizontal/vertical text padding."""

    def drawingRectForBounds_(self, rect):
        # Inset text by 16px horizontally and 10px vertically for modern Spotlight look
        new_rect = NSMakeRect(
            rect.origin.x + 16,
            rect.origin.y + 10,
            rect.size.width - 32,
            rect.size.height - 20
        )
        return objc.super(PremiumTextFieldCell, self).drawingRectForBounds_(new_rect)


class PremiumTextField(NSTextField):
    """Custom Spotlight-style translucent text field with focus highlighting."""

    def initWithFrame_(self, frame):
        self = objc.super(PremiumTextField, self).initWithFrame_(frame)
        if self:
            # Swap standard cell with padded cell
            cell = PremiumTextFieldCell.alloc().init()
            cell.setPlaceholderString_(self.cell().placeholderString())
            cell.setEditable_(True)
            cell.setSelectable_(True)
            self.setCell_(cell)

            self.setBezeled_(False)
            self.setBordered_(False)
            self.setDrawsBackground_(True)
            self.setFocusRingType_(NSFocusRingTypeNone)

            from text2prompt.ui.styles import COLOR_INPUT_BG, COLOR_TEXT_PRIMARY, FONT_INPUT, ELEMENT_CORNER_RADIUS
            self.setBackgroundColor_(COLOR_INPUT_BG)
            self.setTextColor_(COLOR_TEXT_PRIMARY)
            self.setFont_(FONT_INPUT)
            
            self.setWantsLayer_(True)
            self.layer().setCornerRadius_(ELEMENT_CORNER_RADIUS)
            self.layer().setMasksToBounds_(True)
            self.layer().setBorderWidth_(0.0)
        return self

    def becomeFirstResponder(self):
        success = objc.super(PremiumTextField, self).becomeFirstResponder()
        if success:
            from text2prompt.ui.styles import COLOR_INPUT_FOCUS_BG, COLOR_ACCENT_GLOW
            self.setBackgroundColor_(COLOR_INPUT_FOCUS_BG)
            self.layer().setBorderColor_(COLOR_ACCENT_GLOW.CGColor())
            self.layer().setBorderWidth_(1.5)
        return success

    def resignFirstResponder(self):
        success = objc.super(PremiumTextField, self).resignFirstResponder()
        if success:
            from text2prompt.ui.styles import COLOR_INPUT_BG
            self.setBackgroundColor_(COLOR_INPUT_BG)
            self.layer().setBorderWidth_(0.0)
        return success


class PremiumScrollView(NSScrollView):
    """Custom scroll view with translucent dark theme styling."""

    def initWithFrame_(self, frame):
        self = objc.super(PremiumScrollView, self).initWithFrame_(frame)
        if self:
            self.setHasVerticalScroller_(True)
            self.setDrawsBackground_(True)
            self.setBorderType_(NSNoBorder)
            
            from text2prompt.ui.styles import COLOR_CONTAINER_BG, ELEMENT_CORNER_RADIUS
            self.setBackgroundColor_(COLOR_CONTAINER_BG)
            
            self.setWantsLayer_(True)
            self.layer().setCornerRadius_(ELEMENT_CORNER_RADIUS)
            self.layer().setMasksToBounds_(True)
        return self


class PremiumTextView(NSTextView):
    """Custom output text editor with internal margins and custom color tokens."""

    def initWithFrame_(self, frame):
        self = objc.super(PremiumTextView, self).initWithFrame_(frame)
        if self:
            self.setEditable_(True)
            self.setDrawsBackground_(False)
            
            from text2prompt.ui.styles import COLOR_TEXT_PRIMARY, FONT_BODY
            self.setTextColor_(COLOR_TEXT_PRIMARY)
            self.setFont_(FONT_BODY)
            self.setTextContainerInset_(NSMakeSize(12, 12))
        return self


class PremiumButton(NSButton):
    """Standard premium button styled as a flat translucent card."""

    def initWithFrame_(self, frame):
        self = objc.super(PremiumButton, self).initWithFrame_(frame)
        if self:
            self.setBordered_(False)  # Remove standard AppKit grey bezel
            self.setWantsLayer_(True)
            from text2prompt.ui.styles import COLOR_CONTAINER_BG, ELEMENT_CORNER_RADIUS, COLOR_BORDER_LIGHT
            self.layer().setBackgroundColor_(COLOR_CONTAINER_BG.CGColor())
            self.layer().setCornerRadius_(ELEMENT_CORNER_RADIUS)
            self.layer().setBorderColor_(COLOR_BORDER_LIGHT.CGColor())
            self.layer().setBorderWidth_(1.0)
            
            self.setTitle_(self.title())
        return self

    def setTitle_(self, title):
        objc.super(PremiumButton, self).setTitle_(title)
        from text2prompt.ui.styles import FONT_STATUS, COLOR_TEXT_PRIMARY
        attr_title = NSMutableAttributedString.alloc().initWithString_attributes_(
            title,
            {
                NSForegroundColorAttributeName: COLOR_TEXT_PRIMARY,
                NSFontAttributeName: FONT_STATUS,
            }
        )
        self.setAttributedTitle_(attr_title)


class PremiumPrimaryButton(PremiumButton):
    """Primary action button styled with flat glowing neon accent color."""

    def initWithFrame_(self, frame):
        self = objc.super(PremiumPrimaryButton, self).initWithFrame_(frame)
        if self:
            from text2prompt.ui.styles import COLOR_ACCENT_GLOW
            self.layer().setBackgroundColor_(COLOR_ACCENT_GLOW.CGColor())
            self.layer().setBorderWidth_(0.0)  # Pure borderless solid glow
            
            self.setTitle_(self.title())
        return self

    def setTitle_(self, title):
        objc.super(PremiumPrimaryButton, self).setTitle_(title)
        from text2prompt.ui.styles import FONT_STATUS
        attr_title = NSMutableAttributedString.alloc().initWithString_attributes_(
            title,
            {
                NSForegroundColorAttributeName: NSColor.whiteColor(),
                NSFontAttributeName: FONT_STATUS,
            }
        )
        self.setAttributedTitle_(attr_title)
