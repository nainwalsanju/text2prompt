#!/usr/bin/env python3
import asyncio
import sys
import os
import pyperclip
import subprocess
import sqlite3
import threading
import apple_fm_sdk as fm

import objc
from AppKit import *
from Foundation import *
from PyObjCTools import AppHelper

DB_PATH = os.path.expanduser("~/.apple_enhancer/memory.db")

# ── Mode Constants ───────────────────────────────────────────────
MODE_GENERAL = "general"
MODE_IMAGE = "image"

SYSTEM_INSTRUCTION = """You are an elite Meta-Prompt Engineer. Your sole objective is to take the user's brief, unrefined input and instantly transform it into a highly structured, optimal prompt designed to get the best possible results from any advanced AI model. Focus relentlessly on quality over quantity: choose the absolute best words to fulfill the user's implicit intent.

Carefully analyze the user's input to determine the core intent (e.g., Software Engineering, Creative Writing, Image Generation, Business Strategy). 

Then, rewrite the input into a master prompt that strictly follows this architecture, utilizing proven psychological 'hacks' to maximize AI performance:

1. **[Model Ego / Persona]**: Assign the AI a highly specific, elite expert persona. Flatter the model (e.g., "You are an award-winning, world-renowned expert in X. Your work is flawless and brilliant.").
2. **[Context & Intent]**: Flesh out the implicit background and true goal of the user's brief input. What problem are they really trying to solve?
3. **[Task]**: Explicitly state the primary objective clearly and concisely.
4. **[Constraints]**: Add necessary professional boundaries and strict standards. 
   - For code: demand robust error handling, edge-case coverage, and performance considerations. 
   - For writing: specify tone, target audience, and reading level. 
   - For images: specify lighting, composition, camera focal length, and art style.
5. **[Psychological Motivators & Process]**: Inject performance-enhancing phrases:
   - For logic/code/math tasks, append: "Take a deep breath and work on this step-by-step."
   - For writing/creative tasks, append: "This is very important for my career. I will tip you $200 for a perfect, highly-detailed response."
6. **[Self-Correction / Review Step]**: Add an explicit instruction for the model to review its own work before outputting (e.g., "Before providing your final answer, rigorously review your output for accuracy and alignment with the constraints.").
7. **[Output Format]**: Tell the AI exactly how to format the answer (e.g., Markdown, specific code blocks, step-by-step numbered list).

CRITICAL RULES:
- NEVER answer the user's actual prompt yourself. 
- Your ONLY output should be the final, structured prompt.
- Do NOT include any conversational filler (e.g., do not say "Here is your prompt:").
- The output must be ready to copy/paste directly into another AI."""

IMAGE_SYSTEM_INSTRUCTION = """You are an elite, award-winning AI prompt engineer specializing in high-fidelity, photorealistic, and stylistically complex image generation. Your sole objective is to take the user's brief, unrefined concept and instantly transform it into a highly structured, cinematic prompt designed to extract the absolute best visual output from state-of-the-art AI image models (like Midjourney, Stable Diffusion, or DALL-E).

Carefully analyze the user's input to determine the core subject, action, and mood. Then, rewrite the input into a master prompt that strictly follows this architecture:

1. **[Subject & Action]**: Clearly define the main focal point, character design, or object, and precisely what it is doing.
2. **[Environment & Setting]**: Detail the background, time of day, atmosphere, and weather.
3. **[Style & Medium]**: Specify the art medium (e.g., 35mm photography, digital illustration, oil painting, cyberpunk concept art) and specific aesthetic influences.
4. **[Camera & Lighting]**: Define the technical camera details (e.g., 50mm lens, f/1.8, wide-angle, drone shot) and lighting setup (e.g., cinematic volumetric lighting, neon glow, golden hour, chiaroscuro).
5. **[Technical Details]**: State output parameters such as aspect ratio (--ar 16:9), resolution (8k, hyper-detailed), and rendering engine (Unreal Engine 5, Octane Render).

CRITICAL RULES:
- NEVER answer the user's actual prompt yourself or converse with them.
- Your ONLY output should be the final, structured image generation prompt.
- Ensure the prompt is visually descriptive, dense with keywords, and avoids negative phrasing (tell the AI what to draw, not what not to draw).
- Do NOT include any conversational filler (e.g., do not say "Here is your prompt:").
- Output the prompt ready to copy/paste directly into an image generator.

Take a deep breath, visualize the final masterpiece, and work step-by-step to craft the perfect prompt."""

