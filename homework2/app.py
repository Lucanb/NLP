from flask import Flask, request, jsonify, render_template
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import os


class NGramBPE:
    def __init__(self, sentences, corpus, n=2):
        self.sentences = sentences
        self.corpus = corpus
        self.n = n
        self.model = None
        self.tokenizer = None
        self.context = []

    def ex4_init(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")

    def ex4(self, user_msg):
        self.context.append(f"You: {user_msg}")
        all_words = " ".join(self.context).split()
        last_four_words = " ".join(all_words[-4:])

        inputs = self.tokenizer(last_four_words, return_tensors="pt")

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=5,
            do_sample=True,
            top_k=30,
            top_p=0.9,
            temperature=0.6,
            num_return_sequences=5,
            pad_token_id=self.tokenizer.eos_token_id
        )

        candidates = []
        for output in outputs:
            text = self.tokenizer.decode(output, skip_special_tokens=True)
            new_text = text[len(last_four_words):].strip().split()
            if new_text:
                first_word = new_text[0]
                tokens = self.tokenizer(first_word, return_tensors="pt")["input_ids"]
                with torch.no_grad():
                    logits = self.model(**inputs).logits[:, -1, :]
                    probs = torch.softmax(logits, dim=-1)
                    score = probs[0, tokens[0, 0]].item()
                candidates.append((first_word, score))

        if candidates:
            best_word = sorted(candidates, key=lambda x: x[1], reverse=True)[0][0]
        else:
            best_word = "(no output)"

        self.context.append(f"GPT: {best_word}")
        return best_word


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

    next_word = model.ex4(msg)
    return jsonify({"response": next_word})


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
