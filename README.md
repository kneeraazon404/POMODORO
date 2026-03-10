# 🍅 POMODORO

> A focused Pomodoro timer with goal tracking, daily tasks, and session history.  
> Cross-platform · Dark & Light themes · SQLite persistence

---

## Features

| | |
|---|---|
| 🍅 Pomodoro timer | Study / Break auto-cycling |
| 🎯 Goal cards | Yearly / Quarterly / Monthly / Weekly with full CRUD |
| ✅ Daily tasks | Add, complete, and carry-over tasks |
| 📅 Ledger | Review any past day's study time and tasks |
| ☀️🌙 Theme toggle | One-click dark / light switch from any page |
| 🖥️ Mini timer | Floating, draggable, resizable overlay |

---

## Requirements

| Package | Version |
|---|---|
| Python | ≥ 3.10 |
| customtkinter | ≥ 5.2 |
| Pillow | ≥ 10.0 |

---

## Installation

### 🐧 Arch Linux (via PKGBUILD)

```bash
sudo pacman -S python python-pip noto-fonts
makepkg -si
```

Launch with:

```bash
pomodoro
```

### 🐧 Debian / Ubuntu

```bash
sudo apt update && sudo apt install -y python3 python3-pip fonts-noto
pip install customtkinter pillow
python main.py
```

### 🍎 macOS

```bash
brew install python
pip3 install customtkinter pillow
python3 main.py
```

> **Font note:** macOS uses *SF Pro Display* automatically.

### 🪟 Windows

```powershell
pip install customtkinter pillow
python main.py
```

> **Font note:** Windows uses *Segoe UI* automatically.

---

## Running in Development

```bash
git clone https://github.com/kneeraazon/POMODORO.git
cd POMODORO

# Option A – uv (recommended)
pip install uv
uv venv && source .venv/bin/activate
uv pip install customtkinter pillow

# Option B – standard venv
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install customtkinter pillow

python main.py
```

---

## Project Structure

```
POMODORO/
├── main.py                      # Entry point
├── pyproject.toml               # Project metadata and dependencies
├── PKGBUILD                     # Arch Linux package script
├── app/
│   ├── config.py                # Palettes, font resolver, theme switcher
│   ├── database.py              # SQLite data-access layer
│   └── ui/
│       ├── app.py               # Root window, sidebar, routing
│       ├── pages/
│       │   ├── dashboard.py     # Goal cards (CRUD) + stats
│       │   └── timer.py         # Pomodoro timer + task list
│       └── widgets/
│           └── mini_timer.py    # Floating mini timer overlay
└── assets/
    ├── icon.png                 # App icon (all platforms)
    └── pomodoro.desktop         # Linux desktop entry
```

> The `data/` directory (SQLite database) is created automatically on first launch and is not tracked by git.

---

## License

MIT © [kneeraazon](https://github.com/kneeraazon)