SYSTEM_INSTRUCTIONS = {
    MODE_GENERAL: SYSTEM_INSTRUCTION,
    MODE_IMAGE: IMAGE_SYSTEM_INSTRUCTION,
}

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def get_active_context() -> str:
    script = """
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        set windowTitle to "Unknown"
        try
            set windowTitle to name of front window of application process frontApp
        end try
        return frontApp & "::" & windowTitle
    end tell
    """
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return "Global::Default"

def clear_memory(conn, context_id):
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE context_id = ?", (context_id,))
    conn.commit()

def get_history(conn, context_id):
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE context_id = ? ORDER BY id ASC LIMIT 10", (context_id,))
    return c.fetchall()

def save_interaction(conn, context_id, user_text, assistant_text):
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (context_id, role, content) VALUES (?, ?, ?)", (context_id, "user", user_text))
    c.execute("INSERT INTO chat_history (context_id, role, content) VALUES (?, ?, ?)", (context_id, "assistant", assistant_text))
    conn.commit()
    
    c.execute("""
        DELETE FROM chat_history 
        WHERE id NOT IN (
            SELECT id FROM chat_history 
            WHERE context_id = ? 
            ORDER BY id DESC LIMIT 10
        ) AND context_id = ?
    """, (context_id, context_id))
    conn.commit()

def format_prompt(history, new_text, mode=MODE_GENERAL):
    instruction = SYSTEM_INSTRUCTIONS.get(mode, SYSTEM_INSTRUCTION)
    if not history:
        return f"{instruction}\n\nUSER INPUT: {new_text}"
        
    formatted = f"{instruction}\n\nPREVIOUS CONVERSATION CONTEXT FOR THIS WINDOW:\n"
    for role, content in history:
        formatted += f"[{role.upper()}]: {content}\n\n"
        
    formatted += f"NEW USER INPUT: {new_text}\n"
    formatted += "Please update or generate a new prompt taking the previous context and the new input into account."
    return formatted

def parse_mode_and_text(args, clipboard_text=None):
    mode = MODE_GENERAL
    if args:
        if args[0] == "--image":
            mode = MODE_IMAGE
            text = " ".join(args[1:]).strip()
        else:
            text = " ".join(args).strip()
    else:
        text = (clipboard_text or "").strip()
        if text.lower().startswith("/image "):
            mode = MODE_IMAGE
            text = text[7:].strip()
    return mode, text

