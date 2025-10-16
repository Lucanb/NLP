import tkinter as tk
from tkinter import messagebox, Toplevel, Listbox, Scrollbar, END
from PIL import Image, ImageTk, ImageSequence
import json
import os
import game

HISTORY_FILE = "game_history.json"

class WordGameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Word Association Game")
        master.attributes("-fullscreen", True)
        self.history_list = self.load_history()
        self.main_menu()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception:
                pass
        return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self.history_list, f, indent=4)
        except Exception as e:
            print("Error saving history:", e)

    def main_menu(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        try:
            bg_image = Image.open("background.png")
            bg_image = bg_image.resize((self.master.winfo_screenwidth(), self.master.winfo_screenheight()), Image.ANTIALIAS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(self.master, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self.master.config(bg="lightblue")

        tk.Label(self.master, text="Word Association Game", font=("Arial", 40), bg="#ffffff").pack(pady=40)
        tk.Button(self.master, text="Start Game", font=("Arial", 20), width=20, command=self.start_game).pack(pady=10)
        tk.Button(self.master, text="History", font=("Arial", 20), width=20, command=self.show_history).pack(pady=10)
        tk.Button(self.master, text="About", font=("Arial", 20), width=20, command=self.show_about).pack(pady=10)
        tk.Button(self.master, text="Quit", font=("Arial", 20), width=20, command=self.master.quit).pack(pady=10)

    def show_about(self):
        about_text = (
            "Word Association Game\n\n"
            "Objective: Find words associated with the displayed word.\n"
            "Uses WordNet similarity to calculate the score.\n\n"
            "How to play:\n"
            "1. The current word is displayed in the center of the screen.\n"
            "2. Enter an associated word and press SEND.\n"
            "3. Points depend on how closely your word relates to the displayed word.\n"
            "4. Each round adds points to your total score.\n\n"
            "Game history is saved automatically.\n"
            "The total score is shown at the top-right during gameplay."
        )
        messagebox.showinfo("About Word Association Game", about_text)

    def start_game(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.round = 0
        self.total_score = 0
        self.used_words = set()
        self.game_history = []
        self.rounds = 5
        self.canvas = tk.Canvas(self.master, width=self.master.winfo_screenwidth(), height=self.master.winfo_screenheight())
        self.canvas.pack(fill="both", expand=True)
        screen_width = self.master.winfo_screenwidth()
        try:
            gif = Image.open("background.gif")
            self.frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(gif)]
            self.gif_index = 0
            self.bg_label = tk.Label(self.canvas)
            self.bg_label.place(x=0, y=0, relwidth=1, height=400)
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
                bg_image = bg_image.resize((screen_width, 400), Image.ANTIALIAS)
                self.bg_photo = ImageTk.PhotoImage(bg_image)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception:
                self.canvas.create_rectangle(0, 0, screen_width, 400, fill="lightblue")

        self.word_label = tk.Label(self.canvas, text="", font=("Arial", 40), bg="#ffffff", fg="#000000")
        self.canvas.create_window(screen_width//2, 450, window=self.word_label)
        self.entry = tk.Entry(self.canvas, font=("Arial", 30))
        self.canvas.create_window(screen_width//2, 550, window=self.entry)
        self.send_button = tk.Button(self.canvas, text="SEND", font=("Arial", 20), command=self.send_guess)
        self.canvas.create_window(screen_width//2, 620, window=self.send_button)
        self.feedback_label = tk.Label(self.canvas, text="", font=("Arial", 25), bg="#ffffff", fg="#333333")
        self.canvas.create_window(screen_width//2, 700, window=self.feedback_label)
        self.score_label = tk.Label(self.canvas, text=f"Score: {self.total_score}", font=("Arial", 25), fg="green", bg="#ffffff")
        self.canvas.create_window(screen_width - 200, 50, window=self.score_label)
        self.next_round()

    def next_round(self):
        if self.round >= self.rounds:
            self.history_list.append({
                "score": self.total_score,
                "history": self.game_history
            })
            self.save_history()
            messagebox.showinfo("Game Over", f"🏆 Total Score: {self.total_score}")
            self.main_menu()
            return
        self.round += 1
        self.current_word = game.get_random_word()
        self.word_label.config(text=self.current_word.upper())
        self.entry.delete(0, tk.END)
        self.feedback_label.config(text="")

    def send_guess(self):
        guess = self.entry.get().strip().lower()
        if not guess:
            return
        lemma_guess = game.lemmatizer.lemmatize(guess)
        if guess in self.used_words or lemma_guess in self.used_words:
            points = 0
            feedback = f"❌ Already used '{guess}' → 0 points!"
        else:
            score = game.get_similarity(self.current_word, guess)
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
        for idx, game_data in enumerate(self.history_list):
            lb.insert(END, f"Game {idx+1}: {game_data['score']} points")
        def show_details(event):
            sel = lb.curselection()
            if sel:
                index = sel[0]
                game_data = self.history_list[index]
                details = "\n".join([
                    f"Round {h['round']}: Word='{h['word']}', Guess='{h['guess']}', Points={h['points']}, Feedback='{h['feedback']}'"
                    for h in game_data['history']
                ])
                messagebox.showinfo(f"Game {index+1} Details", details)
        lb.bind("<Double-1>", show_details)

if __name__ == "__main__":
    root = tk.Tk()
    app = WordGameGUI(root)
    root.mainloop()
