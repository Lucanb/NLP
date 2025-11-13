import wikipedia
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np
import pandas as pd
from sklearn.decomposition import NMF, LatentDirichletAllocation
import matplotlib.pyplot as plt
import seaborn as sns
import pyLDAvis
from gensim.models import CoherenceModel
from gensim import corpora
from gensim.models.ldamodel import LdaModel

nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

# === Ex 1: Preprocessing ===

topics = {
    "Mathematics": [
        "Harmonic function",
        "Laplace's equation",
        "Potential theory",
        "Fourier series",
        "Analytic function"
    ],
    "Physics": [
        "Quantum mechanics",
        "Wave–particle duality",
        "Schrödinger equation",
        "Quantum entanglement",
        "Quantum field theory"
    ],
    "Computer Science": [
        "Dijkstra's algorithm",
        "Graph theory",
        "Shortest path problem",
        "Bellman–Ford algorithm",
        "A* search algorithm"
    ]
}

documents, labels = [], []

for domain, pages in topics.items():
    for page in pages:
        try:
            page_obj = wikipedia.page(page, auto_suggest=False)
            text = page_obj.content
            text = re.sub(r"==.*?==+", "", text)
            text = re.sub(r"\n+", " ", text)
            documents.append(text)
            labels.append(domain)
        except wikipedia.DisambiguationError as e:
            try:
                text = wikipedia.page(e.options[0], auto_suggest=False).content
                text = re.sub(r"==.*?==+", "", text)
                text = re.sub(r"\n+", " ", text)
                documents.append(text)
                labels.append(domain)
            except Exception:
                pass
        except Exception:
            pass

print(f"Loaded {len(documents)} documents.")

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words]
    return " ".join(tokens)

clean_docs = [preprocess(doc) for doc in documents]

bow_vectorizer = CountVectorizer(max_features=5000)
bow_matrix = bow_vectorizer.fit_transform(clean_docs)
tfidf_vectorizer = TfidfVectorizer(max_features=5000)
tfidf_matrix = tfidf_vectorizer.fit_transform(clean_docs)

feature_names_bow = bow_vectorizer.get_feature_names_out()
feature_names_tfidf = tfidf_vectorizer.get_feature_names_out()

texts = [doc.split() for doc in clean_docs]
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

# === Safe LDA Visualization (Fix for complex128) ===
def safe_prepare_lda(model, matrix, vectorizer):
    term_dists = np.array(model.components_).real.astype(float)
    doc_dists = np.array(model.transform(matrix)).real.astype(float)
    doc_lengths = np.array(matrix.sum(axis=1)).flatten().astype(float)
    vocab = np.array(vectorizer.get_feature_names_out()).tolist()
    term_freq = np.array(matrix.sum(axis=0)).flatten().astype(float)
    term_dists = np.nan_to_num(term_dists, nan=0.0, posinf=0.0, neginf=0.0)
    doc_dists = np.nan_to_num(doc_dists, nan=0.0, posinf=0.0, neginf=0.0)
    term_freq = np.nan_to_num(term_freq, nan=0.0, posinf=0.0, neginf=0.0)
    return pyLDAvis.prepare(
        topic_term_dists=term_dists,
        doc_topic_dists=doc_dists,
        doc_lengths=doc_lengths,
        vocab=vocab,
        term_frequency=term_freq
    )

# === Ex 3: Non-negative Matrix Factorization (NMF) ===

nmf_topic_values = [3, 5, 7, 10]
nmf_recon_errors = []

for k in nmf_topic_values:
    nmf_model = NMF(n_components=k, random_state=42, max_iter=300)
    nmf_model.fit(tfidf_matrix)
    nmf_recon_errors.append(nmf_model.reconstruction_err_)
    print(f"NMF with {k} topics – Reconstruction error: {nmf_model.reconstruction_err_:.3f}")

plt.figure(figsize=(7,4))
plt.plot(nmf_topic_values, nmf_recon_errors, marker='o', color='purple')
plt.xlabel("Number of Topics (k)")
plt.ylabel("Reconstruction Error")
plt.title("NMF Reconstruction Error vs Number of Topics")
plt.grid(True)
plt.show()

best_nmf_k = nmf_topic_values[np.argmin(nmf_recon_errors)]
print(f"\nBest number of topics for NMF: {best_nmf_k}")

