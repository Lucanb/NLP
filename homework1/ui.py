import tkinter as tk
from tkinter import messagebox, Toplevel, Listbox, Scrollbar, END
from PIL import Image, ImageTk, ImageSequence
from game import play_game, get_similarity, lemmatizer

class WordGameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Word Association Game")
        master.geometry("900x600")
        self.history_list = []
        self.main_menu()

    def main_menu(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        tk.Label(self.master, text="Word Association Game", font=("Arial", 30)).pack(pady=40)
        tk.Button(self.master, text="Start Game", font=("Arial", 16), command=self.start_game).pack(pady=10)
        tk.Button(self.master, text="History", font=("Arial", 16), command=self.show_history).pack(pady=10)
        tk.Button(self.master, text="About", font=("Arial", 16), command=self.show_about).pack(pady=10)
        tk.Button(self.master, text="Quit", font=("Arial", 16), command=self.master.quit).pack(pady=10)

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Word Association Game using WordNet similarity.\n"
            "Developed in Python/Tkinter.\n\n"
            "Objective: Find words associated with the displayed word.\n"
            "Points are calculated based on similarity.\n"
            "Each round adds points to your total score."
        )

    def start_game(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.round = 0
        self.total_score = 0
        self.used_words = set()
        self.game_history = []
        self.rounds = 5
        self.canvas = tk.Canvas(self.master, width=900, height=600)
        self.canvas.pack(fill="both", expand=True)

        try:
            gif = Image.open("background.gif")
            self.frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(gif)]
            self.gif_index = 0
            self.bg_label = tk.Label(self.canvas)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            def animate_gif():
                if not hasattr(self, 'bg_label') or not self.bg_label.winfo_exists():
                    return
                frame = self.frames[self.gif_index]
                self.bg_label.config(image=frame)
                self.gif_index = (self.gif_index + 1) % len(self.frames)
                self.master.after(100, animate_gif)
            animate_gif()
        except Exception:
            try:
                bg_image = Image.open("background.png")
                bg_image = bg_image.resize((900, 200), Image.ANTIALIAS)
                self.bg_photo = ImageTk.PhotoImage(bg_image)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception:
                self.canvas.config(bg="lightblue")

        self.word_label = tk.Label(self.canvas, text="", font=("Arial", 30), bg="#ffffff", fg="#000000")
        self.canvas.create_window(450, 250, window=self.word_label)
        self.entry = tk.Entry(self.canvas, font=("Arial", 20))
        self.canvas.create_window(450, 320, window=self.entry)
        self.send_button = tk.Button(self.canvas, text="SEND", font=("Arial", 16), command=self.send_guess)
        self.canvas.create_window(450, 370, window=self.send_button)
        self.feedback_label = tk.Label(self.canvas, text="", font=("Arial", 16), bg="#ffffff", fg="#333333")
        self.canvas.create_window(450, 420, window=self.feedback_label)
        self.score_label = tk.Label(self.canvas, text=f"Score: {self.total_score}", font=("Arial", 16), fg="green", bg="#ffffff")
        self.canvas.create_window(750, 30, window=self.score_label)
        self.next_round()

    def next_round(self):
        if self.round >= self.rounds:
            self.history_list.append({
                "score": self.total_score,
                "history": self.game_history
            })
            messagebox.showinfo("Game Over", f"🏆 Total Score: {self.total_score}")
            self.main_menu()
            return
        self.round += 1
        self.current_word = play_game.get_random_word()
        self.word_label.config(text=self.current_word.upper())
        self.entry.delete(0, tk.END)
        self.feedback_label.config(text="")

    def send_guess(self):
        guess = self.entry.get().strip().lower()
        if not guess:
            return
        lemma_guess = lemmatizer.lemmatize(guess)
        if guess in self.used_words or lemma_guess in self.used_words:
            points = 0
            feedback = f"❌ Already used '{guess}' → 0 points!"
        else:
            score = get_similarity(self.current_word, guess)
            if score is None:
                points = 0
                feedback = f"❌ No valid relation → 0 points!"
            else:
                points = int(score*100)
                if score > 0.8:
                    feedback = f"🔥 Excellent match! +{points}"
                elif score > 0.5:
                    feedback = f"👍 Good association +{points}"
                elif score > 0.2:
                    feedback = f"🤔 Weak relation +{points}"
                else:
                    feedback = f"❌ Almost no connection +{points}"
                self.total_score += points
            self.used_words.add(guess)
            self.used_words.add(lemma_guess)
        self.game_history.append({
            "round": self.round,
            "word": self.current_word,
            "guess": guess,
            "points": points,
            "feedback": feedback
        })
        self.feedback_label.config(text=feedback)
        self.score_label.config(text=f"Score: {self.total_score}")
        self.master.after(1000, self.next_round)

    def show_history(self):
        if not self.history_list:
            messagebox.showinfo("History", "No games played yet.")
            return
        hist_win = Toplevel(self.master)
        hist_win.title("Game History")
        hist_win.geometry("600x400")
        lb = Listbox(hist_win, font=("Arial", 14))
        lb.pack(side="left", fill="both", expand=True)
        scroll = Scrollbar(hist_win)
        scroll.pack(side="right", fill="y")
        lb.config(yscrollcommand=scroll.set)
        scroll.config(command=lb.yview)
        for idx, game in enumerate(self.history_list):
            lb.insert(END, f"Game {idx+1}: {game['score']} points")
        def show_details(event):
            sel = lb.curselection()
            if sel:
                index = sel[0]
                game = self.history_list[index]
                details = "\n".join([
                    f"Round {h['round']}: Word='{h['word']}', Guess='{h['guess']}', Points={h['points']}, Feedback='{h['feedback']}'"
                    for h in game['history']
                ])
                messagebox.showinfo(f"Game {index+1} Details", details)
        lb.bind("<Double-1>", show_details)

if __name__ == "__main__":
    root = tk.Tk()
    app = WordGameGUI(root)
    root.mainloop()
