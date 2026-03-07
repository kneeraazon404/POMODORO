# Pomodoro & Goals Ledger 🍅

A sleek, modern desktop application built with Python and CustomTkinter. It combines a continuous-looping Pomodoro timer, virtual-desktop-persistent overlays, a daily task rollover system, and a local SQLite database to track your study hours and high-level goals.

## 🧠 About the Pomodoro Technique



The Pomodoro Technique is a time management method designed to break work down into highly focused, manageable intervals, separated by short breaks. 

### A Brief History
The technique was developed in the late 1980s by a university student named Francesco Cirillo. Struggling to focus on his studies, he grabbed a kitchen timer shaped like a tomato—*pomodoro* in Italian—and challenged himself to work completely uninterrupted for just 10 minutes. He refined the process into the 25-minute work / 5-minute break cycle that is famous today. 

### Core Benefits
* **Mitigates Burnout:** Frequent, scheduled breaks keep your brain fresh and prevent cognitive fatigue.
* **Builds a Sense of Urgency:** A ticking 25-minute clock forces you to tackle the task immediately rather than endlessly scrolling or procrastinating.
* **Handles Distractions:** When an interruption occurs, you quickly note it down and return to the timer. The break is your designated time to handle those distractions.
* **Improves Estimation:** By tracking how many "Pomodoros" a task takes, you become much better at estimating future workloads.

---

## 💻 Installation & Packaging Guide

To use this app without opening a code editor or running terminal commands every day, you can package it into a native standalone application (an `.exe` for Windows, a `.app` for macOS, or a binary for Linux). 

**Important Note:** You must package the app on the operating system you intend to use it on. You cannot build a Mac `.app` from a Windows machine!

### Step 1: Prerequisites (All Platforms)
Before packaging, ensure you have Python installed and your required libraries set up. Open your terminal or command prompt and run:
`pip install customtkinter pyinstaller`

*(Linux users may also need to install Tkinter via their package manager, e.g., `sudo apt-get install python3-tk`)*

### Step 2: Packaging for Windows
1. Open Command Prompt or PowerShell.
2. Navigate to the folder containing `pomodoro.py`.
3. Run the following command:
   `pyinstaller --noconsole --onefile pomodoro.py`
4. **The Result:** Inside the newly created `dist/` folder, you will find `pomodoro.exe`. 
5. **Next Step:** Move this `.exe` to a permanent folder, right-click it, select **Create shortcut**, and drag that shortcut into your Start Menu or Taskbar.

### Step 3: Packaging for macOS
1. Open the Terminal app.
2. Navigate to the folder containing `pomodoro.py`.
3. Run the following command:
   `pyinstaller --noconsole --windowed pomodoro.py`
   *(Note: macOS uses `--windowed` instead of `--onefile` to properly generate a Mac application bundle).*
4. **The Result:** Inside the `dist/` folder, you will find a `pomodoro.app` bundle.
5. **Next Step:** Drag and drop `pomodoro.app` into your Mac's **Applications** folder. You can now launch it from Launchpad or Spotlight.

### Step 4: Packaging for Linux
1. Open your Terminal.
2. Navigate to the folder containing `pomodoro.py`.
3. Run the following command:
   `pyinstaller --noconsole --onefile pomodoro.py`
4. **The Result:** Inside the `dist/` folder, you will find an executable binary named `pomodoro`.
5. **Next Step:** Move the binary to a desired location. You may need to ensure it has execution permissions by running `chmod +x pomodoro`. You can then create a `.desktop` file in `~/.local/share/applications/` to make it searchable in your app launcher.