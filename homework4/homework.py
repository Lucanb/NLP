import nltk
import spacy
from nltk import CFG, ChartParser, Nonterminal, Production
from io import StringIO

nlp = spacy.load("en_core_web_sm")

grammar = CFG.fromstring("""
S -> NP VP | VP
NP -> Det N | Det X1 | N | Adj N | NP PP | NP X2 | V NP
X1 -> Adj N
X2 -> Conj NP
VP -> V NP | V X3 | V Adj | Modal VP | Aux V | Aux VP | Modal V | VP X4 | V X5 | V X6
X3 -> NP PP
X4 -> Conj VP
X5 -> P NP
X6 -> NP AdvP
PP -> P NP | PP X7
X7 -> Conj PP
AdvP -> Adv | Adv X8 | Adv X9 | AdvP X10
X8 -> P NP
X9 -> PP
X10 -> PP
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

grammar_cfg = CFG.fromstring("""
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

productions = grammar_cfg.productions()
new_productions = []
counter = 0

def new_var():
    global counter
    counter += 1
    return Nonterminal(f"X{counter}")

for p in productions:
    lhs = p.lhs()
    rhs = list(p.rhs())
    if len(rhs) > 2:
        prev = rhs[0]
        for sym in rhs[1:-1]:
            new_nt = new_var()
            new_productions.append(Production(lhs, [prev, new_nt]))
            lhs = new_nt
            prev = sym
        new_productions.append(Production(lhs, [prev, rhs[-1]]))
    elif len(rhs) == 2:
        new_productions.append(Production(lhs, rhs))
    elif len(rhs) == 1:
        new_productions.append(Production(lhs, rhs))

cnf_grammar = CFG(grammar_cfg.start(), new_productions)

with open("grammar_cnf.txt", "w", encoding="utf-8") as f:
    for p in cnf_grammar.productions():
        f.write(str(p) + "\n")

print("Constituency parses saved to parsed_trees.txt")
print("Dependency parses saved to dependency_parsing.txt")
print("Converted CNF grammar saved to grammar_cnf.txt")
