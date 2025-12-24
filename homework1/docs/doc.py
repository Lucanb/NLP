import os

os.makedirs("docs", exist_ok=True)

# --- README.md ---
readme_content = r'''# Word Association Game

## Project Structure

background.gif        "Animated background for GUI"
game_history.json     "Stores previous game history"
game.py               "Core game logic (WordNet functions)"
main.py               "GUI entry point for the game"
ui.py                 "Optional GUI utilities"
lab1.py               "Additional scripts (if any)"
env/                  "Virtual environment for dependencies"
__pycache__/          "Python cache files"
docs/                 "Documentation folder"

---

## Requirements
- Python 3.9+
- tkinter
- nltk
- Pillow

### NLTK Data
Make sure you have downloaded WordNet and lemmatizer data:

import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')

### Running the Game

Activate your virtual environment if available:

Linux/macOS:
source env/bin/activate

Windows:
.\env\Scripts\activate

Run the main GUI:
python main.py

Use the GUI buttons to start the game, check history, view About info, or quit.
'''

with open("docs/README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

# --- GAME_DOC.md ---
game_doc_content = r'''# Game Logic Documentation

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
'''

with open("docs/GAME_DOC.md", "w", encoding="utf-8") as f:
    f.write(game_doc_content)

# --- GUI_DOC.md ---
gui_doc_content = r'''# GUI Documentation

This document explains the GUI implementation in main.py.

## WordGameGUI(master)
Handles main menu, game rounds, history, and About info. Uses tkinter for GUI components.

## Main Components
- Canvas with animated or static background
- Word display label
- Entry box for guesses
- SEND button
- Feedback label
- Score label

## Main Menu Buttons
- Start Game
- History
- About
- Quit

## History Window
Shows previous game scores and detailed rounds.

## About Window
Shows game instructions and information.
'''

with open("docs/GUI_DOC.md", "w", encoding="utf-8") as f:
    f.write(gui_doc_content)

print("All documentation files created successfully in docs/")
