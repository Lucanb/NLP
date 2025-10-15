import random
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

def get_similarity(word1, word2):
    """
    Calculate the maximum Wu-Palmer similarity between two words using WordNet.
    Returns None if no similarity is found.
    """
    syns1 = wn.synsets(word1)
    syns2 = wn.synsets(word2)
    if not syns1 or not syns2:
        return None
    max_score = 0
    for s1 in syns1:
        for s2 in syns2:
            score = s1.wup_similarity(s2)
            if score and score > max_score:
                max_score = score
    return max_score

def get_random_word():
    """
    Return a random single-word lemma from WordNet (alphabetic only, no underscores).
    """
    all_lemmas = [lemma.name() for syn in wn.all_synsets() for lemma in syn.lemmas()]
    filtered = [w for w in all_lemmas if "_" not in w and w.isalpha()]
    return random.choice(filtered)

def play_game(rounds=5, input_function=input, display_word=None, display_feedback=None,
              display_separator=None, display_final_score=None):
    """
    Play a word association game in console or GUI mode.

    Arguments:
        rounds: number of rounds to play
        input_function: function to get user input
        display_word: function(word, round) to display the starting word
        display_feedback: function(feedback) to display feedback
        display_separator: function() to show separator between rounds
        display_final_score: function(score) to show final score

    Returns:
        score_total: total score accumulated
        history: list of dicts containing round history
                 [{"round": r, "word": word, "guess": guess, "points": points, "feedback": feedback}]
    """
    score_total = 0
    used_words = set()
    history = []

    for r in range(1, rounds + 1):
        word = get_random_word()
        if display_word:
            display_word(word, r)
        else:
            print(f"\nRound {r}: Starting word → {word.upper()}")

        guess = input_function("Type a related word (or 'exit' to quit): ").strip().lower()
        if guess == "exit":
            break

        lemma_guess = lemmatizer.lemmatize(guess)

        if guess in used_words or lemma_guess in used_words:
            points = 0
            feedback = f"❌ You already used '{guess}' → 0 points!"
        else:
            score = get_similarity(word, guess)
            if score is None:
                points = 0
                feedback = f"❌ No valid relation between '{word}' and '{guess}' → 0 points!"
            else:
                points = int(score * 100)
                if score > 0.8:
                    feedback = f"🔥 Excellent match! +{points}"
                elif score > 0.5:
                    feedback = f"👍 Good association +{points}"
                elif score > 0.2:
                    feedback = f"🤔 Weak relation +{points}"
                else:
                    feedback = f"❌ Almost no connection +{points}"
                score_total += points

            used_words.add(guess)
            used_words.add(lemma_guess)

        history.append({
            "round": r,
            "word": word,
            "guess": guess,
            "points": points,
            "feedback": feedback
        })

        if display_feedback:
            display_feedback(feedback)
        else:
            print(feedback)

        if display_separator:
            display_separator()
        else:
            print("\n" + "-"*40 + "\n")

    if display_final_score:
        display_final_score(score_total)
    else:
        print(f"\nFinal Score: {score_total} points\nThanks for playing!")

    return score_total, history
