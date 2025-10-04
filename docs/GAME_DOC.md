# Game Logic Documentation

This document explains the functions defined in game.py, which handles the core mechanics of the Word Association Game.

## 1. get_similarity(word1, word2)
Purpose: Calculate semantic similarity between two words using WordNet.
Parameters:
- word1 (str): first word
- word2 (str): second word
Returns:
- float: maximum Wu-Palmer similarity score (0–1)
- None: if no valid synsets exist
Example:
from game import get_similarity
score = get_similarity("cat", "dog")
print(score)  # e.g., 0.857

## 2. get_random_word()
Purpose: Select a random alphabetic WordNet word with no underscores.
Returns: str – randomly selected word
Example:
from game import get_random_word
word = get_random_word()
print(word)  # e.g., "flower"

## 3. play_game(rounds=5, input_function=input, display_word=None, display_feedback=None, display_separator=None, display_final_score=None)
Purpose: Run the game in console mode. Tracks score, prevents duplicate guesses, and provides feedback.
Returns: tuple (score_total, history) where history is a list of dicts containing round info.
