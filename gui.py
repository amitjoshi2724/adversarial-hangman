import random
import tkinter as tk
from hangman_logic import HangmanGame

TOTAL_PARTS = 26


class IOSToggle(tk.Canvas):
    def __init__(self, parent, command=None, on_color="#8b5cf6", *args, **kwargs):
        super().__init__(parent, width=50, height=26, bg="#0f172a", highlightthickness=0, *args, **kwargs)
        self.command  = command
        self.is_on    = False
        self.bg_off   = "#334155"
        self.bg_on    = on_color
        self.fg_color = "#ffffff"
        self.bind("<Button-1>", self.toggle)
        self.draw()

    def set_state(self, state):
        self.is_on = state
        self.draw()

    def draw(self):
        self.delete("all")
        bg = self.bg_on if self.is_on else self.bg_off
        self.create_line(13, 13, 37, 13, width=26, capstyle="round", fill=bg)
        kx = 37 if self.is_on else 13
        self.create_oval(kx-11, 2, kx+11, 24, fill=self.fg_color, outline="")

    def toggle(self, _=None):
        self.is_on = not self.is_on
        self.draw()
        if self.command:
            self.command(self.is_on)


class HangmanGUI:
    def __init__(self, root):
        self.root          = root
        self.root.title("Hangman")
        self.root.geometry("660x960")
        self.root.configure(bg="#0f172a")

        self.game          = None
        self.is_adversarial = True
        self.god_mode      = False
        self.max_errors    = 10

        self.canvas        = None
        self.word_label    = None
        self.status_label  = None
        self.record_label  = None
        self.lock_label    = None
        self.guesses_spin  = None
        self.keyboard_frame = None
        self.keys          = {}

        self.setup_ui()
        self.start_new_game()

    # ── UI Setup ──────────────────────────────────────────────────────────────
    def setup_ui(self):
        hdr = tk.Frame(self.root, bg="#0f172a")
        hdr.pack(pady=10, fill=tk.X, padx=20)

        left = tk.Frame(hdr, bg="#0f172a")
        left.pack(side=tk.LEFT)
        tk.Label(left, text="HANGMAN", font=("Outfit", 28, "bold"),
                 fg="#60a5fa", bg="#0f172a").pack(side=tk.LEFT)
        self.record_label = tk.Label(left, text="Record: 0/0",
                                     font=("Outfit", 12, "bold"),
                                     fg="#f8fafc", bg="#0f172a")
        self.record_label.pack(side=tk.LEFT, padx=15)

        right = tk.Frame(hdr, bg="#0f172a")
        right.pack(side=tk.RIGHT)

        # Always-Win toggle
        gf = tk.Frame(right, bg="#0f172a"); gf.pack(anchor=tk.E, pady=2)
        tk.Label(gf, text="Always Win", fg="#94a3b8", bg="#0f172a",
                 font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)
        self.god_toggle = IOSToggle(gf, command=self.set_god_mode, on_color="#f59e0b")
        self.god_toggle.pack(side=tk.LEFT)

        # Mode toggle
        mf = tk.Frame(right, bg="#0f172a"); mf.pack(anchor=tk.E, pady=2)
        tk.Label(mf, text="Regular",     fg="#94a3b8", bg="#0f172a",
                 font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)
        self.mode_toggle = IOSToggle(mf, command=self.set_adv_mode, on_color="#8b5cf6")
        self.mode_toggle.set_state(True)
        self.mode_toggle.pack(side=tk.LEFT)
        tk.Label(mf, text="Adversarial", fg="#94a3b8", bg="#0f172a",
                 font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)

        # Guesses spinbox
        guf = tk.Frame(right, bg="#0f172a"); guf.pack(anchor=tk.E, pady=2)
        self.guesses_label = tk.Label(guf, text="Guess Limit:", fg="#94a3b8", bg="#0f172a",
                 font=("Outfit", 10))
        self.guesses_label.pack(side=tk.LEFT, padx=5)
        self.guesses_var  = tk.IntVar(value=10)
        self.guesses_spin = tk.Spinbox(
            guf, from_=6, to=TOTAL_PARTS, textvariable=self.guesses_var,
            width=4, font=("Outfit", 11, "bold"),
            bg="#1e293b", fg="white", buttonbackground="#334155",
            relief=tk.FLAT, command=self.on_guesses_change
        )
        self.guesses_spin.pack(side=tk.LEFT)
        # Tooltip hint shown via title attribute (native OS tooltip)
        self.guesses_spin.config(cursor="question_arrow")

        # Hangman canvas
        self.canvas = tk.Canvas(self.root, width=230, height=280,
                                bg="#0f172a", highlightthickness=0)
        self.canvas.pack(pady=5)
        self.draw_scaffold()

        self.word_label = tk.Label(self.root, text="",
                                   font=("Courier", 24, "bold"),
                                   fg="#f8fafc", bg="#0f172a")
        self.word_label.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Ready to play?",
                                     font=("Outfit", 16), fg="#f8fafc", bg="#0f172a")
        self.status_label.pack(pady=5)

        self.keyboard_frame = tk.Frame(self.root, bg="#0f172a")
        self.keyboard_frame.pack(pady=8)
        self.build_keyboard()

        self.bottom_frame = tk.Frame(self.root, bg="#0f172a")
        self.bottom_frame.pack(pady=10)

        self.next_btn = tk.Button(
            self.bottom_frame, text="Next Word",
            font=("Outfit", 13, "bold"), bg="#10b981", fg="black",
            relief=tk.FLAT, padx=12, pady=6, command=self.start_new_game)

        self.refresh_btn = tk.Button(
            self.bottom_frame, text="🔄 Refresh",
            font=("Outfit", 13, "bold"), bg="#334155", fg="white",
            relief=tk.FLAT, padx=12, pady=6, command=self.refresh_action)
        self.refresh_btn.pack(side=tk.LEFT, padx=10)

        self.root.bind('<Key>', self.handle_keypress)

    # ── Guesses spinbox ───────────────────────────────────────────────────────
    def on_guesses_change(self):
        if self.game and self.game.guessed_letters:
            # revert
            self.guesses_var.set(self.max_errors)
            return
        val = max(6, min(TOTAL_PARTS, self.guesses_var.get()))
        self.guesses_var.set(val)
        self.max_errors = val
        if self.game:
            self.game.max_errors = val

    # ── Toggle callbacks ──────────────────────────────────────────────────────
    def set_god_mode(self, is_on):
        self.god_mode = is_on
        if self.game:
            self.game.god_mode = is_on
            self.game._check_end()
            self.update_ui()

    def set_adv_mode(self, is_adv):
        if not self.game:
            self.is_adversarial = is_adv
            return

        was_adv = self.is_adversarial
        self.is_adversarial = is_adv

        if not self.game.guessed_letters:
            # No guesses yet – just flip mode, no reset
            self.game.is_adversarial = is_adv
            if not is_adv:
                self.game.regular_word = random.choice(self.game.possible_words)
            return

        # Mid-game switch
        if not was_adv and is_adv:
            # Regular → Adversarial: recompute possible_words
            revealed      = set(l for l in self.game.current_pattern if l != '_')
            wrong_letters = self.game.guessed_letters - revealed
            self.game.possible_words = [
                w for w in self.game.dictionary
                if len(w) == self.game.word_length
                and all(w[i] == self.game.current_pattern[i]
                        for i in range(self.game.word_length)
                        if self.game.current_pattern[i] != '_')
                and not any(l in w for l in wrong_letters)
            ]
            self.game.is_adversarial = True
        elif was_adv and not is_adv:
            # Adversarial → Regular: commit a word from current possible set
            self.game.regular_word   = random.choice(self.game.possible_words)
            self.game.is_adversarial = False
        # No reset

    # ── Actions ───────────────────────────────────────────────────────────────
    def refresh_action(self):
        if self.game:
            self.game.is_adversarial = self.is_adversarial
            self.game.god_mode       = self.god_mode
            self.game.max_errors     = self.max_errors
            self.game.refresh()
            self.reset_ui_for_new_game()

    def start_new_game(self):
        if self.game is None:
            self.game = HangmanGame(
                is_adversarial=self.is_adversarial,
                god_mode=self.god_mode,
                max_errors=self.max_errors)
        else:
            self.game.is_adversarial = self.is_adversarial
            self.game.god_mode       = self.god_mode
            self.game.max_errors     = self.max_errors
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
        # Unlock spinbox
        self.guesses_spin.config(state='normal')
        self.guesses_label.config(text="Guess Limit:")

    # ── Drawing ───────────────────────────────────────────────────────────────
    def draw_scaffold(self):
        c = self.canvas; c.delete("all")
        c.create_line(20,  260, 110, 260, width=4, fill="#94a3b8", capstyle=tk.ROUND)
        c.create_line(65,  260, 65,  20,  width=4, fill="#94a3b8", capstyle=tk.ROUND)
        c.create_line(65,  20,  150, 20,  width=4, fill="#94a3b8", capstyle=tk.ROUND)
        c.create_line(150, 20,  150, 52,  width=4, fill="#94a3b8", capstyle=tk.ROUND)

    def draw_hangman(self, errors):
        c  = self.canvas
        cl = "#ef4444"
        hx, hy, hr = 150, 72, 20

        parts = [
            lambda: c.create_oval(hx-hr, hy-hr, hx+hr, hy+hr, width=4, outline=cl),        # 0 head
            lambda: c.create_line(hx, hy+hr, hx, 170, width=4, fill=cl, capstyle=tk.ROUND), # 1 body
            lambda: c.create_oval(hx-hr-9,hy-7,hx-hr,hy+7, width=3, outline=cl),            # 2 L ear
            lambda: c.create_oval(hx+hr,hy-7,hx+hr+9,hy+7, width=3, outline=cl),            # 3 R ear
            lambda: c.create_oval(hx-11,hy-10,hx-4,hy-3, width=3, outline=cl),              # 4 L eye
            lambda: c.create_oval(hx+4, hy-10,hx+11,hy-3, width=3, outline=cl),             # 5 R eye
            lambda: c.create_line(hx,hy-2,hx,hy+6, width=3, fill=cl, capstyle=tk.ROUND),    # 6 nose
            lambda: c.create_arc(hx-10,hy+3,hx+10,hy+18,start=200,extent=140,
                                 style=tk.ARC, width=3, outline=cl),                          # 7 mouth
            # 8 hair
            lambda: [c.create_line(hx-12,hy-hr+2,hx-15,hy-hr-9,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx,   hy-hr,   hx,   hy-hr-9,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx+12,hy-hr+2,hx+15,hy-hr-9,width=3,fill=cl,capstyle=tk.ROUND)],
            lambda: c.create_line(hx,115,hx-38,142, width=4, fill=cl, capstyle=tk.ROUND),   # 9  L arm
            lambda: c.create_line(hx,115,hx+38,142, width=4, fill=cl, capstyle=tk.ROUND),   # 10 R arm
            lambda: c.create_oval(hx-46,138,hx-36,148, width=3, outline=cl),                 # 11 L hand
            lambda: c.create_oval(hx+36,138,hx+46,148, width=3, outline=cl),                 # 12 R hand
            lambda: c.create_line(hx,170,hx-30,215, width=4, fill=cl, capstyle=tk.ROUND),   # 13 L leg
            lambda: c.create_line(hx,170,hx+30,215, width=4, fill=cl, capstyle=tk.ROUND),   # 14 R leg
            lambda: c.create_line(hx-30,215,hx-47,222, width=4,fill=cl,capstyle=tk.ROUND),  # 15 L foot
            lambda: c.create_line(hx+30,215,hx+47,222, width=4,fill=cl,capstyle=tk.ROUND),  # 16 R foot
            # 17 L toes
            lambda: [c.create_line(hx-41,222,hx-41,231,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx-45,222,hx-45,231,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx-49,222,hx-49,231,width=3,fill=cl,capstyle=tk.ROUND)],
            # 18 R toes
            lambda: [c.create_line(hx+41,222,hx+41,231,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx+45,222,hx+45,231,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx+49,222,hx+49,231,width=3,fill=cl,capstyle=tk.ROUND)],
            lambda: c.create_line(hx-12,hy-hr+10,hx-1,hy-hr+8,width=3,fill=cl,capstyle=tk.ROUND),# 19 L brow
            lambda: c.create_line(hx+1, hy-hr+8,hx+12,hy-hr+10,width=3,fill=cl,capstyle=tk.ROUND),#20 R brow
            # 21 L fingers
            lambda: [c.create_line(hx-43,148,hx-47,156,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx-40,149,hx-42,157,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx-37,148,hx-38,156,width=3,fill=cl,capstyle=tk.ROUND)],
            # 22 R fingers
            lambda: [c.create_line(hx+37,148,hx+38,156,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx+40,149,hx+42,157,width=3,fill=cl,capstyle=tk.ROUND),
                     c.create_line(hx+43,148,hx+47,156,width=3,fill=cl,capstyle=tk.ROUND)],
            lambda: c.create_oval(hx-4,128,hx+4,136, width=3, outline=cl),                   # 23 belly button
            lambda: c.create_oval(hx-38,188,hx-30,200, width=3, outline=cl),                  # 24 L knee
            lambda: c.create_oval(hx+30,188,hx+38,200, width=3, outline=cl),                  # 25 R knee
        ]

        for i, draw_fn in enumerate(parts):
            if errors >= i + 1:
                draw_fn()

        # Always-Win halo
        if errors >= self.max_errors and self.god_mode:
            c.create_oval(hx-hr-13, hy-hr-13, hx+hr+13, hy+hr+13,
                          width=2, outline="#f59e0b", dash=(5, 4))

    # ── Keyboard ──────────────────────────────────────────────────────────────
    def build_keyboard(self):
        for w in self.keyboard_frame.winfo_children():
            w.destroy()
        self.keys = {}
        for i, ch in enumerate('abcdefghijklmnopqrstuvwxyz'):
            btn = tk.Button(
                self.keyboard_frame, text=ch.upper(), width=4, height=2,
                font=("Outfit", 11, "bold"), bg="#1e293b", fg="white",
                relief=tk.FLAT,
                command=lambda c=ch: self.handle_guess(c))
            btn.grid(row=i//7, column=i%7, padx=2, pady=2)
            self.keys[ch] = btn

    def handle_keypress(self, event):
        ch = event.char.lower()
        if ch.isalpha() and len(ch) == 1:
            self.handle_guess(ch)

    def handle_guess(self, ch):
        if not self.game or self.game.game_over:
            return
        success, _ = self.game.guess(ch)
        if success:
            btn = self.keys.get(ch)
            if btn:
                btn.config(state=tk.DISABLED)
                btn.config(bg="#10b981" if ch in self.game.current_pattern else "#ef4444")

            # Lock spinbox after first guess
            if len(self.game.guessed_letters) == 1:
                self.guesses_spin.config(state='disabled')
                self.guesses_label.config(
                    text="Guess Limit — locked mid-game (enable Always Win for more room):")

            self.update_ui()
            if self.game.game_over:
                self.end_game()

    # ── State updates ─────────────────────────────────────────────────────────
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
    app  = HangmanGUI(root)
    root.mainloop()
