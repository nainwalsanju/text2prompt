# text2prompt Roadmap

> What's next for the privacy-first, on-device prompt builder.

---

## Current State (v2.0)

- **5 prompt modes**: General, Image, Code, Creative, Analysis
- **Menu bar app** with global hotkey (`Cmd+Shift+Space`)
- **Apple Intelligence** on-device inference (Apple Neural Engine)
- **Context-aware history** scoped by active app + window title
- **SQLite memory** with 10-entry cap per context
- **Auto-copy & replace** via clipboard + AppleScript
- **Zero cloud dependency** — 100% local

---

## Phase 1: Core UX Polish

### 1.1 Keyboard-First Navigation
- **Tab through modes** in the popover without using the mouse
- **Arrow keys** to cycle through history suggestions
- **Escape** to close the popover from anywhere
- **Cmd+Enter** to generate (currently only Enter on the input field works)

### 1.2 Inline Preview
- Show a **live preview** of the generated prompt before copying
- Allow **editing the output** directly in the popover before pasting
- **Diff view**: compare original input vs enhanced output side-by-side

### 1.3 Quick Actions
- **Star/favorite** prompts to a separate "Favorites" section
- **Recent prompts** list accessible via dropdown in the input field
- **One-click rerun** last prompt with the same mode

---

## Phase 2: New Prompt Modes

### 2.1 Markdown Mode
Optimizes prompts for AI models that consume markdown (Claude, GPT-4, etc.).
- Adds structure hints: tables, code blocks, headings
- Embeds formatting instructions in the system prompt

### 2.2 Shell Mode
Transforms natural language into ready-to-run terminal commands.
- "list all files modified in the last hour" → `find . -mtime -1 -type f`
- Includes safety warnings for destructive commands
- Supports bash, zsh, fish syntax variants

### 2.3 Translation Mode
Specializes in translating rough ideas into prompts for non-English outputs.
- Auto-detects target language from context
- Preserves technical terms in original language

### 2.4 Debugging Mode
Takes error messages / logs and generates structured debugging prompts.
- "Ask the AI to analyze this stack trace step-by-step"
- Suggests relevant files to include based on error context

### 2.5 Summary Mode
Condenses long content into concise prompts for summarization.
- "Summarize this meeting transcript into 3 bullet points"
- Supports chunking for very long inputs

---

## Phase 3: Context & Intelligence

### 3.1 File Context Awareness
- Detect if the active app is a code editor (VS Code, Xcode, Cursor)
- **Auto-suggest** including the current file name or selection
- Option to "Include current file content" as additional context

### 3.2 URL Context
- If the active app is a browser, offer to include:
  - Page title
  - Selected text
  - URL itself
- Useful for: "summarize this article", "extract key points"

### 3.3 Selection-aware Input
- If text is selected in the active app when the hotkey is pressed,
  auto-populate the input field with the selection
- Shows a "Selection: 142 chars" indicator

### 3.4 Multi-turn Conversations
- Currently history is read-only context. Enable **follow-up mode**
  where the user can refine the prompt in a chat-like interface
- Show previous turn as collapsible context in the popover

---

## Phase 4: Customization

### 4.1 User-defined Templates
- Allow users to **create custom modes** with their own system instructions
- Template variables: `{input}`, `{context}`, `{history}`
- Import/export templates as JSON

### 4.2 Persona Presets
- Switch between personas: "Concise", "Verbose", "Academic", "Casual"
- Each persona tweaks the system instruction without changing the mode

### 4.3 Output Length Control
- Slider or presets: Short / Medium / Long / Max
- Adjusts constraints in the system prompt dynamically

### 4.4 Temperature Control
- Expose the model's temperature parameter in preferences
- Low = deterministic, High = creative

---

## Phase 5: Integrations

### 5.1 Raycast Extension
- Native Raycast command that opens the popover or runs inline
- No menu bar app needed for Raycast power users

### 5.2 Alfred Workflow
- Alfred keyword `t2p` to trigger prompt generation
- Show results directly in Alfred's output pane

### 5.3 Shortcuts App (Siri Shortcuts)
- "Hey Siri, enhance this prompt"
- Shortcut action that accepts text and returns the enhanced version
- Allows chaining: Drafts → text2prompt → Mail

### 5.4 API Mode (Local HTTP Server)
- Optional lightweight HTTP server for other apps to call
- `POST /enhance {text, mode}` → returns enhanced prompt
- Useful for automators, Hammerspoon, Keyboard Maestro

---

## Phase 6: Intelligence Upgrades

### 6.1 Mode Auto-detection
- Use a lightweight on-device classifier to **guess the mode**
  from the input text
- "write a python function" → auto-selects Code mode
- "draw a picture of" → auto-selects Image mode
- Shows suggestion but allows override

### 6.2 Quality Scoring
- After generation, show a **confidence score** (1-5 stars)
- Based on: prompt length, keyword density, structure completeness
- Low score = offer to regenerate with adjusted parameters

### 6.3 Prompt Validation
- Detect common anti-patterns in the output:
  - Negative phrasing in image prompts
  - Missing constraints in code prompts
  - Passive voice in creative prompts
- Show warnings with one-click fixes

---

## Phase 7: Enterprise & Power User

### 7.1 Team Templates
- Sync custom templates via iCloud or shared folder
- Organization-wide persona and constraint presets

### 7.2 Analytics Dashboard
- Stats: prompts generated per day, most-used modes, average length
- Privacy-preserving: all data stays local, displayed in a local web view

### 7.3 Batch Processing
- Drop a text file or folder of files
- Batch-enhance all prompts in one run
- Export results as CSV or individual .txt files

---

## Nice-to-Haves

| Feature | Why | Priority |
|---------|-----|----------|
| Dark/light mode adaptive UI | macOS aesthetic consistency | Low |
| Custom hotkey binding | User preference flexibility | Low |
| Voice input (Siri dictation) | Hands-free usage | Low |
| Widget for macOS Notification Center | Quick access without menu bar | Low |
| iCloud sync for history | Cross-device continuity | Low |
| Localization (French, German, Japanese) | Broader audience | Low |

---

## Contributing

Want to pick up one of these? Open an issue with the feature name and we'll discuss approach.

Priority order for implementation:
1. **Phase 1** (UX polish) — highest impact, lowest risk
2. **Phase 2** (new modes) — extends utility without architecture changes
3. **Phase 3** (context) — requires deeper macOS integration
4. **Phase 4+** — incremental enhancements

All features must maintain the core constraint: **zero cloud calls, 100% on-device**.
