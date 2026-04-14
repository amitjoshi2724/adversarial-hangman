import tkinter as tk
from tkinter import messagebox
from hangman_logic import HangmanGame

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
        self.root.geometry("600x800")
        self.root.configure(bg="#0f172a")
        
        self.game = None
        self.is_adversarial = False
        self.god_mode = False
        
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
        
        # Record
        self.record_label = tk.Label(title_frame, text="Record: 0/0", font=("Outfit", 12, "bold"), fg="#f8fafc", bg="#0f172a")
        self.record_label.pack(side=tk.LEFT, padx=15)
        
        # Toggles Frame
        toggles_frame = tk.Frame(header_frame, bg="#0f172a")
        toggles_frame.pack(side=tk.RIGHT)
        
        # Top Toggle: God Mode
        god_frame = tk.Frame(toggles_frame, bg="#0f172a")
        god_frame.pack(anchor=tk.E, pady=2)
        tk.Label(god_frame, text="God Mode", fg="#94a3b8", bg="#0f172a", font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)
        self.god_toggle = IOSToggle(god_frame, command=self.set_god_mode, on_color="#f59e0b")
        self.god_toggle.pack(side=tk.LEFT)
        
        # Bottom Toggle: Mode
        mode_frame = tk.Frame(toggles_frame, bg="#0f172a")
        mode_frame.pack(anchor=tk.E, pady=2)
        tk.Label(mode_frame, text="Regular", fg="#94a3b8", bg="#0f172a", font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)
        self.mode_toggle = IOSToggle(mode_frame, command=self.set_adv_mode, on_color="#8b5cf6")
        self.mode_toggle.pack(side=tk.LEFT)
        tk.Label(mode_frame, text="Adversarial", fg="#94a3b8", bg="#0f172a", font=("Outfit", 10)).pack(side=tk.LEFT, padx=5)
        
        # Canvas for Hangman
        self.canvas = tk.Canvas(self.root, width=200, height=250, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.draw_scaffold()
        
        # Word Display
        self.word_label = tk.Label(self.root, text="", font=("Courier", 24, "bold"), fg="#f8fafc", bg="#0f172a")
        self.word_label.pack(pady=15)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Ready to play?", font=("Outfit", 16), fg="#f8fafc", bg="#0f172a")
        self.status_label.pack(pady=5)
        
        # Keyboard Frame
        self.keyboard_frame = tk.Frame(self.root, bg="#0f172a")
        self.keyboard_frame.pack(pady=10)
        self.build_keyboard()
        
        # Bottom Controls
        self.bottom_frame = tk.Frame(self.root, bg="#0f172a")
        self.bottom_frame.pack(pady=10)
        
        self.next_btn = tk.Button(self.bottom_frame, text="Next Word", font=("Outfit", 14, "bold"), bg="#10b981", fg="black", command=self.start_new_game)
        self.next_btn.pack(side=tk.LEFT, padx=10)
        
        self.refresh_btn = tk.Button(self.bottom_frame, text="🔄 Refresh", font=("Outfit", 14, "bold"), bg="#334155", fg="white", command=self.refresh_action)
        self.refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # Key bindings
        self.root.bind('<Key>', self.handle_keypress)

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
            self.game.refresh()
            self.record_label.config(text=f"Record: {self.game.games_won}/{self.game.games_played}")
            self.reset_ui_for_new_game()

    def start_new_game(self):
        if self.game is None:
            self.game = HangmanGame(is_adversarial=self.is_adversarial, god_mode=self.god_mode)
        else:
            self.game.is_adversarial = self.is_adversarial
            self.game.god_mode = self.god_mode
            self.game.start_game()
        
        self.reset_ui_for_new_game()

    def reset_ui_for_new_game(self):
        self.draw_scaffold()
        self.update_ui()
        self.status_label.config(text="Ready to play!", fg="#f8fafc")
        
        for btn in self.keys.values():
            btn.config(state=tk.NORMAL, bg="#1e293b", fg="black")
            
        self.next_btn.pack_forget()

    def draw_scaffold(self):
        self.canvas.delete("all")
        self.canvas.create_line(20, 230, 100, 230, width=4, fill="#94a3b8")
        self.canvas.create_line(60, 230, 60, 20, width=4, fill="#94a3b8")
        self.canvas.create_line(60, 20, 140, 20, width=4, fill="#94a3b8")
        self.canvas.create_line(140, 20, 140, 50, width=4, fill="#94a3b8")

    def draw_hangman(self, errors):
        colors = "#ef4444"
        if errors >= 1: self.canvas.create_oval(120, 50, 160, 90, width=4, outline=colors)
        if errors >= 2: self.canvas.create_line(140, 90, 140, 150, width=4, fill=colors)
        if errors >= 3: self.canvas.create_line(140, 100, 110, 130, width=4, fill=colors)
        if errors >= 4: self.canvas.create_line(140, 100, 170, 130, width=4, fill=colors)
        if errors >= 5: self.canvas.create_line(140, 150, 110, 190, width=4, fill=colors)
        if errors >= 6: self.canvas.create_line(140, 150, 170, 190, width=4, fill=colors)
        
        # Let users know God mode is saving them visually
        if errors >= 6 and self.god_mode:
            self.canvas.create_oval(115, 45, 165, 95, width=2, outline="#f59e0b", dash=(4, 4)) # halo

    def build_keyboard(self):
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()
            
        letters = 'abcdefghijklmnopqrstuvwxyz'
        self.keys = {}
        for i, char in enumerate(letters):
            row = i // 7
            col = i % 7
            btn = tk.Button(self.keyboard_frame, text=char.upper(), width=4, height=2,
                            font=("Outfit", 12, "bold"), bg="#1e293b", fg="black",
                            command=lambda c=char: self.handle_guess(c))
            btn.grid(row=row, column=col, padx=3, pady=3)
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
            btn = self.keys[char]
            btn.config(state=tk.DISABLED)
            
            if char in self.game.current_pattern:
                btn.config(bg="#10b981")
            else:
                btn.config(bg="#ef4444")
                
            self.update_ui()
            
            if self.game.game_over:
                self.end_game()

    def update_ui(self):
        self.word_label.config(text=self.game.get_display_pattern())
        self.draw_scaffold() # clear and redraw
        self.draw_hangman(self.game.wrong_guesses)
        self.record_label.config(text=f"Record: {self.game.games_won}/{self.game.games_played}")

    def end_game(self):
        for btn in self.keys.values():
            btn.config(state=tk.DISABLED)
            
        self.update_ui() # Ensure streak updates immediately
        
        if self.game.won:
            self.status_label.config(text="You Win!", fg="#10b981")
        else:
            answer = self.game.get_answer()
            self.status_label.config(text=f"Game Over. Word was: {answer}", fg="#ef4444")
            
        self.next_btn.pack(side=tk.LEFT, padx=10) # show next word button

if __name__ == "__main__":
    root = tk.Tk()
    app = HangmanGUI(root)
    root.mainloop()
