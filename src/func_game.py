# func_game.py
import pygame
import tkinter as tk
from config import DIALOG_PADX, DIALOG_PADY
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
    """
    Sử dụng cosmic selector - integrated với main game
    """
    return "cosmic_selector"  # Signal để main.py xử lý

def ask_algorithm_cosmic():
    """
    Sử dụng cosmic selector - tạm thời disable
    """
    import pygame
    from Ui.cosmic_selector import cosmic_algorithm_selector
    
    # Sử dụng screen và clock từ main module nếu có
    try:
        # Import từ main để sử dụng screen và clock đã có
        import main
        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        
        if screen is None:
            # Fallback nếu không có screen
            pygame.init()
            screen = pygame.display.set_mode((1100, 640))
            pygame.display.set_caption("Algorithm Selector")
            clock = pygame.time.Clock()
        
        result = cosmic_algorithm_selector(screen, clock)
        return result if result else "Player"  # Default to Player if cancelled
        
    except Exception as e:
        print(f"Error with cosmic selector, falling back to tkinter: {e}")
        # Fallback to original tkinter version
        return ask_algorithm_tkinter()

def ask_algorithm_tkinter():
    """
    Original tkinter version as fallback
    """
def ask_algorithm_tkinter():
    """
    Original tkinter version as fallback
    """
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
                       font=font_big, anchor="w", padx=DIALOG_PADX).pack(fill="x")

    result = {"algo": "Player"}

    def on_ok():
        result["algo"] = selected.get()
        dialog.destroy()

    btn_ok = tk.Button(dialog, text="OK", command=on_ok,
                       width=9, height=2, font=font_big)
    btn_ok.pack(pady=DIALOG_PADY)

    dialog.wait_window()
    root.destroy()
    return result["algo"]

# === SMART MOVEMENT QUEUE SYSTEM ===
"""
Hệ thống queue thông minh cho xử lý input di chuyển
- Chống spam input
- Hỗ trợ smooth movement  
- Buffer input để phản hồi nhanh
"""

# Movement queue globals
movement_queue = []  # Queue để lưu các movement commands
MAX_QUEUE_SIZE = 2   # Tối đa 2 moves trong queue (current + next)
last_input_time = 0  # Thời gian input cuối cùng
INPUT_BUFFER_TIME = 50  # ms - thời gian buffer để detect spam

def add_movement_to_queue(direction, current_time):
    """Thêm movement vào queue với logic thông minh"""
    global movement_queue, last_input_time
    
    # Kiểm tra spam input (nếu input quá nhanh, ignore)
    if current_time - last_input_time < INPUT_BUFFER_TIME:
        return
    
    # Nếu queue đầy, remove oldest hoặc override nếu cùng direction
    if len(movement_queue) >= MAX_QUEUE_SIZE:
        # Nếu direction cuối cùng giống với input mới, ignore
        if movement_queue[-1] == direction:
            return
        # Override direction cuối cùng trong queue
        movement_queue[-1] = direction
    else:
        # Thêm vào queue nếu chưa đầy
        movement_queue.append(direction)
    
    last_input_time = current_time

def get_next_movement():
    """Lấy movement tiếp theo từ queue"""
    global movement_queue
    if movement_queue:
        return movement_queue.pop(0)
    return None

def clear_movement_queue():
    """Xóa toàn bộ queue"""
    global movement_queue
    movement_queue.clear()

def get_queue_size():
    """Lấy số lượng movements trong queue"""
    return len(movement_queue)

def is_queue_empty():
    """Kiểm tra queue có rỗng không"""
    return len(movement_queue) == 0

def peek_next_movement():
    """Xem movement tiếp theo mà không remove khỏi queue"""
    if movement_queue:
        return movement_queue[0]
    return None