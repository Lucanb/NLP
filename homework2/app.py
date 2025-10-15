from flask import Flask, request, jsonify, render_template
from lab import NGramBPE
import os


class NGramBPE:
    def __init__(self, sentences, corpus, n=2):
        self.sentences = sentences
        self.corpus = corpus
        self.n = n
        self.vocab_bpe = None
        self.ngram_model = None
        self.vocab_ngram = set()
        self.generator = None
        self.context = []

    def ex4_init(self):
        if self.generator is None:
            from transformers import pipeline
            self.generator = pipeline("text-generation", model="gpt2")

    def ex4(self, user_msg):
        from transformers import pipeline
        if self.generator is None:
            self.generator = pipeline("text-generation", model="gpt2")
        self.context.append(f"You: {user_msg}")
        all_words = ' '.join(self.context).split()
        last_four_words = ' '.join(all_words[-4:])
        result = self.generator(
            last_four_words,
            max_new_tokens=10,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )[0]['generated_text']
        new_words = result[len(last_four_words):].strip().split()[:2]
        gpt_msg = ' '.join(new_words)
        self.context.append(f"GPT: {gpt_msg}")

        return gpt_msg


app = Flask(__name__)
model = NGramBPE([], "")
model.ex4_init()
model.context = []

HISTORY_DIR = "history"
os.makedirs(HISTORY_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"response": "Please enter a message."})

    model.context.append(msg)
    all_text = " ".join(model.context)
    last_four = " ".join(all_text.split()[-4:])
    next_words = model.ex4(last_four)
    response = next_words
    model.context.append(response)
    return jsonify({"response": response})

@app.route('/save', methods=['POST'])
def save():
    filename = os.path.join(HISTORY_DIR, "conversation.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(model.context))
    return jsonify({"status": "saved", "filename": filename})

@app.route('/history', methods=['GET'])
def history():
    files = os.listdir(HISTORY_DIR)
    return jsonify({"files": files})

@app.route('/load/<filename>', methods=['GET'])
def load(filename):
    filepath = os.path.join(HISTORY_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"content": content})
    return jsonify({"content": ""})

if __name__ == "__main__":
    app.run(debug=True)