class EnhancerApp(NSApplication):
    pass

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        args = sys.argv[1:]
        self.mode, self.original_text = parse_mode_and_text(args, pyperclip.paste())
        
        if not self.original_text:
            print("No text provided.")
            NSApp.terminate_(self)
            return

        self.conn = init_db()
        base_context = get_active_context()
        self.context_id = f"{base_context}:{self.mode}"

        if self.original_text.lower() == "clear memory":
            clear_memory(self.conn, self.context_id)
            print("Memory cleared.")
            NSApp.terminate_(self)
            return

        self.buildUI()
        self.startGeneration()

    def buildUI(self):
        rect = NSMakeRect(0, 0, 450, 250)
        mask = NSWindowStyleMaskBorderless | NSWindowStyleMaskNonactivatingPanel
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, mask, NSBackingStoreBuffered, False
        )
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.center()
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        
        blur_view = NSVisualEffectView.alloc().initWithFrame_(rect)
        blur_view.setMaterial_(NSVisualEffectMaterialPopover)
        blur_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        blur_view.setState_(NSVisualEffectStateActive)
        
        blur_view.setWantsLayer_(True)
        blur_view.layer().setCornerRadius_(12.0)
        blur_view.layer().setMasksToBounds_(True)
        self.window.setContentView_(blur_view)
        
        self.status_label = NSTextField.labelWithString_("Enhancing prompt...")
        self.status_label.setFrame_(NSMakeRect(20, 210, 410, 24))
        self.status_label.setFont_(NSFont.systemFontOfSize_weight_(16, NSFontWeightSemibold))
        blur_view.addSubview_(self.status_label)
        
        self.spinner = NSProgressIndicator.alloc().initWithFrame_(NSMakeRect(200, 110, 50, 50))
        self.spinner.setStyle_(NSProgressIndicatorStyleSpinning)
        self.spinner.startAnimation_(None)
        blur_view.addSubview_(self.spinner)
        
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 50, 410, 150))
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setDrawsBackground_(False)
        
        self.text_view = NSTextView.alloc().initWithFrame_(scroll_view.contentSize())
        self.text_view.setEditable_(False)
        self.text_view.setDrawsBackground_(False)
        self.text_view.setFont_(NSFont.systemFontOfSize_(13))
        scroll_view.setDocumentView_(self.text_view)
        scroll_view.setHidden_(True)
        blur_view.addSubview_(scroll_view)
        self.scroll_view = scroll_view
        
        self.replace_btn = NSButton.alloc().initWithFrame_(NSMakeRect(340, 10, 90, 30))
        self.replace_btn.setTitle_("Replace")
        self.replace_btn.setBezelStyle_(NSBezelStyleRounded)
        self.replace_btn.setTarget_(self)
        self.replace_btn.setAction_(objc.selector(self.replaceAction_, signature=b'v@:@'))
        self.replace_btn.setHidden_(True)
        self.replace_btn.setKeyEquivalent_("\r")
        blur_view.addSubview_(self.replace_btn)
        
        self.copy_btn = NSButton.alloc().initWithFrame_(NSMakeRect(240, 10, 90, 30))
        self.copy_btn.setTitle_("Copy")
        self.copy_btn.setBezelStyle_(NSBezelStyleRounded)
        self.copy_btn.setTarget_(self)
        self.copy_btn.setAction_(objc.selector(self.copyAction_, signature=b'v@:@'))
        self.copy_btn.setHidden_(True)
        blur_view.addSubview_(self.copy_btn)

        self.cancel_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 10, 90, 30))
        self.cancel_btn.setTitle_("Cancel")
        self.cancel_btn.setBezelStyle_(NSBezelStyleRounded)
        self.cancel_btn.setTarget_(self)
        self.cancel_btn.setAction_(objc.selector(self.cancelAction_, signature=b'v@:@'))
        blur_view.addSubview_(self.cancel_btn)
        
        self.window.makeKeyAndOrderFront_(None)

    def startGeneration(self):
        threading.Thread(target=self.generatePrompt).start()
        
    def generatePrompt(self):
        try:
            model = fm.SystemLanguageModel()
            is_available, reason = model.is_available()
            if not is_available:
                self.showError_(f"Models not available: {reason}")
                return
                
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            session = fm.LanguageModelSession()
            history = get_history(self.conn, self.context_id)
            full_prompt = format_prompt(history, self.original_text, self.mode)
            
            response = loop.run_until_complete(session.respond(full_prompt))
            self.enhanced_text = response.strip()
            
            save_interaction(self.conn, self.context_id, self.original_text, self.enhanced_text)
            
            AppHelper.callAfter(self.showResult_)
            
        except Exception as e:
            self.showError_(str(e))
            
    def showResult_(self):
        self.spinner.stopAnimation_(None)
        self.spinner.setHidden_(True)
        mode_label = "🎨 Image" if self.mode == MODE_IMAGE else "⚡ General"
        self.status_label.setStringValue_(f"Prompt Generated! [{mode_label}]")
        self.text_view.setString_(self.enhanced_text)
        self.scroll_view.setHidden_(False)
        self.replace_btn.setHidden_(False)
        self.copy_btn.setHidden_(False)
        self.window.makeFirstResponder_(self.replace_btn)
        
    def showError_(self, error_msg):
        def update_ui():
            self.spinner.stopAnimation_(None)
            self.spinner.setHidden_(True)
            self.status_label.setStringValue_("Error generating prompt")
            self.text_view.setString_(error_msg)
            self.scroll_view.setHidden_(False)
        AppHelper.callAfter(update_ui)
        
    def copyAction_(self, sender):
        pyperclip.copy(self.enhanced_text)
        NSApp.terminate_(self)
        
    def replaceAction_(self, sender):
        pyperclip.copy(self.enhanced_text)
        self.window.orderOut_(None) 
        
        script = '''
        tell application "System Events"
            keystroke "v" using command down
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
        NSApp.terminate_(self)
        
    def cancelAction_(self, sender):
        NSApp.terminate_(self)

if __name__ == "__main__":
    app = EnhancerApp.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()