# Roblox SafeChat Overlay

**Version:** 1.0.0

A lightweight, always-on-top classic chat overlay for Roblox, built with wxPython. Provides quick-access canned phrases organized by category, injected directly into the Roblox chat - akin to the 2013 build.

---

## Features

- **Category-based phrases**: Loadable from `safechat.xml`, organized into nested categories.
- **Transparent overlay**: Semi-transparent window that floats above Roblox.
- **Drag & drop**: Click-and-drag the title bar to reposition anywhere on screen.
- **Toggle menu**: Collapse or expand the phrase list.
- **Always-on-top**: Pin/unpin the overlay at runtime.
- **Custom icon**: Window and executable icon support via `app.ico`.
- **Standalone executable**: Packaged into a single EXE with PyInstaller.

---

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Windows 10/11**
- Install required packages:
  ```bash
  pip install wxPython psutil pygetwindow keyboard pywin32
  ```

### Running from Source

1. Place `safechat.py`, `safechat.xml`, and `app.ico` in the same folder.
2. Open a command prompt in that folder.
3. Run:
   ```bash
   python safechat.py
   ```

---

## Building a Standalone EXE

Use **PyInstaller** to bundle everything into one executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon app.ico --name RobloxSafeChatOverlay --add-data "safechat.xml;." --add-data "app.ico;." safechat.py
```

- `--onefile`: Produce a single EXE.
- `--windowed`: Hide the console window.
- `--icon`: Embed `app.ico` as the application icon.
- `--add-data`: Include `safechat.xml` and `app.ico` inside the bundle.

After building, the EXE will be at `dist\RobloxSafeChatOverlay.exe`. Distribute it by sharing that file (no Python install required).

--

## Repository Setup

Initialize Git and push to GitHub:

```bash
cd path/to/SafeChat
git init
git add .
git commit -m "Initial commit of Roblox SafeChat Overlay v1.0.0"
git remote add origin https://github.com/<username>/roblox-safechat-overlay.git
git branch -M main
git push -u origin main
```

Include a `.gitignore` to skip build artifacts.

---

## Usage

1. Launch **RobloxSafeChatOverlay.exe**.
2. Drag the title bar to reposition.
3. Click the ▼ button to collapse/expand the phrase menu.
4. Use the 📌/📍 button to toggle always-on-top behavior.
5. Select a category, then choose a phrase to send it directly into Roblox chat.

---

## License

MIT © pointcastle
