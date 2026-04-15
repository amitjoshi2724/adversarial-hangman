import random
import os

class HangmanGame:
    def __init__(self, dict_path='dict.txt', is_adversarial=True, god_mode=False, max_errors=10):
        self.is_adversarial = is_adversarial
        self.god_mode = god_mode
        self.max_errors = max_errors
        self.word_length = 0
        self.possible_words = []
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.current_pattern = []
        self.regular_word = ""
        self.game_over = False
        self.won = False
        self.games_won = 0
        self.games_played = 0
        
        # Load dictionary
        self.dictionary = self._load_dictionary(dict_path)
        if not self.dictionary:
            self.dictionary = ['apple', 'banana', 'orange', 'grape', 'peach']
        
        self.start_game()

    def _load_dictionary(self, dict_path):
        words = []
        if os.path.exists(dict_path):
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    w = line.strip().lower()
                    if w.isalpha():
                        words.append(w)
        return words

    def refresh(self):
        # Optional: could count as a loss, but we'll just skip adding to games_played
        self.start_game()

    def start_game(self):
        self.guessed_letters.clear()
        self.wrong_guesses = 0
        self.game_over = False
        self.won = False
        
        # Pick random word to determine length uniformly
        seed_word = random.choice(self.dictionary)
        self.word_length = len(seed_word)
        
        self.possible_words = [w for w in self.dictionary if len(w) == self.word_length]
        
        if not self.is_adversarial:
            self.regular_word = random.choice(self.possible_words)
            
        self.current_pattern = ['_'] * self.word_length

    def guess(self, letter):
        letter = letter.lower()
        if self.game_over or letter in self.guessed_letters or not letter.isalpha() or len(letter) != 1:
            return False, "Invalid or already guessed letter."
            
        self.guessed_letters.add(letter)
        hit = False
        
        if self.is_adversarial:
            groups = {}
            for word in self.possible_words:
                pattern = []
                for i in range(self.word_length):
                    if self.current_pattern[i] != '_':
                        pattern.append(self.current_pattern[i])
                    elif word[i] == letter:
                        pattern.append(letter)
                    else:
                        pattern.append('_')
                pattern_tuple = tuple(pattern)
                if pattern_tuple not in groups:
                    groups[pattern_tuple] = []
                groups[pattern_tuple].append(word)
                
            # Probabilistic adversarial selection
            alpha = 1.5
            patterns = list(groups.keys())
            raw_weights = [len(groups[p]) ** alpha for p in patterns]
            total_weight = sum(raw_weights)
            probabilities = [w / total_weight for w in raw_weights]
            
            # Debug logging
            print(f"--- Adversarial Selection (Alpha={alpha}) ---")
            for p, w, prob in zip(patterns, raw_weights, probabilities):
                pattern_display = "".join(p)
                print(f"Pattern: {pattern_display} | Size: {len(groups[p])} | Weight: {w:.2f} | Prob: {prob:.2%}")
            
            chosen_pattern = random.choices(patterns, weights=raw_weights, k=1)[0]
            self.possible_words = groups[chosen_pattern]
            
            for i in range(self.word_length):
                if chosen_pattern[i] == letter:
                    hit = True
                    self.current_pattern[i] = letter
        else:
            for i in range(self.word_length):
                if self.regular_word[i] == letter:
                    hit = True
                    self.current_pattern[i] = letter
                    
        if not hit:
            self.wrong_guesses += 1
            
        self._check_end()
        return True, "Hit!" if hit else "Miss!"

    def _check_end(self):
        if self.game_over: return
        
        if '_' not in self.current_pattern:
            self.game_over = True
            self.won = True
            self.games_won += 1
            self.games_played += 1
        elif self.wrong_guesses >= self.max_errors and not self.god_mode:
            self.game_over = True
            self.won = False
            self.games_played += 1

    def get_answer(self):
        if not self.game_over: return None
        if self.is_adversarial:
            return random.choice(self.possible_words)
        return self.regular_word

    def get_display_pattern(self):
        return " ".join(self.current_pattern)
