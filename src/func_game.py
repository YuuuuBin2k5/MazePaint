# func_game.py
import pygame
import tkinter as tk
from config import *

def handle_input(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP: return "UP"
        if event.key == pygame.K_DOWN: return "DOWN"
        if event.key == pygame.K_LEFT: return "LEFT"
        if event.key == pygame.K_RIGHT: return "RIGHT"
    return None

def move_player(player_pos, MAZE_ROWS, MAZE_COLS, direction, maze, painted_tiles):
    row, col = player_pos
    dr, dc = 0, 0
    if direction == "UP": dr = -1
    elif direction == "DOWN": dr = 1
    elif direction == "LEFT": dc = -1
    elif direction == "RIGHT": dc = 1
    
    while 0<=row+dr< MAZE_ROWS and 0<=col+dc<MAZE_COLS and maze[row + dr][col + dc] == 0:
        row += dr
        col += dc
        painted_tiles[row][col] = True
    
    return [row, col], painted_tiles

def check_win_condition(maze, painted_tiles):
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            if maze[r][c] == 0 and not painted_tiles[r][c]:
                return False
    return True

def ask_algorithm():
    root = tk.Tk()
    root.withdraw()  # ẩn cửa sổ chính

    dialog = tk.Toplevel(root)
    dialog.title("Chọn thuật toán")
    dialog.resizable(False, False)

    font_big = ("Arial", 14)

    # căn giữa cửa sổ
    w, h = 300, 400
    sw = dialog.winfo_screenwidth()
    sh = dialog.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    dialog.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(dialog, text="Chọn chế độ/thuật toán:", font=font_big).pack(pady=15)

    # danh sách thuật toán
    algorithms = ["Player", "BFS", "DFS", "UCS", "Greedy", "Astar"]
    selected = tk.StringVar(value="Player")  # mặc định

    for algo in algorithms:
        tk.Radiobutton(dialog, text=algo, variable=selected, value=algo,
                       font=font_big, anchor="w", padx=20).pack(fill="x")

    result = {"algo": "Player"}

    def on_ok():
        result["algo"] = selected.get()
        dialog.destroy()

    btn_ok = tk.Button(dialog, text="OK", command=on_ok,
                       width=9, height=2, font=font_big)
    btn_ok.pack(pady=20)

    dialog.wait_window()
    root.destroy()
    return result["algo"]