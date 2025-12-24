# Word Association Game

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
