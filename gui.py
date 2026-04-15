import tkinter as tk
from tkinter import messagebox
from hangman_logic import HangmanGame

TOTAL_PARTS = 19  # parts 0-18

class IOSToggle(tk.Canvas):
    def __init__(self, parent, command=None, on_color="#8b5cf6", *args, **kwargs):
        super().__init__(parent, width=50, height=26, bg="#0f172a", highlightthickness=0, *args, **kwargs)
        self.command = command
        self.is_on = False
        self.bg_off = "#334155"
        self.bg_on = on_color
        self.fg_color = "#ffffff"
        self.bind("<Button-1>", self.toggle)
        self.draw()

    def set_state(self, state):
        self.is_on = state
        self.draw()

    def draw(self):
        self.delete("all")
        bg_color = self.bg_on if self.is_on else self.bg_off
        self.create_line(13, 13, 37, 13, width=26, capstyle="round", fill=bg_color)
        knob_x = 37 if self.is_on else 13
        self.create_oval(knob_x-11, 2, knob_x+11, 24, fill=self.fg_color, outline="")

    def toggle(self, event=None):
        self.is_on = not self.is_on
        self.draw()
        if self.command:
            self.command(self.is_on)


class HangmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman")
        self.root.geometry("640x900")
        self.root.configure(bg="#0f172a")

        self.game = None
        self.is_adversarial = True
        self.god_mode = False
        self.max_errors = 10

        self.canvas = None
        self.word_label = None
        self.status_label = None
        self.record_label = None
        self.keyboard_frame = None
        self.keys = {}

        self.setup_ui()
        self.start_new_game()

    def setup_ui(self):
        # Header frame
        header_frame = tk.Frame(self.root, bg="#0f172a")
        header_frame.pack(pady=10, fill=tk.X, padx=20)

        title_frame = tk.Frame(header_frame, bg="#0f172a")
        title_frame.pack(side=tk.LEFT)

        title = tk.Label(title_frame, text="HANGMAN", font=("Outfit", 28, "bold"), fg="#60a5fa", bg="#0f172a")
        title.pack(side=tk.LEFT)

        self.record_label = tk.Label(title_frame, text="Record: 0/0", font=("Outfit", 12, "bold"), fg="#f8fafc", bg="#0f172a")
        self.record_label.pack(side=tk.LEFT, padx=15)

        # Toggles Frame (right side)
        toggles_frame = tk.Frame(header_frame, bg="#0f172a")
        toggles_frame.pack(side=tk.RIGHT)

        # Always Win Toggle
        god_frame = tk.Frame(toggles_frame, bg="#0f172a")
        god_frame.pack(anchor=tk.E, pady=2)
        tk.Label(god_frame, text="Always Win", fg="#94a3b8", bg="#0f172a", font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)
        self.god_toggle = IOSToggle(god_frame, command=self.set_god_mode, on_color="#f59e0b")
        self.god_toggle.pack(side=tk.LEFT)

        # Mode Toggle
        mode_frame = tk.Frame(toggles_frame, bg="#0f172a")
        mode_frame.pack(anchor=tk.E, pady=2)
        tk.Label(mode_frame, text="Regular", fg="#94a3b8", bg="#0f172a", font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)
        self.mode_toggle = IOSToggle(mode_frame, command=self.set_adv_mode, on_color="#8b5cf6")
        self.mode_toggle.set_state(True)
        self.mode_toggle.pack(side=tk.LEFT)
        tk.Label(mode_frame, text="Adversarial", fg="#94a3b8", bg="#0f172a", font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)

        # Guesses Spinbox
        guesses_frame = tk.Frame(toggles_frame, bg="#0f172a")
        guesses_frame.pack(anchor=tk.E, pady=2)
        tk.Label(guesses_frame, text="Guesses:", fg="#94a3b8", bg="#0f172a", font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)
        self.guesses_var = tk.IntVar(value=10)
        guesses_spin = tk.Spinbox(
            guesses_frame, from_=6, to=TOTAL_PARTS, textvariable=self.guesses_var,
            width=4, font=("Outfit", 11, "bold"), bg="#1e293b", fg="white",
            buttonbackground="#334155", relief=tk.FLAT, command=self.on_guesses_change
        )
        guesses_spin.pack(side=tk.LEFT)

        # Canvas for Hangman (taller to fit all parts)
        self.canvas = tk.Canvas(self.root, width=220, height=270, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(pady=5)
        self.draw_scaffold()

        # Word Display
        self.word_label = tk.Label(self.root, text="", font=("Courier", 24, "bold"), fg="#f8fafc", bg="#0f172a")
        self.word_label.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(self.root, text="Ready to play?", font=("Outfit", 16), fg="#f8fafc", bg="#0f172a")
        self.status_label.pack(pady=5)

        # Keyboard Frame
        self.keyboard_frame = tk.Frame(self.root, bg="#0f172a")
        self.keyboard_frame.pack(pady=8)
        self.build_keyboard()

        # Bottom Controls
        self.bottom_frame = tk.Frame(self.root, bg="#0f172a")
        self.bottom_frame.pack(pady=10)

        self.next_btn = tk.Button(
            self.bottom_frame, text="Next Word", font=("Outfit", 13, "bold"),
            bg="#10b981", fg="black", relief=tk.FLAT, padx=12, pady=6,
            command=self.start_new_game
        )
        # next_btn initially hidden

        self.refresh_btn = tk.Button(
            self.bottom_frame, text="🔄 Refresh", font=("Outfit", 13, "bold"),
            bg="#334155", fg="white", relief=tk.FLAT, padx=12, pady=6,
            command=self.refresh_action
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=10)

        # Key bindings
        self.root.bind('<Key>', self.handle_keypress)

    def on_guesses_change(self):
        val = self.guesses_var.get()
        val = max(6, min(TOTAL_PARTS, val))
        self.guesses_var.set(val)
        self.max_errors = val
        self.refresh_action()

    def set_god_mode(self, is_on):
        self.god_mode = is_on
        if self.game:
            self.game.god_mode = is_on
            self.game._check_end()
            self.update_ui()

    def set_adv_mode(self, is_adv):
        self.is_adversarial = is_adv
        self.refresh_action()

    def refresh_action(self):
        if self.game:
            self.game.is_adversarial = self.is_adversarial
            self.game.god_mode = self.god_mode
            self.game.max_errors = self.max_errors
            self.game.refresh()
            self.reset_ui_for_new_game()

    def start_new_game(self):
        if self.game is None:
            self.game = HangmanGame(
                is_adversarial=self.is_adversarial,
                god_mode=self.god_mode,
                max_errors=self.max_errors
            )
        else:
            self.game.is_adversarial = self.is_adversarial
            self.game.god_mode = self.god_mode
            self.game.max_errors = self.max_errors
            self.game.start_game()
        self.reset_ui_for_new_game()

    def reset_ui_for_new_game(self):
        self.draw_scaffold()
        self.update_ui()
        self.status_label.config(text="Ready to play!", fg="#f8fafc")
        for btn in self.keys.values():
            btn.config(state=tk.NORMAL, bg="#1e293b", fg="white")
        self.next_btn.pack_forget()
        if not self.refresh_btn.winfo_ismapped():
            self.refresh_btn.pack(side=tk.LEFT, padx=10)

    def draw_scaffold(self):
        c = self.canvas
        c.delete("all")
        # Base
        c.create_line(20, 245, 105, 245, width=4, fill="#94a3b8", capstyle=tk.ROUND)
        # Vertical post
        c.create_line(62, 245, 62, 20, width=4, fill="#94a3b8", capstyle=tk.ROUND)
        # Horizontal beam
        c.create_line(62, 20, 145, 20, width=4, fill="#94a3b8", capstyle=tk.ROUND)
        # Rope drop
        c.create_line(145, 20, 145, 52, width=4, fill="#94a3b8", capstyle=tk.ROUND)

    def draw_hangman(self, errors):
        c = self.canvas
        col = "#ef4444"

        # Center of head
        hx, hy, hr = 145, 72, 20

        # 0: Head (full circle)
        if errors >= 1:
            c.create_oval(hx-hr, hy-hr, hx+hr, hy+hr, width=4, outline=col)
        # 1: Body
        if errors >= 2:
            c.create_line(hx, hy+hr, hx, 165, width=4, fill=col, capstyle=tk.ROUND)
        # 2: Left Ear
        if errors >= 3:
            c.create_oval(hx-hr-8, hy-7, hx-hr, hy+7, width=3, outline=col)
        # 3: Right Ear
        if errors >= 4:
            c.create_oval(hx+hr, hy-7, hx+hr+8, hy+7, width=3, outline=col)
        # 4: Left Eye
        if errors >= 5:
            c.create_oval(hx-10, hy-10, hx-4, hy-4, width=3, outline=col)
        # 5: Right Eye
        if errors >= 6:
            c.create_oval(hx+4, hy-10, hx+10, hy-4, width=3, outline=col)
        # 6: Nose
        if errors >= 7:
            c.create_line(hx, hy-2, hx, hy+6, width=3, fill=col, capstyle=tk.ROUND)
        # 7: Mouth (arc approximated with a curve)
        if errors >= 8:
            c.create_arc(hx-10, hy+2, hx+10, hy+18, start=200, extent=140, style=tk.ARC, width=3, outline=col)
        # 8: Hair (3 strands)
        if errors >= 9:
            c.create_line(hx-12, hy-hr+2, hx-15, hy-hr-8, width=3, fill=col, capstyle=tk.ROUND)
            c.create_line(hx,    hy-hr,   hx,    hy-hr-9, width=3, fill=col, capstyle=tk.ROUND)
            c.create_line(hx+12, hy-hr+2, hx+15, hy-hr-8, width=3, fill=col, capstyle=tk.ROUND)
        # 9: Left Arm
        if errors >= 10:
            c.create_line(hx, 110, hx-35, 135, width=4, fill=col, capstyle=tk.ROUND)
        # 10: Right Arm
        if errors >= 11:
            c.create_line(hx, 110, hx+35, 135, width=4, fill=col, capstyle=tk.ROUND)
        # 11: Left Hand
        if errors >= 12:
            c.create_oval(hx-43, 130, hx-33, 140, width=3, outline=col)
        # 12: Right Hand
        if errors >= 13:
            c.create_oval(hx+33, 130, hx+43, 140, width=3, outline=col)
        # 13: Left Leg
        if errors >= 14:
            c.create_line(hx, 165, hx-28, 208, width=4, fill=col, capstyle=tk.ROUND)
        # 14: Right Leg
        if errors >= 15:
            c.create_line(hx, 165, hx+28, 208, width=4, fill=col, capstyle=tk.ROUND)
        # 15: Left Foot
        if errors >= 16:
            c.create_line(hx-28, 208, hx-44, 214, width=4, fill=col, capstyle=tk.ROUND)
        # 16: Right Foot
        if errors >= 17:
            c.create_line(hx+28, 208, hx+44, 214, width=4, fill=col, capstyle=tk.ROUND)
        # 17: Left Toes
        if errors >= 18:
            for dx in [-38, -43, -48]:
                c.create_line(hx+dx, 214, hx+dx, 222, width=3, fill=col, capstyle=tk.ROUND)
        # 18: Right Toes
        if errors >= 19:
            for dx in [38, 43, 48]:
                c.create_line(hx+dx, 214, hx+dx, 222, width=3, fill=col, capstyle=tk.ROUND)

        # Always-Win halo (dashed golden ring around head)
        if errors >= self.max_errors and self.god_mode:
            c.create_oval(hx-hr-12, hy-hr-12, hx+hr+12, hy+hr+12,
                          width=2, outline="#f59e0b", dash=(5, 4))

    def build_keyboard(self):
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()
        letters = 'abcdefghijklmnopqrstuvwxyz'
        self.keys = {}
        for i, char in enumerate(letters):
            row = i // 7
            col = i % 7
            btn = tk.Button(
                self.keyboard_frame, text=char.upper(), width=4, height=2,
                font=("Outfit", 11, "bold"), bg="#1e293b", fg="white",
                relief=tk.FLAT,
                command=lambda c=char: self.handle_guess(c)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.keys[char] = btn

    def handle_keypress(self, event):
        char = event.char.lower()
        if char.isalpha() and len(char) == 1:
            self.handle_guess(char)

    def handle_guess(self, char):
        if not self.game or self.game.game_over:
            return
        success, msg = self.game.guess(char)
        if success:
            btn = self.keys.get(char)
            if btn:
                btn.config(state=tk.DISABLED)
                btn.config(bg="#10b981" if char in self.game.current_pattern else "#ef4444")
            self.update_ui()
            if self.game.game_over:
                self.end_game()

    def update_ui(self):
        self.word_label.config(text=self.game.get_display_pattern())
        self.draw_scaffold()
        self.draw_hangman(self.game.wrong_guesses)
        self.record_label.config(text=f"Record: {self.game.games_won}/{self.game.games_played}")

    def end_game(self):
        for btn in self.keys.values():
            btn.config(state=tk.DISABLED)
        self.update_ui()
        if self.game.won:
            self.status_label.config(text="You Win! 🎉", fg="#10b981")
        else:
            answer = self.game.get_answer()
            self.status_label.config(text=f"Game Over. Word was: {answer}", fg="#ef4444")

        self.next_btn.pack(side=tk.LEFT, padx=10)
        self.refresh_btn.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = HangmanGUI(root)
    root.mainloop()
