# Adversarial Hangman Suite

Welcome to the Adversarial Hangman Suite! This project offers a standard and adversarial game of Hangman across multiple platforms (Web, Python GUI, Python CLI). 

## 🎮 Game Modes

### 1. Regular Hangman
Classic Hangman. The computer picks a single word at the beginning of the game. If you guess a letter that is in the word, it's revealed. If not, your hangman is progressively drawn. Win by guessing all the letters before running out of lives (6)!

### 2. Adversarial Hangman
In this mode, the computer *sneaky* changes the word as you play to make it as hard as possible. 
Instead of choosing a definitive word at the start, the computer maintains a list of *all possible words*. Whenever you make a guess, the computer partitions the remaining words into groups based on where your guessed letter appears. It then forces the word to be whatever group contains the **most possible words**, effectively minimizing the information you gain! 

## 🌟 Extra Features

* **Record Tracking**: Keep track of your performance! We now track the total number of games won over the total games played (e.g. `Record: 5/7`). You can explicitly "Refresh" to abandon a game and quickly get a new word without penalizing your record.
* **God Mode**: A special toggle setting available in the Web UI and Python GUI that disables the "Lost" state. If you guess incorrectly 6 times, your hangman will turn gold but you can keep playing to figure out the word (though your record won't increment if you passed 6 errors)!

## 🚀 Running the Game

### 💻 1. Web Application

An elegant, screen-agnostic Web App with iOS-style toggles and CSS animations.

1. In your terminal, navigate to this project folder.
2. Run a local python server so the browser can securely read your `dict.txt`:
   ```bash
   python3 -m http.server 3000
   ```
3. Open `http://localhost:3000` in your favorite web browser.

### 🖼️ 2. Python GUI

A native Tkinter application mimicking the Web App's layout and custom iOS toggles. No dependencies required!

```bash
python3 gui.py
```

### ⌨️ 3. Command Line Interface

A clean terminal text-input version of the game.

```bash
python3 cli.py
```

---

## ☕ Support

If you enjoy the game and want to support its development, you can support me here: [https://ko-fi.com/amitjoshi2724](https://ko-fi.com/amitjoshi2724)!

---

*Good luck!*
