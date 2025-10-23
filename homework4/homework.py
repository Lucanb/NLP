import nltk
import spacy
from nltk import CFG, ChartParser
from io import StringIO

nlp = spacy.load("en_core_web_sm")

import nltk
from nltk import CFG

grammar = CFG.fromstring("""
S -> NP VP | VP
NP -> Det N | Det X1 | N | Adj N | X2 X3 | V NP
X1 -> Adj N
X2 -> NP Conj
X3 -> NP
VP -> V NP | X4 X5 | V Adj | Modal VP | Aux V | X6 X7 | Modal V | X8 X9 | X10 X11 | X12 X13
X4 -> V NP
X5 -> PP
X6 -> Aux VP
X7 -> PP
X8 -> VP Conj
X9 -> VP
X10 -> V P
X11 -> NP
X12 -> V NP
X13 -> AdvP
PP -> P NP
AdvP -> Adv | X14 X15 | X16 X17 | X18 X19
X14 -> Adv P
X15 -> NP
X16 -> Adv PP
X17 -> PP
X18 -> AdvP PP
X19 -> PP
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


parser = ChartParser(grammar)

sentences = [
    "flying planes can be dangerous",
    "The parents of the bride and the groom were flying",
    "The groom loves dangerous planes more than the bride"
]

with open("parsed_trees.txt", "w", encoding="utf-8") as f:
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

with open("dependency_parsing.txt", "w", encoding="utf-8") as f:
    for sent in sentences:
        doc = nlp(sent)
        f.write(f"Sentence: {sent}\n")
        for token in doc:
            f.write(f"{token.text:<15}{token.dep_:<15}{token.head.text:<15}{[child.text for child in token.children]}\n")
        f.write("=" * 60 + "\n\n")

print("Constituency parses saved to parsed_trees.txt")
print("Dependency parses saved to dependency_parsing.txt")
