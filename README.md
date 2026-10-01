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

## 📲 Install as an App & Play Offline (Mac, iOS & Android)

**Adversarial Hangman** is built as a full **Progressive Web App (PWA)** powered by a dedicated **Service Worker (`sw.js`)** and Web App Manifest (`manifest.json`). 

Once installed to your desktop or smartphone:
- ✈️ **100% Offline Playable:** All game logic, vocabulary dictionaries (`dict.txt`), minimax partitions, animations, and custom UI components are pre-cached directly to persistent device storage via the **Cache Storage API**. You can play in Airplane Mode with zero Wi-Fi or cellular data anytime, anywhere.
- 🖥️ **Native Standalone Window:** Launches in its own dedicated window without browser address bars, URL fields, or tabs.
- 🔄 **Zero-Hassle Background Updates:** When you connect to Wi-Fi, the Service Worker automatically fetches and updates any new changes pushed to GitHub.

### 🍎 Mac (macOS Desktop App)

You can install **Adversarial Hangman** directly as a native macOS desktop application with its own dedicated window, Dock icon, and full offline support:

#### Method A: Safari (macOS Sonoma / Sequoia or newer)
1. Open **[https://amitjoshi2724.github.io/adversarial-hangman/](https://amitjoshi2724.github.io/adversarial-hangman/)** in **Safari**.
2. In the top menu bar, click **File** > **Add to Dock...** (or click the **Share** button in the Safari toolbar and select **Add to Dock**).
3. Name it **Adversarial Hangman** and click **Add**.
4. The app is saved to your `Applications` folder and pinned to your **macOS Dock**.
5. Launch it like any native Mac app—it runs in its own window without browser tabs or address bars, supports full keyboard controls, and is 100% playable offline!

#### Method B: Google Chrome, Brave, or Microsoft Edge
1. Open **[https://amitjoshi2724.github.io/adversarial-hangman/](https://amitjoshi2724.github.io/adversarial-hangman/)** in **Chrome**, **Brave**, or **Edge**.
2. Click the **Install Adversarial Hangman** icon in the right side of the address/URL bar (or go to **Settings (⋮)** > **Save and share** > **Install Adversarial Hangman...**).
3. Click **Install**.
4. The game opens in its own standalone desktop window and is added to your Mac's **Launchpad**, **Spotlight**, and `~/Applications/Chrome Apps` folder.

### 🍏 iPhone & iPad (iOS Safari)
1. Open **[https://amitjoshi2724.github.io/adversarial-hangman/](https://amitjoshi2724.github.io/adversarial-hangman/)** in **Safari**.
2. Tap the **Share** button at the bottom of the screen (the square with an arrow pointing upward).
3. Scroll down the share sheet and tap **"Add to Home Screen"**.
4. Tap **Add** in the top-right corner. A dedicated Hangman icon will appear on your home screen.
5. Tap the new icon once while online to let the Service Worker cache all assets and the entire dictionary—after that, it is permanently playable offline in airplane mode!

### 🤖 Android (Google Chrome)
1. Open **[https://amitjoshi2724.github.io/adversarial-hangman/](https://amitjoshi2724.github.io/adversarial-hangman/)** in **Google Chrome**.
2. Tap the **three-dots menu (⋮)** in the top-right corner.
3. Tap **"Install app"** or **"Add to Home screen"**.
4. Confirm the prompt by tapping **Install**. The game will install to your app drawer and home screen as a standalone application.

---

## ☕ Support

If you enjoy the game and want to support its development, you can support me here: [https://ko-fi.com/amitjoshi2724](https://ko-fi.com/amitjoshi2724)!

---

*Good luck!*
