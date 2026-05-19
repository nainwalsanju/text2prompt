# 🍎 text2prompt v2.0

A blazing-fast, privacy-first, on-device prompt builder for macOS powered by Apple Intelligence.

Transform short descriptions into highly detailed, expertly crafted prompts for AI generation — entirely on your Mac, with zero data leaving your machine.

**Released May 20, 2026**

---

## ✨ Features

- **Menu Bar App** - Always accessible, native macOS experience with sparkles icon
- **5 Prompt Modes:** General, Image Generation, Code Assistance, Creative Writing, and Analysis
- **Native macOS Feel:** Beautiful popover with frosted-glass (`NSVisualEffectView`) and dark mode support
- **100% Local Processing:** Powered by Apple's on-device Foundation Models SDK — runs on Neural Engine
- **Contextual Memory:** Maintains per-app context history using SQLite
- **Instant Injection:** Replace selected text natively in any app
- **CLI + Menu Bar:** Use from terminal or click the menu bar icon

No API keys, no internet connection required, and zero data leaves your machine.

---

## ⚡️ Prerequisites

- **Apple Silicon Mac** (M1, M2, M3, M4)
- **macOS 26.0 (Tahoe) or newer**
- **Apple Intelligence** enabled in System Settings
- **Xcode 26.0+** installed with license agreement accepted

---

## 🚀 One-Command Installation

Open **Terminal** and run:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/text2prompt/main/install.sh | bash
```

*(Replace `YOUR_USERNAME` with your GitHub username)*

### What the installer does:
1. Creates isolated Python virtual environment at `~/.text2prompt/`
2. Installs the package with all dependencies
3. Sets up CLI command `text2prompt` in `~/.local/bin/`

---

## 🪄 How to Use

### Via Menu Bar

1. Click the **sparkles icon** in your menu bar
2. Type your idea in the input field
3. Select a mode (General, Image, Code, Creative, Analysis)
4. Click **Generate**
5. Click **Replace** to swap text, or **Copy** to clipboard

### Via CLI

```bash
# General prompt
text2prompt "a knight in shining armor"

# Image generation
text2prompt --image "a sunset over mountains"

# Code assistance
text2prompt --code "explain this function"

# Creative writing
text2prompt --creative "write a poem about rain"

# Analysis
text2prompt --analysis "analyze this data"
```

---

## 📋 Prompt Modes

| Mode | Flag | Use Case |
|------|------|----------|
| General | (default) | Enhance any text into optimal prompts |
| Image | `--image` | Generate prompts for AI image models |
| Code | `--code` | Create prompts for code explanation/generation |
| Creative | `--creative` | Creative writing and storytelling prompts |
| Analysis | `--analysis` | Research and analytical prompts |

---

## 🔒 Privacy & Permissions

- **100% Private:** Zero bytes leave your machine
- **Accessibility Permission:** Required for text replacement (simulate `Cmd+V`)
- **Grant in:** System Settings → Privacy & Security → Accessibility

---

## 🛠 Development

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/text2prompt.git
cd text2prompt
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run the app
python -m text2prompt "test prompt"
```

---

## 📁 Project Structure

```
src/text2prompt/
├── app.py              # Main application
├── config.py           # Configuration
├── menu/               # Menu bar components
│   ├── statusbar.py    # NSStatusBar + menu
│   └── popover.py      # Popover UI
├── engine/             # AI engine
│   ├── model.py        # apple-fm-sdk wrapper
│   └── templates.py    # Template registry
├── memory/             # SQLite persistence
│   └── db.py
├── ui/                 # UI components
│   ├── panel.py
│   └── styles.py
├── utils/              # Utilities
│   ├── parser.py       # Mode/text parsing
│   └── system.py       # osascript helpers
└── templates/          # Prompt templates
    ├── general.py
    ├── image.py
    ├── code.py
    ├── creative.py
    └── analysis.py
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

*Built with Python, PyObjC, and Apple's Foundation Models SDK.*
