import tkinter as tk
from tkinter import messagebox
import random

# Sample muna 
board = [
    [0, 0, 0, 2, 6, 0, 7, 0, 1],
    [6, 8, 0, 0, 7, 0, 0, 9, 0],
    [1, 9, 0, 0, 0, 4, 5, 0, 0],
    [8, 2, 0, 1, 0, 0, 0, 4, 0],
    [0, 0, 4, 6, 0, 2, 9, 0, 0],
    [0, 5, 0, 0, 0, 3, 0, 2, 8],
    [0, 0, 9, 3, 0, 0, 0, 7, 4],
    [0, 4, 0, 0, 5, 0, 0, 3, 6],
    [7, 0, 3, 0, 1, 8, 0, 0, 0]
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
                entry.grid(row=row, column=col, padx=(0 if col % 3 != 0 else 2), pady=(0 if row % 3 != 0 else 2))

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

    def provide_model_hint(self):
        print("\n[Model Hint] Scanning board for confident cells...")
        confident_cells = []

        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    possible = self.get_possibilities(row, col)
                    if len(possible) == 1:
                        confident_cells.append((row, col, possible.pop()))

        if confident_cells:
            row, col, val = random.choice(confident_cells)
            print(f"[Model Hint] Placing value {val} at ({row}, {col})")
            self.cells[row][col].delete(0, tk.END)
            self.cells[row][col].insert(0, str(val))
            self.cells[row][col].config(fg='blue')
            board[row][col] = val
        else:
            print("[Model Hint] No confident cell found. Not enough data.")
            messagebox.showinfo("Model Hint", "No confident hint available.")

    def get_possibilities(self, row, col):
        used = set()

        # Check row
        used.update(board[row])

        # Check column
        used.update([board[r][col] for r in range(9)])

        # Check box
        box_start_row = (row // 3) * 3
        box_start_col = (col // 3) * 3
        for r in range(box_start_row, box_start_row + 3):
            for c in range(box_start_col, box_start_col + 3):
                used.add(board[r][c])

        return set(range(1, 10)) - used

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
