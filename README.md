# text2prompt

Turn rough ideas into polished AI prompts — right from your menu bar. Zero data leaves your Mac.

<img src="assets/icon_512.png" width="80" />

---

## What it does

You type a short idea. text2prompt transforms it into a detailed, ready-to-paste prompt using Apple's on-device AI. Works in any app via `Cmd+Shift+Space`.

**Five modes, one hotkey:**
| Mode | For |
|---|---|
| General | Anything |
| Image | AI image prompts |
| Code | Coding help |
| Creative | Writing & stories |
| Analysis | Research & data |

---

## Install

```bash
curl -sSL https://raw.githubusercontent.com/nainwalsanju/text2prompt/main/install.sh | bash
```

Requires: Apple Silicon Mac, macOS 26+

---

## Use

```bash
# CLI
text2prompt "a knight in shining armor"
text2prompt --image "a sunset over mountains"
text2prompt --code "explain this function"

# Or hit Cmd+Shift+Space anywhere
```

---

## Why

- **100% local** — runs on Apple Neural Engine, not the cloud
- **No API keys** — no accounts, no subscriptions
- **No internet** — works offline
- **Menu bar app** — always one click away

---

## Dev

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

---

[MIT](LICENSE)
