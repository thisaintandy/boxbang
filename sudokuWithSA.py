import tkinter as tk
from tkinter import messagebox
import random
import os
import ast

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game with Levels")
        self.level = 1
        self.board = []
        self.original_board = []
        self.selected_cell = None
        self.cells = [[None for _ in range(9)] for _ in range(9)]

        self.grid_frame = tk.Frame(self.root, bg="white")
        self.grid_frame.pack(pady=10)

        self.load_board()
        self.draw_grid()
        self.draw_buttons()

    def load_board(self):
        filename = f"Sudoku/Level{self.level}.txt"
        if not os.path.exists(filename):
            messagebox.showinfo("🎉 Finished", "No more levels. You’ve completed the game!")
            self.root.quit()
            return

        with open(filename, 'r') as f:
            try:
                self.board = ast.literal_eval(f.read())
                self.original_board = [row[:] for row in self.board]
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read {filename}:\n{e}")
                self.root.quit()
                return

        if len(self.board) != 9 or any(len(row) != 9 for row in self.board):
            messagebox.showerror("Board Error", f"Level {self.level} board is not a valid 9x9 grid.")
            self.root.quit()
            return

    def draw_grid(self):
        for row in range(9):
            for col in range(9):
                bg_color = "#ffffff" if (row // 3 + col // 3) % 2 == 0 else "#e0f7fa"
                entry = tk.Entry(self.grid_frame, width=3, font=('Arial', 20), justify='center', borderwidth=1, relief='solid', bg=bg_color)
                padx = (2 if col % 3 == 0 else 1, 2 if col % 3 == 2 else 1)
                pady = (2 if row % 3 == 0 else 1, 2 if row % 3 == 2 else 1)
                entry.grid(row=row, column=col, padx=padx, pady=pady, ipadx=5, ipady=5)
                entry.bind("<FocusIn>", lambda e, r=row, c=col: self.select_cell(r, c))
                entry.bind("<KeyRelease>", lambda e, r=row, c=col: self.on_input(r, c))
                self.cells[row][col] = entry
        self.populate_board()

    def populate_board(self):
        for row in range(9):
            for col in range(9):
                value = self.board[row][col]
                entry = self.cells[row][col]
                entry.delete(0, tk.END)
                if value != 0:
                    entry.insert(0, str(value))
                    entry.config(state='readonly', disabledforeground='black', readonlybackground=entry.cget("bg"))
                else:
                    entry.config(state='normal', fg='blue')

    def draw_buttons(self):
        btn_frame = tk.Frame(self.root, bg="white")
        btn_frame.pack(pady=10)

        btn_style = {"font": ('Arial', 14), "padx": 20, "pady": 12, "bg": "#4fc3f7", "fg": "white", "relief": "flat"}

        model_btn = tk.Button(btn_frame, text="✨ Hint", command=self.provide_model_hint, **btn_style)
        model_btn.grid(row=0, column=0, padx=10)

        refresh_btn = tk.Button(btn_frame, text="🔁 Refresh", command=self.refresh_board, **btn_style)
        refresh_btn.grid(row=0, column=1, padx=10)

        next_btn = tk.Button(btn_frame, text="➡ Next Level", command=self.next_level, **btn_style)
        next_btn.grid(row=0, column=2, padx=10)

    def select_cell(self, row, col):
        self.selected_cell = (row, col)

    def on_input(self, row, col):
        val = self.cells[row][col].get()
        if not val.isdigit() or not (1 <= int(val) <= 9):
            self.cells[row][col].delete(0, tk.END)
            return
        self.board[row][col] = int(val)
        self.check_board_status()

    def check_board_status(self):
        for row in self.board:
            if 0 in row:
                return
        if self.is_board_valid():
            messagebox.showinfo("✅ Level Completed", f"Congratulations! You completed Level {self.level}.")
            self.next_level()

    def is_board_valid(self):
        for i in range(9):
            row = self.board[i]
            col = [self.board[r][i] for r in range(9)]
            if len(set(row)) != 9 or len(set(col)) != 9:
                return False

        for sr in range(0, 9, 3):
            for sc in range(0, 9, 3):
                block = []
                for r in range(sr, sr + 3):
                    for c in range(sc, sc + 3):
                        block.append(self.board[r][c])
                if len(set(block)) != 9:
                    return False
        return True

    def get_possibilities(self, row, col):
        used = set(self.board[row])
        used.update([self.board[r][col] for r in range(9)])
        start_row, start_col = (row // 3) * 3, (col // 3) * 3
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                used.add(self.board[r][c])
        return set(range(1, 10)) - used

    def provide_model_hint(self):
        # Step 1: Try to find a cell with only one valid possibility (logical hint)
        for r in range(9):
            print("[Model Hint] Using Simulated Annealing to guess a possible value...")
            for c in range(9):
                if self.board[r][c] == 0:
                    poss = self.get_possibilities(r, c)
                    if len(poss) == 1:
                        val = list(poss)[0]
                        self.cells[r][c].delete(0, tk.END)
                        self.cells[r][c].insert(0, str(val))
                        self.cells[r][c].config(fg='blue')
                        self.board[r][c] = val
                        self.check_board_status()
                        return

        # Step 2: No direct hint found, simulate a guess with model (Simulated Annealing)
        def fill_random(b):
            filled = [row[:] for row in b]
            for r in range(9):
                for c in range(9):
                    if filled[r][c] == 0:
                        poss = list(self.get_possibilities(r, c))
                        if poss:
                            filled[r][c] = random.choice(poss)
            return filled

        def fitness(b):
            score = 0
            for i in range(9):
                score += len(set(b[i]))
                score += len(set([b[r][i] for r in range(9)]))
            return score

        def get_neighbors(b):
            neighbors = []
            for _ in range(5):
                new_b = [row[:] for row in b]
                r = random.randint(0, 8)
                empty = [c for c in range(9) if self.board[r][c] == 0]
                if len(empty) >= 2:
                    c1, c2 = random.sample(empty, 2)
                    new_b[r][c1], new_b[r][c2] = new_b[r][c2], new_b[r][c1]
                    neighbors.append(new_b)
            return neighbors

        def simulated_annealing():
            current = fill_random(self.board)
            best = current
            best_score = fitness(current)
            temp = 1.0
            for _ in range(500):
                for neighbor in get_neighbors(current):
                    score = fitness(neighbor)
                    if score > fitness(current) or random.random() < temp:
                        current = neighbor
                        if score > best_score:
                            best = neighbor
                            best_score = score
                temp *= 0.99
            return best
        

        solved = simulated_annealing()

        # Step 3: Try to extract a confident hint from the model
        best_cell = None
        best_possibilities = 10
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    poss = self.get_possibilities(r, c)
                    if solved[r][c] in poss and len(poss) < best_possibilities:
                        best_cell = (r, c, solved[r][c])
                        best_possibilities = len(poss)

        if best_cell:
            r, c, val = best_cell
            self.cells[r][c].delete(0, tk.END)
            self.cells[r][c].insert(0, str(val))
            self.cells[r][c].config(fg='blue')
            self.board[r][c] = val
            self.check_board_status()
            print(f"[Model Hint] Best confident value {val} added at ({r}, {c}) with {best_possibilities} possibilities.")
        else:
            print("[Model Hint] No confident hint found. The board might be unsolvable.")
            messagebox.showwarning("⚠️ No Hint Available", "Invalid answers. No hint available. The board might be unsolvable.")

    def is_solvable(self):
        def is_valid_board_state():
            for r in range(9):
                row_vals = [val for val in self.board[r] if val != 0]
                if len(row_vals) != len(set(row_vals)):
                    return False
            for c in range(9):
                col_vals = [self.board[r][c] for r in range(9) if self.board[r][c] != 0]
                if len(col_vals) != len(set(col_vals)):
                    return False
            for br in range(0, 9, 3):
                for bc in range(0, 9, 3):
                    box = []
                    for r in range(br, br + 3):
                        for c in range(bc, bc + 3):
                            val = self.board[r][c]
                            if val != 0:
                                box.append(val)
                    if len(box) != len(set(box)):
                        return False
            return True

        def is_valid(r, c, n):
            for i in range(9):
                if self.board[r][i] == n or self.board[i][c] == n:
                    return False
            sr, sc = (r // 3) * 3, (c // 3) * 3
            for i in range(sr, sr + 3):
                for j in range(sc, sc + 3):
                    if self.board[i][j] == n:
                        return False
            return True

        def solve():
            for r in range(9):
                for c in range(9):
                    if self.board[r][c] == 0:
                        for n in range(1, 10):
                            if is_valid(r, c, n):
                                self.board[r][c] = n
                                if solve():
                                    return True
                                self.board[r][c] = 0
                        return False
            return True

        if not is_valid_board_state():
            messagebox.showerror("❌ Invalid Board", f"Level {self.level} board has conflicts (e.g., duplicate numbers).")
            return False

        backup = [row[:] for row in self.board]
        solvable = solve()
        self.board = backup
        if not solvable:
            messagebox.showwarning("🛑 Unsolvable", f"Level {self.level} board is not solvable.")
        return solvable

    def refresh_board(self):
        self.board = [row[:] for row in self.original_board]
        self.populate_board()

    def next_level(self):
        self.level += 1

        # Clear the existing grid widgets
        for row in self.cells:
            for cell in row:
                cell.destroy()

        # Reload and draw the new board
        self.load_board()
        self.draw_grid()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x600")
    root.title("Sudoku Game")

    start_frame = tk.Frame(root, bg="#fce4ec")
    start_frame.pack(fill="both", expand=True)

    title = tk.Label(start_frame, text="🧠 Sudoku Challenge", font=("Arial", 30, "bold"), bg="#fce4ec", fg="#ad1457")
    title.pack(pady=60)

    subtitle = tk.Label(start_frame, text="Sharpen your mind\nOne puzzle at a time!", font=("Arial", 14), bg="#fce4ec")
    subtitle.pack(pady=10)

    def start_game():
        start_frame.destroy()
        SudokuApp(root)

    play_btn = tk.Button(start_frame, text="▶ Play", command=start_game, font=("Arial", 18, "bold"), bg="#f06292", fg="white", relief="flat", padx=25, pady=15, borderwidth=0)
    play_btn.pack(pady=30)
    play_btn.config(highlightthickness=0)

    root.mainloop()
