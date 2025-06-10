import pygame
import random
import math
import time

pygame.init()

WIDTH, HEIGHT = 540, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku with Hints and Simulated Annealing")

FONT = pygame.font.SysFont("comicsans", 40)
SMALL_FONT = pygame.font.SysFont("comicsans", 20)

WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    box_x, box_y = (row // 3) * 3, (col // 3) * 3
    for i in range(box_x, box_x + 3):
        for j in range(box_y, box_y + 3):
            if board[i][j] == num:
                return False
    return True

def solve_board(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                for num in range(1, 10):
                    if is_valid(board, i, j, num):
                        board[i][j] = num
                        if solve_board(board):
                            return True
                        board[i][j] = 0
                return False
    return True

def generate_puzzle():
    board = [[0]*9 for _ in range(9)]
    solve_board(board)
    solution = [row[:] for row in board]

    # Remove random cells
    for _ in range(40):
        x, y = random.randint(0, 8), random.randint(0, 8)
        board[x][y] = 0

    return board, solution

# Simulated Annealing
def sudoku_cost(board):
    cost = 0
    for row in board:
        cost += 9 - len(set(row))
    for col in zip(*board):
        cost += 9 - len(set(col))
    return cost

def random_fill(puzzle):
    board = [[puzzle[i][j] if puzzle[i][j] != 0 else 0 for j in range(9)] for i in range(9)]
    for box_x in range(0, 9, 3):
        for box_y in range(0, 9, 3):
            nums = set(range(1, 10))
            for i in range(box_x, box_x + 3):
                for j in range(box_y, box_y + 3):
                    if board[i][j] != 0:
                        nums.discard(board[i][j])
            empty = [(i, j) for i in range(box_x, box_x + 3) for j in range(box_y, box_y + 3) if board[i][j] == 0]
            for (i, j), val in zip(empty, nums):
                board[i][j] = val
    return board

def simulated_annealing(puzzle):
    print("Simulated Annealing: Solving puzzle...")
    current = random_fill(puzzle)
    cost = sudoku_cost(current)
    T = 1.0
    T_min = 1e-6
    alpha = 0.99

    while T > T_min and cost > 0:
        i = random.randint(0, 8)
        row = current[i]
        indices = [j for j in range(9) if puzzle[i][j] == 0]

        if len(indices) < 2:
            T *= alpha
            continue

        a, b = random.sample(indices, 2)
        neighbor = [r[:] for r in current]
        neighbor[i][a], neighbor[i][b] = neighbor[i][b], neighbor[i][a]
        new_cost = sudoku_cost(neighbor)
        delta = new_cost - cost

        if delta < 0 or random.random() < math.exp(-delta / T):
            current = neighbor
            cost = new_cost

        T *= alpha

    if cost == 0:
        print("Simulated Annealing: Solution found!")
        return current
    else:
        print("Simulated Annealing: Failed to solve.")
        return None

# Hint system
def get_hint(selected):
    if not selected:
        return None, "Select a cell first."
    
    i, j = selected

    if puzzle[i][j] != 0:
        return None, "Cell is already filled."

    row_nums = set(puzzle[i][x] for x in range(9) if puzzle[i][x] != 0)
    col_nums = set(puzzle[x][j] for x in range(9) if puzzle[x][j] != 0)
    box_x, box_y = (i // 3) * 3, (j // 3) * 3
    box_nums = set(
        puzzle[x][y]
        for x in range(box_x, box_x + 3)
        for y in range(box_y, box_y + 3)
        if puzzle[x][y] != 0
    )

    possible = [n for n in range(1, 10) if n not in row_nums | col_nums | box_nums]

    if len(possible) == 1:
        return (i, j, possible[0]), None
    else:
        solved = simulated_annealing(puzzle)
        if solved:
            return (i, j, solved[i][j]), "Hint generated using Simulated Annealing"
        else:
            return None, "Unable to generate hint."

# Drawing
def draw_board(selected):
    screen.fill(WHITE)

    for i in range(10):
        thick = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (0, i * 60), (540, i * 60), thick)
        pygame.draw.line(screen, BLACK, (i * 60, 0), (i * 60, 540), thick)

    for i in range(9):
        for j in range(9):
            num = puzzle[i][j]
            if num != 0:
                text = FONT.render(str(num), True, BLACK)
                screen.blit(text, (j * 60 + 20, i * 60 + 15))

    if selected:
        pygame.draw.rect(screen, RED, (selected[1]*60, selected[0]*60, 60, 60), 3)

    pygame.draw.rect(screen, GREY, (WIDTH//2 - 60, HEIGHT - 50, 120, 40))
    hint_text = SMALL_FONT.render("Get Hint", True, BLACK)
    screen.blit(hint_text, (WIDTH//2 - 40, HEIGHT - 40))

    if status_message:
        status_text = SMALL_FONT.render(status_message, True, BLUE)
        screen.blit(status_text, (20, HEIGHT - 45))

    pygame.display.update()

# Input system
def input_number(pos, key):
    if puzzle[pos[0]][pos[1]] == 0 and key in range(pygame.K_1, pygame.K_9+1):
        val = key - pygame.K_0
        if 1 <= val <= 9:
            user_board[pos[0]][pos[1]] = val
            puzzle[pos[0]][pos[1]] = val

# Main loop
def main():
    global status_message
    selected = None
    running = True
    while running:
        draw_board(selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if y < 540:
                    selected = (y // 60, x // 60)
                elif WIDTH//2 - 60 <= x <= WIDTH//2 + 60 and HEIGHT - 50 <= y <= HEIGHT - 10:
                    hint, msg = get_hint(selected)
                    if hint:
                        i, j, val = hint
                        puzzle[i][j] = val
                        user_board[i][j] = val
                        status_message = f"Hint placed {val} at ({i+1},{j+1})"
                    else:
                        status_message = msg

            elif event.type == pygame.KEYDOWN:
                if selected and event.key in range(pygame.K_1, pygame.K_9+1):
                    input_number(selected, event.key)

    pygame.quit()

# Setup
puzzle, solution = generate_puzzle()
user_board = [[puzzle[i][j] for j in range(9)] for i in range(9)]
status_message = ""
main()
