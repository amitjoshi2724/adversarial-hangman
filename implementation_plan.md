# Plan: God Mode, Streak Tracking, and iOS Toggles

## Goal Description

You want to add several features to the games:
1. **Refresh Button**: A quick way to reset the current game.
2. **Streak Tracking**: A counter showing how many games you've won in a row without losing.
3. **"Can't Lose" Mode (God Mode)**: A mode where you simply can't lose (the hangman might fully draw, but the game won't end until you guess the word).
4. **iOS Toggle Sliders**: You want "God Mode" and the "Regular/Adversarial" switch to use nice, smooth iOS-style toggle sliders across both the Python GUI and Web App.

## Proposed Changes

### Core Logic (`hangman_logic.py`)
- **[MODIFY] hangman_logic.py**:
  - Add a `streak` counter that increments on a win and resets to `0` on a loss (unless in God Mode, where losses are impossible so the streak continues).
  - Add a `god_mode` flag. If `True`, the `_check_end()` function will not trigger a loss even if `wrong_guesses >= max_errors`.
  - Add a `refresh()` method that explicitly resets the board without resetting the streak if you explicitly refresh.

### Web Application (`index.html`, `style.css`, `script.js`)
- **[MODIFY] index.html & style.css**:
  - Add a "Streak: 0" label next to the game status.
  - Add a "God Mode" iOS-style toggle switch (using the CSS slider class we already have for the Adversarial switch).
  - Add a dedicated refresh/restart icon button near the header for immediate access instead of a large button at the bottom.
- **[MODIFY] script.js**:
  - Track `streak` across games.
  - Implement God Mode flag to prevent game over on 6 wrong guesses.

### Python GUI (`gui.py`)
- **[MODIFY] gui.py**:
  - Delete the explicit "Regular" and "Adversarial" segmented buttons.
  - Create a custom Tkinter `Canvas`-based class called `IOSToggle` that draws a beautiful, animated iOS switch.
  - Instantiate two `IOSToggle` switches: One for Regular/Adversarial, one for God Mode.
  - Add a Streak label to the header.
  - Add a "Refresh 🔄" button next to the streak label.

## User Review Required

> [!IMPORTANT]  
> In Tkinter, creating a smooth native-looking iOS toggle slider requires custom drawing on a `Canvas`. It will look great, but I just want to confirm you're okay with this custom implementation for the Python GUI since it does not come with a built-in iOS toggle.
> 
> Also, if you use a "Refresh" button in the middle of a game, should it count as a loss and reset your streak? (Usually, abandoning a game resets the streak). For now, I will assume refreshing a played game resets the streak unless you haven't made any guesses yet. Please confirm!

## Verification Plan

### Manual Verification
1. I will boot up both the Web UI and Python GUI and verify that the toggles look and animate like an iOS slider.
2. I will intentionally guess incorrectly > 6 times in God Mode to verify the game continues.
3. I will win 2 games to verify the streak increases to 2.
