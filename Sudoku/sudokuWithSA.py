import tkinter as tk
from tkinter import messagebox
import random

# Sample board (editable by user)
board = [
    [1, 0, 0, 4, 8, 9, 0, 0, 6],
    [7, 3, 0, 0, 0, 0, 0, 4, 0],
    [0, 0, 0, 0, 0, 1, 2, 9, 5],

    [0, 0, 7, 1, 2, 0, 6, 0, 0],
    [5, 0, 0, 7, 0, 3, 0, 0, 8],
    [0, 0, 6, 0, 9, 5, 7, 0, 0],

    [9, 1, 4, 6, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 3, 7],
    [8, 0, 0, 5, 1, 2, 0, 0, 4]
]

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku with Logic and Model Hint")

        self.selected_cell = None
        self.cells = [[None for _ in range(9)] for _ in range(9)]

        self.draw_grid()
        self.draw_buttons()

    def draw_grid(self):
        for row in range(9):
            for col in range(9):
                value = board[row][col]
                entry = tk.Entry(self.root, width=2, font=('Arial', 24), justify='center', borderwidth=2, relief='solid')

                # Add padding to visually separate 3x3 blocks
                padx = (2 if col % 3 == 0 else 1, 2 if col % 3 == 2 else 1)
                pady = (2 if row % 3 == 0 else 1, 2 if row % 3 == 2 else 1)
                entry.grid(row=row, column=col, padx=padx, pady=pady)

                if value != 0:
                    entry.insert(0, str(value))
                    entry.config(state='readonly')

                entry.bind("<Button-1>", lambda e, r=row, c=col: self.select_cell(r, c))
                self.cells[row][col] = entry

    def draw_buttons(self):
        logic_btn = tk.Button(self.root, text="Logic Hint", command=self.provide_logic_hint)
        logic_btn.grid(row=9, column=3, columnspan=2, pady=10)

        model_btn = tk.Button(self.root, text="Model Hint", command=self.provide_model_hint)
        model_btn.grid(row=9, column=5, columnspan=2, pady=10)

    def select_cell(self, row, col):
        self.selected_cell = (row, col)
        self.cells[row][col].focus_set()

    def provide_logic_hint(self):
        if not self.selected_cell:
            messagebox.showinfo("Hint", "Select a cell first.")
            return

        row, col = self.selected_cell
        if board[row][col] != 0:
            messagebox.showinfo("Hint", "Cell already filled.")
            return

        possibilities = self.get_possibilities(row, col)
        if len(possibilities) == 1:
            hint = possibilities.pop()
            self.cells[row][col].delete(0, tk.END)
            self.cells[row][col].insert(0, str(hint))
            self.cells[row][col].config(fg='blue')
            board[row][col] = hint
        else:
            messagebox.showinfo("Hint", "No clear logic hint available.")

    def get_possibilities(self, row, col):
        used = set(board[row])
        used.update([board[r][col] for r in range(9)])
        start_row, start_col = (row // 3) * 3, (col // 3) * 3
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                used.add(board[r][c])
        return set(range(1, 10)) - used

    def provide_model_hint(self):
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
                score += len(set(b[i]))               # unique in row
                score += len(set([b[r][i] for r in range(9)]))  # unique in column
            return score

        def get_neighbors(b):
            neighbors = []
            for _ in range(5):
                new_b = [row[:] for row in b]
                r = random.randint(0, 8)
                empty = [c for c in range(9) if board[r][c] == 0]
                if len(empty) >= 2:
                    c1, c2 = random.sample(empty, 2)
                    new_b[r][c1], new_b[r][c2] = new_b[r][c2], new_b[r][c1]
                    neighbors.append(new_b)
            return neighbors

        def simulated_annealing():
            current = fill_random(board)
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

        print("[Model Hint] Running Simulated Annealing...")
        solved = simulated_annealing()

        best_cell = None
        best_possibilities = 10  # more than max (which is 9)

        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    poss = self.get_possibilities(r, c)
                    if solved[r][c] in poss:
                        if len(poss) < best_possibilities:
                            best_possibilities = len(poss)
                            best_cell = (r, c, solved[r][c])

        if best_cell:
            r, c, val = best_cell
            self.cells[r][c].delete(0, tk.END)
            self.cells[r][c].insert(0, str(val))
            self.cells[r][c].config(fg='blue')
            board[r][c] = val
            print(f"[Model Hint] Best confident value {val} added at ({r}, {c}) with {best_possibilities} possibilities.")
        else:
            messagebox.showinfo("Model Hint", "No confident hint found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
