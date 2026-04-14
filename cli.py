import sys
from hangman_logic import HangmanGame

def print_hangman(errors):
    stages = [
        """
           --------
           |      |
           |      
           |    
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |    
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |      |
           |      |
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     /|
           |      |
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     /|\\
           |      |
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     /|\\
           |      |
           |     /
           -
        """,
        """
           --------
           |      |
           |      O
           |     /|\\
           |      |
           |     / \\
           -
        """
    ]
    print(stages[errors])

def main():
    print("Welcome to Hangman!")
    mode = input("Select mode - (R)egular or (A)dversarial [Default: R]: ").strip().upper()
    is_adv = mode == 'A'
    
    game = HangmanGame(is_adversarial=is_adv)
    
    while not game.game_over:
        print("\n" + "="*30)
        print_hangman(game.wrong_guesses)
        print(f"Word: {game.get_display_pattern()}")
        print(f"Guessed letters: {', '.join(sorted(list(game.guessed_letters)))}")
        print(f"Errors: {game.wrong_guesses}/{game.max_errors}")
        
        guess = input("Enter a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single alphabetical character.")
            continue
            
        success, msg = game.guess(guess)
        if not success:
            print(msg)
        else:
            if guess in game.current_pattern:
                print("Good guess!")
            else:
                print("Wrong guess!")
                
    print("\n" + "="*30)
    print_hangman(game.wrong_guesses)
    if game.won:
        print(f"Congratulations! You won! The word was {game.get_display_pattern().replace(' ', '')}")
    else:
        print(f"Game Over. You ran out of lives. The word was: {game.get_answer()}")

if __name__ == "__main__":
    # Ensure graceful exit on KeyboardInterrupt
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting. Thanks for playing!")
        sys.exit(0)