best_nmf = NMF(n_components=best_nmf_k, random_state=42, max_iter=300)
W = best_nmf.fit_transform(tfidf_matrix)
H = best_nmf.components_

def print_topics(model, feature_names, n_top_words=10):
    for topic_idx, comp in enumerate(model.components_):
        terms = [feature_names[i] for i in comp.argsort()[:-n_top_words - 1:-1]]
        print(f"Topic {topic_idx+1}: {', '.join(terms)}")

print("\n=== Best NMF Topics ===\n")
print_topics(best_nmf, feature_names_tfidf)

nmf_topics_df = pd.DataFrame(W, columns=[f"Topic {i+1}" for i in range(best_nmf_k)])
nmf_topics_df.index = [f"{label}_{i}" for i, label in enumerate(labels)]

plt.figure(figsize=(10,6))
sns.heatmap(nmf_topics_df, cmap="magma", annot=False)
plt.title(f"Document–Topic Distribution (Best NMF, k={best_nmf_k})")
plt.xlabel("Topics")
plt.ylabel("Documents")
plt.show()

# === Ex 4: Latent Dirichlet Allocation (LDA) ===

topic_values = [3, 5, 7, 10]
coherences, elbos = [], []

for k in topic_values:
    lda_model = LatentDirichletAllocation(
        n_components=k,
        learning_method='batch',
        random_state=42,
        max_iter=20,
        evaluate_every=1,
        verbose=0
    )
    lda_model.fit(bow_matrix)
    elbo = lda_model.bound_
    elbos.append(elbo)
    temp = LdaModel(corpus=corpus, num_topics=k, id2word=dictionary, passes=5, random_state=42)
    coherence_model = CoherenceModel(model=temp, texts=texts, dictionary=dictionary, coherence='c_v')
    coherence = coherence_model.get_coherence()
    coherences.append(coherence)
    print(f"\n=== LDA Results for {k} Topics ===")
    print(f"ELBO: {elbo:.2f}")
    print(f"Coherence: {coherence:.3f}")
    lda_display = safe_prepare_lda(lda_model, bow_matrix, bow_vectorizer)
    out_file = f"lda_visualization_{k}_topics.html"
    pyLDAvis.save_html(lda_display, out_file)
    print(f"Visualization saved as {out_file}")

plt.figure(figsize=(7,4))
plt.plot(topic_values, coherences, marker='o', label='Coherence Score')
plt.xlabel("Number of Topics (k)")
plt.ylabel("Coherence")
plt.title("LDA Coherence vs Number of Topics")
plt.grid(True)
plt.legend()
plt.show()

plt.figure(figsize=(7,4))
plt.plot(topic_values, elbos, marker='s', color='orange', label='ELBO')
plt.xlabel("Number of Topics (k)")
plt.ylabel("ELBO")
plt.title("LDA ELBO vs Number of Topics")
plt.grid(True)
plt.legend()
plt.show()

best_idx = np.argmax(coherences)
best_k = topic_values[best_idx]
print(f"\nBest number of topics for LDA: {best_k} (Coherence = {coherences[best_idx]:.3f}, ELBO = {elbos[best_idx]:.2f})")

best_lda = LatentDirichletAllocation(
    n_components=best_k,
    learning_method='batch',
    random_state=42,
    max_iter=30
)
best_lda.fit(bow_matrix)

lda_display = safe_prepare_lda(best_lda, bow_matrix, bow_vectorizer)
pyLDAvis.save_html(lda_display, f"lda_best_{best_k}_topics.html")
print(f"LDA visualization for best model saved as lda_best_{best_k}_topics.html")

topic_names = [f"Topic {i+1}" for i in range(best_k)]
doc_topics = best_lda.transform(bow_matrix)
df_topics = pd.DataFrame(doc_topics, columns=topic_names)
df_topics.index = [f"{label}_{i}" for i, label in enumerate(labels)]

plt.figure(figsize=(10,6))
sns.heatmap(df_topics, cmap="coolwarm", annot=False)
plt.title(f"Document–Topic Distribution (Best LDA, k={best_k})")
plt.xlabel("Topics")
plt.ylabel("Documents")
plt.show()

#doc de fct