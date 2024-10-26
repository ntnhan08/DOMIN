import tkinter as tk
import random
import time

class Minesweeper:
    def __init__(self, master, rows=20, cols=20, mines=40):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.flags = 0
        self.buttons = []
        self.mine_positions = set()
        self.revealed = set()
        self.first_click = True
        self.start_time = None
        self.timer_label = None
        self.flags_label = None
        self.create_widgets()
        self.place_mines()

    def create_widgets(self):
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                button = tk.Button(self.master, width=2, height=1, bg='lightblue')
                button.grid(row=r, column=c)
                button.bind('<Button-1>', lambda e, r=r, c=c: self.left_click(r, c))
                button.bind('<Button-3>', lambda e, r=r, c=c: self.right_click(r, c))
                row.append(button)
            self.buttons.append(row)
        self.restart_button = tk.Button(self.master, text="Restart", command=self.restart_game, state='disabled')
        self.restart_button.grid(row=self.rows, column=0, columnspan=self.cols)
        self.timer_label = tk.Label(self.master, text="Time: 00:00")
        self.timer_label.grid(row=self.rows + 1, column=0, columnspan=self.cols)
        self.flags_label = tk.Label(self.master, text=f"Flags: {self.flags}/{self.mines}")
        self.flags_label.grid(row=self.rows + 2, column=0, columnspan=self.cols)
        self.leaderboard_button = tk.Button(self.master, text="Leaderboard", command=self.show_leaderboard)
        self.leaderboard_button.grid(row=self.rows + 3, column=0, columnspan=self.cols)
        self.update_timer()

    def place_mines(self):
        while len(self.mine_positions) < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            self.mine_positions.add((r, c))

    def left_click(self, r, c):
        if self.buttons[r][c]['text'] == 'F':
            return
        if self.first_click:
            self.first_click = False
            self.start_time = time.time()
            self.reveal_initial_cells(r, c)
        elif (r, c) in self.mine_positions:
            self.buttons[r][c].config(text='*', bg='red')
            self.game_over()
        else:
            self.reveal(r, c)
            if self.check_win():
                self.win_game()

    def right_click(self, r, c):
        if self.buttons[r][c]['state'] == 'disabled':
            return
        current_text = self.buttons[r][c]['text']
        if current_text == '':
            self.buttons[r][c].config(text='F', bg='yellow')
            self.flags += 1
        elif current_text == 'F':
            self.buttons[r][c].config(text='', bg='lightblue')
            self.flags -= 1
        self.flags_label.config(text=f"Flags: {self.flags}/{self.mines}")

    def reveal_initial_cells(self, r, c):
        to_reveal = [(r, c)]
        revealed_count = 0
        while to_reveal and revealed_count < 10:
            cr, cc = to_reveal.pop()
            if (cr, cc) not in self.revealed:
                self.reveal(cr, cc)
                revealed_count += 1
                if self.count_mines(cr, cc) == 0:
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                to_reveal.append((nr, nc))

    def reveal(self, r, c):
        if (r, c) in self.revealed:
            return
        self.revealed.add((r, c))
        
        mines_count = self.count_mines(r, c)
        if mines_count == 0:
            self.buttons[r][c].config(text='', state='disabled', bg='SystemButtonFace')
        else:
            color = self.get_color(mines_count)
            self.buttons[r][c].config(text=str(mines_count), fg=color, state='disabled', bg='SystemButtonFace')
        
        if mines_count == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal(nr, nc)

    def count_mines(self, r, c):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in self.mine_positions:
                    count += 1
        return count

    def get_color(self, mines_count):
        colors = {
            1: 'blue',
            2: 'red',
            3: 'green',
            4: 'purple'
        }
        return colors.get(mines_count, 'black')

    def game_over(self):
        for r, c in self.mine_positions:
            self.buttons[r][c].config(text='*', bg='red')
        for row in self.buttons:
            for button in row:
                button.config(state='disabled')
        self.restart_button.config(state='normal')
        self.show_message("YOU LOSE")

    def check_win(self):
        return len(self.revealed) == self.rows * self.cols - self.mines

    def win_game(self):
        for row in self.buttons:
            for button in row:
                button.config(state='disabled')
        self.restart_button.config(state='normal')
        self.show_message("YOU WON")
        self.update_leaderboard()

    def restart_game(self):
        self.master.destroy()
        root = tk.Tk()
        root.title("Minesweeper")
        game = Minesweeper(root)
        root.mainloop()

    def update_timer(self):
        if self.start_time:
            elapsed_time = int(time.time() - self.start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            self.timer_label.config(text=f"Time: {minutes:02}:{seconds:02}")
        self.master.after(1000, self.update_timer)

    def update_leaderboard(self):
        elapsed_time = int(time.time() - self.start_time)
        with open("leaderboard.txt", "a") as file:
            file.write(f"{elapsed_time}\n")
        self.show_leaderboard()

    def show_leaderboard(self):
        with open("leaderboard.txt", "r") as file:
            times = file.readlines()
        times = [int(time.strip()) for time in times]
        times.sort()
        leaderboard = tk.Toplevel(self.master)
        leaderboard.title("Leaderboard")
        tk.Label(leaderboard, text="Top Times:").pack()
        for i, time in enumerate(times[:10]):
            minutes = time // 60
            seconds = time % 60
            tk.Label(leaderboard, text=f"{i + 1}. {minutes:02}:{seconds:02}").pack()

    def show_message(self, message):
        message_window = tk.Toplevel(self.master)
        message_window.title("Game Over")
        tk.Label(message_window, text=message, font=("Helvetica", 24)).pack(pady=20)
        tk.Button(message_window, text="OK", command=message_window.destroy).pack(pady=10)
        self.master.after_cancel(self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minesweeper")
    game = Minesweeper(root)
    root.mainloop()
