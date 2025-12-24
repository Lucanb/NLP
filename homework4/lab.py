import nltk
from nltk import CFG, ChartParser
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from io import StringIO

for pkg in ["punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except LookupError:
        nltk.download(pkg)

grammar = CFG.fromstring("""
S -> NP VP | VP
NP -> Det N | Det Adj N | N | Adj N | NP PP | NP Conj NP | V NP
VP -> V NP | V NP PP | V Adj | V | Modal VP | Aux V | Aux VP | Modal V | VP PP | VP Conj VP | V P NP | V NP AdvP
PP -> P NP
AdvP -> Adv | Adv P NP | Adv PP | AdvP PP
Conj -> 'and'
Det -> 'the' | 'a' | 'an'
N -> 'planes' | 'parents' | 'bride' | 'groom'
V -> 'flying' | 'were' | 'loves' | 'be' | 'can'
Adj -> 'dangerous' | 'flying'
Adv -> 'more' | 'than'
P -> 'of' | 'and' | 'more' | 'than'
Modal -> 'can'
Aux -> 'were' | 'be'
""")

# grammar = CFG.fromstring("""
# S -> NP VP | VP
# NP -> Det N | Det X1 | N | Adj N | NP X2 | NP X3 | V NP
# X1 -> Adj N
# X2 -> PP
# X3 -> Conj NP
# VP -> V NP | V X4 | V Adj | Modal VP | Aux V | Aux VP | Modal V | VP X5 | VP X6 | V X7 | V X8
# X4 -> NP PP
# X5 -> PP
# X6 -> Conj VP
# X7 -> P NP
# X8 -> NP AdvP
# PP -> P NP
# AdvP -> Adv | Adv X9 | Adv X10 | AdvP X11
# X9 -> P NP
# X10 -> PP
# X11 -> PP
# Conj -> 'and'
# Det -> 'the' | 'a' | 'an'
# N -> 'planes' | 'parents' | 'bride' | 'groom'
# V -> 'flying' | 'were' | 'loves' | 'be' | 'can'
# Adj -> 'dangerous' | 'flying'
# Adv -> 'more' | 'than'
# P -> 'of' | 'and' | 'more' | 'than'
# Modal -> 'can'
# Aux -> 'were' | 'be'
# """)

parser = ChartParser(grammar)

sentences = [
    "flying planes can be dangerous",
    "The parents of the bride and the groom were flying",
    "The groom loves dangerous planes more than the bride"
]

output_file = "parsed_trees.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for sent in sentences:
        tokens = nltk.word_tokenize(sent.lower())
        try:
            trees = list(parser.parse(tokens))
        except ValueError as e:
            f.write(f"Sentence: {sent}\nNo valid parse found: {e}\n\n")
            continue
        if not trees:
            f.write(f"Sentence: {sent}\nNo valid parse found.\n\n")
            continue

        seen = set()
        distinct_trees = []
        for t in trees:
            s = t.pformat()
            if s not in seen:
                seen.add(s)
                distinct_trees.append(t)

        f.write(f"Sentence: {sent}\nFound {len(distinct_trees)} unique trees.\n\n")
        for i, tree in enumerate(distinct_trees):
            buf = StringIO()
            tree.pretty_print(stream=buf)
            f.write(f"Tree {i+1} (ASCII view):\n{buf.getvalue()}\n")
        f.write("=" * 60 + "\n\n")

        window = tk.Tk()
        window.title(f"Sentence: {sent}")
        text_area = ScrolledText(window, width=100, height=40, font=("Courier", 10))
        text_area.pack(fill="both", expand=True)
        text_area.insert("end", f"Sentence: {sent}\n\n")

        for i, tree in enumerate(distinct_trees[:2]):
            buf = StringIO()
            tree.pretty_print(stream=buf)
            text_area.insert("end", f"Tree {i+1}:\n{buf.getvalue()}\n")

        text_area.config(state="disabled")
        window.mainloop()

print(f"Parse trees have been saved to {output_file}")
