# Adversarial / Regular Hangman Implementation Complete!

I've completed the implementation of the Adversarial and Regular Hangman games across three different platforms: Web, Python CLI, and Python GUI. 

## Features Overview

1. **Web UI** (`index.html`, `style.css`, `script.js`)
    * Fully screen-agnostic layout using responsive CSS units (`vw`, `vh`, `%`, `flexbox`).
    * Beautiful dark mode aesthetic with glassmorphism elements, CSS animations (pop-ins when a letter is revealed, smooth fading for the drawing), and clear success/error state colors.
    * Toggle switch dynamically changes the rules between Regular and Adversarial Hangman.
    * Includes both an on-screen keyboard and physical keyboard support!
    * **Note**: Due to browser CORS policies, if you want `dict.txt` to be loaded dynamically rather than falling back to the default fruit list, you should run a local server in the directory. (e.g. `python3 -m http.server`). Then open `http://localhost:8000` in your browser.

2. **Core Python Logic** (`hangman_logic.py`)
    * Reusable modular class `HangmanGame` handling adversarial logic (grouping, tie-breaking uniformly randomly as requested) and determining states. 

3. **Python Graphical UI** (`gui.py`)
    * Built using python's built-in `tkinter` to eliminate dependencies.
    * Fully operational visual canvas, similar game loop to the Web app.

4. **Python Command Line** (`cli.py`)
    * Terminal-rendered ASCII art for the Hangman.
    * Type-to-guess functionality.

> [!TIP]
> The dictionary fetching defaults to an internal fallback array if `dict.txt` is missing. Whenever you upload your `dict.txt` into the `/Users/amitjoshi2724/Desktop/adversarial-hangman` folder, the game should automatically load it upon restarting!

## Visual Testing Demo
Below is a video of our agent validating the Web UI in both Regular and Adversarial game modes:

![Browser Test validation](/Users/amitjoshi2724/.gemini/antigravity/brain/fccbebad-1ef3-4a78-906b-5f7f05948af0/hangman_ui_test_1776181375568.webp)

## Launching Instructions

### Web App:
```bash
cd /Users/amitjoshi2724/Desktop/adversarial-hangman
python3 -m http.server 3000
# Then visit http://localhost:3000 in your browser
```

### Python CLI:
```bash
python3 cli.py
```

### Python GUI:
```bash
python3 gui.py
```
