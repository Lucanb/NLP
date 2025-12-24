from collections import Counter, defaultdict
import re

class NGramBPE:
    def __init__(self, sentences, corpus, n=2):
        self.sentences = sentences
        self.corpus = corpus
        self.n = n
        self.vocab_bpe = None
        self.ngram_model = None
        self.vocab_ngram = set()

    def ex1(self, iterations=10):
        vocab = Counter(' '.join(self.sentences).split())
        vocab = {' '.join(list(word)): freq for word, freq in vocab.items()}
        for _ in range(iterations):
            pairs = Counter()
            for word, freq in vocab.items():
                symbols = word.split()
                for i in range(len(symbols) - 1):
                    pairs[(symbols[i], symbols[i + 1])] += freq
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            bigram = ' '.join(best)
            replacement = ''.join(best)
            vocab = {word.replace(bigram, replacement): freq for word, freq in vocab.items()}
        self.vocab_bpe = vocab
        print("Ex1:", self.vocab_bpe)

    def ex2(self):
        words = re.sub(r'[^a-zăâîșț ]', '', self.corpus.lower()).split()
        ngrams = [tuple(words[i:i+self.n]) for i in range(len(words)-self.n+1)]
        model = defaultdict(Counter)
        for ngram in ngrams:
            context = ngram[:-1]
            target = ngram[-1]
            model[context][target] += 1
            self.vocab_ngram.add(target)
        self.ngram_model = model
        context = ("merg",)
        count_context = sum(model[context].values())
        count_word = model[context]["la"]
        prob = (count_word + 1) / (count_context + len(self.vocab_ngram))
        print("Ex2:", prob)

    def ex3(self, sentence):
        words = re.sub(r'[^a-zăâîșț ]', '', sentence.lower()).split()
        prob = 1.0
        for i in range(self.n-1, len(words)):
            context = tuple(words[i - self.n + 1:i])
            word = words[i]
            count_context = sum(self.ngram_model[context].values())
            count_word = self.ngram_model[context][word]
            prob *= (count_word + 1) / (count_context + len(self.vocab_ngram))
        print(f"Ex3 ({sentence}):", prob)


if __name__ == "__main__":
    sentences = ["eu merg la scoala", "tu mergi la facultate"]
    corpus = """Eu merg la magazin si cumpar paine si lapte. Apoi merg acasa si mananc.
Tu mergi la magazin si cumperi fructe."""
    model = NGramBPE(sentences, corpus, n=2)
    model.ex1()
    model.ex2()
    model.ex3("eu merg la magazin")
