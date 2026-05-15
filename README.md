# 🍎 Apple Prompt Enhancer

A blazing-fast, privacy-first, on-device text expander that takes short descriptions and turns them into highly detailed, vivid prompts for AI generation. 

It mimics the native Apple Intelligence "Writing Tools" by utilizing a floating, frameless UI that appears at your cursor's location. It processes the text locally via the official `apple-fm-sdk` and allows you to instantly inject the enhanced prompt back into your active application.

No API keys, no internet connection required, and zero data leaves your machine.

---

## ✨ Features

- **Native macOS Feel:** Uses PyObjC to render a beautiful, borderless window with Apple's native frosted-glass (`NSVisualEffectView`) and dark mode support. Instantly pops up at your cursor without the cold-boot delay of other UI frameworks.
- **100% Local Processing:** Powered by your Mac's Neural Engine. Your text is processed entirely on-device.
- **Contextual Memory:** Maintains short-term memory per-app context (e.g., Notes, Safari) using a lightweight SQLite database.
- **Instant Injection:** Replaces your selected text natively, right where you typed it.

## ⚡️ Prerequisites

- **Apple Silicon Mac** (M1, M2, M3, M4)
- **macOS 15.1 (Sequoia) or newer**
- **Apple Intelligence** enabled in System Settings

## 🚀 One-Command Installation

You don't need to configure anything. Just open **Terminal** and run this single command to download and install the app automatically:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/apple-prompt-enhancer/main/install.sh | bash
```

*(Note: Replace `YOUR_USERNAME` with your actual GitHub username once you push this repository).*

### What the installer does automatically:
1. Creates a clean, isolated Python virtual environment at `~/.apple_enhancer/`.
2. Installs the required libraries (`apple-fm-sdk`, `pyperclip`, `pyobjc`).
3. Generates a native macOS "Quick Action" in your `~/Library/Services/` folder.
4. Makes the tool available instantly across your entire Mac.

## 🪄 How to Use It

The Enhancer integrates directly into macOS as a system-wide Quick Action. You can use it in **any app**!

1. **Highlight** a short idea (e.g., `"a knight in shining armor"`).
2. **Right-click** the text.
3. Navigate to **Services > Enhance Prompt** (or click it if it's in the main menu).
4. A beautiful, native popup will appear at your cursor, showing the AI generating your prompt.
5. Click **Replace** to instantly swap your short text with the highly detailed prompt!

### Pro-Tip: Add a Keyboard Shortcut
For maximum speed, bind it to a shortcut:
1. Open **System Settings**.
2. Go to **Keyboard > Keyboard Shortcuts... > Services**.
3. Under the **Text** section, find **Enhance Prompt**.
4. Double-click "none" and press a shortcut (e.g., `Cmd + Shift + E`).
5. Now, just highlight text and press `Cmd + Shift + E`!

## 🔒 Privacy & Permissions

- **100% Private:** Zero bytes of data leave your machine.
- **Accessibility Permission:** The first time you click "Replace", macOS will ask you to grant Accessibility permissions to the app. This is completely safe and is required so the app can simulate the `Cmd+V` keystroke to auto-paste the text for you. 

## 🛠 Project Structure

This project is built to be easily extensible. 

- `apple_enhancer.py`: The main application. Uses `PyObjC` for the native Apple UI and `apple-fm-sdk` for AI inference.
- `install.sh`: The automated 1-click installation script.

Want to use a different local model like Ollama or MLX? The python script can be easily adapted to swap out the AI engine!

---
*Built with Python, PyObjC, and Apple Intelligence.*