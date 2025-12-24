import nltk
from nltk.corpus import wordnet as wn

nltk.download('wordnet')
nltk.download('omw-1.4')

#1

word = input("Introdu cuvantul: ")
synsets = wn.synsets(word)

if not synsets:
    print("Nu s-au gasit rezultate pentru:", word)
else:
    synonyms = set()
    for s in synsets:
        for l in s.lemmas():
            synonyms.add(l.name())
    print("\nSinonime:", synonyms)

    antonyms = set()
    for s in synsets:
        for l in s.lemmas():
            for ant in l.antonyms():
                antonyms.add(ant.name())
    print("\nAntonime:", antonyms)
    print("\nDefinitii:")
    for s in synsets:
        print("-", s.definition())
    first = synsets[0]
    print("\nHyponyms ", [h.lemma_names() for h in first.hyponyms()])
    print("\nHypernyms :", [h.lemma_names() for h in first.hypernyms()])
    print("\nMeronyms ", [m.lemma_names() for m in first.part_meronyms()])
    print("\nHolonyms ", [h.lemma_names() for h in first.part_holonyms()])