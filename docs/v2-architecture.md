# text2prompt v2.0 Architecture

## Vision
A modern, native macOS menu bar app that transforms any text into expertly crafted prompts. Released May 20, 2026.

## Key Features
1. **Menu Bar App** - Always accessible, native macOS feel
2. **Streaming Text** - Real-time token-by-token display
3. **Prompt History** - Searchable library of all generated prompts
4. **Preferences Panel** - Full customization
5. **Global Hotkey** - Trigger from anywhere with keyboard shortcut
6. **Prompt Quality Scoring** - Rate and improve prompts
7. **Export Options** - Copy, save, share in multiple formats
8. **Modern UI** - Smooth animations, transitions, dark mode

## Architecture

```
src/text2prompt/
├── __init__.py
├── __main__.py
├── app.py                  # NSApplication + AppDelegate
├── config.py               # Settings management
├── logging_config.py       # Application logging
├── menu/
│   ├── __init__.py
│   ├── statusbar.py        # NSStatusBar + NSMenu
│   └── popover.py          # NSPopover with main UI
├── ui/
│   ├── __init__.py
│   ├── main_view.py        # Main prompt generation view
│   ├── history_view.py     # Prompt history browser
│   ├── prefs_view.py       # Preferences panel
│   ├── streaming_text.py   # Streaming text display
│   └── styles.py           # Colors, fonts, constants
├── engine/
│   ├── __init__.py
│   ├── model.py            # apple-fm-sdk wrapper with streaming
│   ├── templates.py        # Prompt template registry
│   └── scorer.py           # Prompt quality scoring
├── memory/
│   ├── __init__.py
│   ├── db.py               # SQLite with FTS5 search
│   └── export.py           # Export functionality
├── utils/
│   ├── __init__.py
│   ├── parser.py           # Mode/text parsing
│   ├── system.py           # osascript, app detection
│   ├── hotkey.py           # Global keyboard shortcuts
│   └── clipboard.py        # Clipboard operations
└── templates/
    ├── __init__.py
    ├── general.py
    ├── image.py
    ├── code.py
    ├── creative.py
    └── analysis.py
```

## UI Flow

1. **Menu Bar Icon** - Always visible, click to open popover
2. **Popover** - Main interface with:
   - Text input field
   - Mode selector (tabs or dropdown)
   - Generate button
   - Streaming output display
   - Action buttons (Copy, Save, Replace, History)
3. **History View** - Searchable list of past prompts
4. **Preferences** - Customization panel

## Technical Details

- **Streaming**: Use apple-fm-sdk's streaming API with token-by-token updates
- **Hotkey**: Register global hotkey via NSEvent monitor
- **Animations**: Core Animation for smooth transitions
- **Dark Mode**: Automatic via NSAppearance
- **Storage**: SQLite with FTS5 for full-text search

## Release Checklist
- [ ] All features implemented
- [ ] Tests passing
- [ ] Documentation complete
- [ ] Install script updated
- [ ] README with screenshots
- [ ] LICENSE and CONTRIBUTING
- [ ] Version 2.0.0 tag
