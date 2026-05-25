# text2prompt — AGENTS.md

Privacy-first, on-device macOS prompt builder powered by Apple Intelligence.
v2.0.0 — macOS 26.0+ / Apple Silicon only.

## Architecture

```
src/text2prompt/
├── __main__.py          # CLI + py2app entry point
├── app.py               # AppDelegate — orchestrates menu bar app lifecycle
├── config.py            # Config dataclass, ~/.text2prompt/preferences.json
├── engine/
│   ├── model.py         # apple-fm-sdk wrapper (on-device LLM inference)
│   └── templates.py     # TemplateRegistry singleton — mode → prompt template
├── memory/
│   └── db.py            # SQLite history — scoped by context_id, capped at 10
├── menu/
│   ├── statusbar.py     # NSStatusBar + custom click handler
│   ├── popover.py       # Frosted-glass prompt window (NSVisualEffectView)
│   ├── hotkey.py        # Cmd+Shift+Space global hotkey (NSEvent monitors)
│   ├── history.py       # NSTableView prompt history viewer
│   └── preferences.py   # Preferences modal + login item management
├── ui/
│   ├── styles.py        # Dimension/color/margin constants
│   └── panel.py         # NSRect layout helpers
├── utils/
│   ├── parser.py        # CLI mode flags + clipboard prefix detection
│   └── system.py        # osascript: foreground app/window detection
└── templates/
    ├── general.py       # Meta-Prompt Engineer persona
    ├── image.py         # Subject/Environment/Style/Camera/Technical
    ├── code.py          # Role/Context/Problem/Constraints/Output
    ├── creative.py      # Voice/Setting/Character/Structure/Constraints
    └── analysis.py      # Role/Scope/Framework/Evidence/Output
```

## Five Prompt Modes

| Mode | CLI Flag | Clipboard Prefix |
|---|---|---|
| **general** | (default) | — |
| **image** | `--image` | `/image` |
| **code** | `--code` | — |
| **creative** | `--creative` | — |
| **analysis** | `--analysis` | — |

All templates enforce: output only the generated prompt, no conversational filler, ready to paste.

## Key Patterns

- **Background threading:** Prompt generation runs on `threading.Thread(daemon=True)`, UI updates via `AppHelper.callAfter()`
- **Singletons:** `TemplateRegistry` via module-level `_registry` factory
- **Lazy windows:** HistoryWindow, PreferencesWindow created on first show, reused
- **AppleScript integration:** `subprocess.run(['osascript', '-e', ...])` for foreground app detection, Replace (Cmd+V), login items
- **SQLite multi-thread:** `check_same_thread=False`, history scoped by `context_id = "AppName::WindowTitle:mode"`, 10-entry cap

## Development

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Build macOS app
python setup.py py2app
```

## Testing

- Framework: pytest + pytest-asyncio
- Test files: `tests/test_engine.py`, `test_templates.py`, `test_parser.py`, `test_config.py`, `test_db.py`, `test_system.py`
- Config: `testpaths = ["tests"]`, `pythonpath = ["src"]`

## Conventions

- **TDD required** — write tests before implementation
- **Type hints** on all functions
- **Google-style docstrings** (Args/Returns/Raises)
- **Conventional commits:** `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- **Ruff:** line-length 100, target py310, rules: E F I N W UP B C4 SIM
- **Double quotes**, space indentation

## Dependencies

| Package | Purpose |
|---|---|
| `apple-fm-sdk` | On-device LLM inference via Apple Neural Engine |
| `pyperclip` | Clipboard access |
| `pyobjc` | Python-to-Objective-C bridge (NSWindow, NSEvent, etc.) |
| `pytest`, `pytest-asyncio` (dev) | Testing |
| `ruff`, `pyright` (dev) | Linting + type checking |

## Config Location

User preferences: `~/.text2prompt/preferences.json`
Fields: `db_path`, `max_history`, `default_mode`, `auto_copy`, `include_context`, `save_history`, `launch_at_login`
