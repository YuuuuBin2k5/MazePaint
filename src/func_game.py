"""
func_game.py
Tiện ích và logic game tách ra từ main.py:
- Xử lý input & movement queue
- Di chuyển player / check win
- Dialog chọn thuật toán (tkinter/cosmic)
- Gọi các solver và xử lý kết quả (preview, history)
- Lưu map, khởi tạo trạng thái ban đầu, apply state vào main module
- Helpers: queue API, update preview interval
Lưu ý: file chỉ tổ chức lại chú thích / layout; code logic giữ nguyên.
"""
# === IMPORTS ================================================================
import sys
import copy
import time
from pathlib import Path

import pygame
import tkinter as tk

from config import DIALOG_PADX, DIALOG_PADY
from config import *
from maps import *

# Solver imports (kept here to avoid circular import when possible)
from Algorithm.BFS import bfs_solve
from Algorithm.DFS import dfs_solve
from Algorithm.UCS import ucs_solve
from Algorithm.Greedy import greedy_solve
from Algorithm.Astar import astar_solve

# === MODULE-LEVEL CONSTANTS / QUEUE CONFIG ==================================
# Movement queue configuration
MAX_QUEUE_SIZE = 2        # Maximum queued moves (current + next)
INPUT_BUFFER_TIME = 50    # ms - debounce / buffer time for inputs

# Movement queue state
movement_queue = []
last_input_time = 0

# === INPUT / MOVEMENT QUEUE API ============================================
def handle_input(event):
    """Convert pygame key event to direction string or None."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP: return "UP"
        if event.key == pygame.K_DOWN: return "DOWN"
        if event.key == pygame.K_LEFT: return "LEFT"
        if event.key == pygame.K_RIGHT: return "RIGHT"
    return None

def add_movement_to_queue(direction, current_time):
    """Add a movement to the queue with spam protection and simple override."""
    global movement_queue, last_input_time
    if current_time - last_input_time < INPUT_BUFFER_TIME:
        return
    if len(movement_queue) >= MAX_QUEUE_SIZE:
        if movement_queue[-1] == direction:
            return
        movement_queue[-1] = direction
    else:
        movement_queue.append(direction)
    last_input_time = current_time

def get_next_movement():
    """Pop next movement from queue or return None."""
    global movement_queue
    if movement_queue:
        return movement_queue.pop(0)
    return None

def clear_movement_queue():
    """Clear the movement queue."""
    global movement_queue
    movement_queue.clear()

def get_queue_size():
    """Return number of movements queued."""
    return len(movement_queue)

def is_queue_empty():
    """Return True if movement queue is empty."""
    return len(movement_queue) == 0

def peek_next_movement():
    """Peek next movement without popping."""
    if movement_queue:
        return movement_queue[0]
    return None

# === MOVEMENT / GAME MECHANICS =============================================
def move_player(player_pos, MAZE_ROWS, MAZE_COLS, direction, maze, painted_tiles):
    """
    Slide the player in the given direction until blocked.
    Mark any visited PATH tiles as painted.
    Returns updated player_pos and painted_tiles.
    """
    row, col = player_pos
    dr, dc = 0, 0
    if direction == "UP": dr = -1
    elif direction == "DOWN": dr = 1
    elif direction == "LEFT": dc = -1
    elif direction == "RIGHT": dc = 1

    # Slide while next cell is PATH
    while 0 <= row + dr < MAZE_ROWS and 0 <= col + dc < MAZE_COLS and maze[row + dr][col + dc] == PATH:
        row += dr
        col += dc
        painted_tiles[row][col] = True

    return [row, col], painted_tiles

def check_win_condition(maze, painted_tiles):
    """Return True if all PATH tiles are painted."""
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            if maze[r][c] == PATH and not painted_tiles[r][c]:
                return False
    return True

# === DIALOG / ALGORITHM SELECTION ==========================================
def ask_algorithm():
    """Signal to main to open integrated selector (cosmic)."""
    return "cosmic_selector"

def ask_algorithm_cosmic():
    """
    Try using the in-game cosmic selector (preferred).
    Fallback to tkinter dialog on error.
    """
    import pygame
    from Ui.cosmic_selector import cosmic_algorithm_selector

    try:
        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        if screen is None:
            pygame.init()
            screen = pygame.display.set_mode((1100, 640))
            pygame.display.set_caption("Algorithm Selector")
            clock = pygame.time.Clock()

        result = cosmic_algorithm_selector(screen, clock)
        return result if result else "Player"
    except Exception as e:
        print(f"Error with cosmic selector, falling back to tkinter: {e}")
        return ask_algorithm_tkinter()

def ask_algorithm_tkinter():
    """Tkinter fallback dialog to choose algorithm."""
    root = tk.Tk()
    root.withdraw()
    dialog = tk.Toplevel(root)
    dialog.title("Chọn thuật toán")
    dialog.resizable(False, False)

    font_big = ("Arial", 14)
    w, h = 300, 400
    sw = dialog.winfo_screenwidth()
    sh = dialog.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    dialog.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(dialog, text="Chọn chế độ/thuật toán:", font=font_big).pack(pady=15)
    algorithms = ["Player", "BFS", "DFS", "UCS", "Greedy", "Astar"]
    selected = tk.StringVar(value="Player")

    for algo in algorithms:
        tk.Radiobutton(dialog, text=algo, variable=selected, value=algo,
                       font=font_big, anchor="w", padx=DIALOG_PADX).pack(fill="x")

    result = {"algo": "Player"}

    def on_ok():
        result["algo"] = selected.get()
        dialog.destroy()

    btn_ok = tk.Button(dialog, text="OK", command=on_ok, width=9, height=2, font=font_big)
    btn_ok.pack(pady=DIALOG_PADY)

    dialog.wait_window()
    root.destroy()
    return result["algo"]

# === STATE / INITIALIZATION HELPERS =======================================
def get_initial_state():
    """Return a dict with minimal initial game state (values will be set by reset_game)."""
    return {
        "player_pos": [1, 1],
        "painted_tiles": [],
        "current_maze": [],
        "maze_rows": 0,
        "maze_cols": 0,
        "game_won": False,
        "solving_path": None,
        "move_count": 0,
        "level_start_time": None,
        "history_groups": {},
        "algorithm": "Player",
        "current_map_index": 0,
        "preview_tiles": [],
        "preview_painted": set(),
        "preview_running": False,
        "pending_solving_path": None,
        "victory_frame": 0,
        "victory_phase3_sound_played": False,
    }

def reset_game(current_map_index, all_maps):
    """
    Reset game state for a given map index.
    Returns a state dict that main.py can apply (via apply_state).
    """
    state = {}
    map_names = list(all_maps.keys())
    state['current_maze'] = copy.deepcopy(all_maps[map_names[current_map_index]])
    state['maze_rows'] = len(state['current_maze'])
    state['maze_cols'] = len(state['current_maze'][0])

    state['player_pos'] = [1, 1]
    state['player_visual_pos'] = [1, 1]
    state['player_target_pos'] = [1, 1]
    state['is_moving_smooth'] = False
    state['movement_progress'] = 0.0
    state['current_auto_direction'] = None
    state['last_auto_direction'] = None

    state['painted_tiles'] = [[False for _ in range(state['maze_cols'])] for _ in range(state['maze_rows'])]
    state['painted_tiles'][1][1] = True

    state['board_before_player_moves'] = None
    state['game_won'] = False
    state['solving_path'] = None
    state['move_count'] = 0
    state['victory_frame'] = 0
    state['victory_phase3_sound_played'] = False
    state['level_start_time'] = time.time()

    # Preview / animation reset
    state['preview_tiles'] = []
    state['preview_painted'] = set()
    state['preview_running'] = False
    state['pending_solving_path'] = None
    state['time_since_last_preview'] = 0.0
    state['preview_elapsed_total'] = 0.0

    clear_movement_queue()
    return state

# === HISTORY / RESULT RECORDING ===========================================
def add_to_history(history_groups, algorithm, current_maze, result, execution_time):
    """
    Append solver result to history_groups.
    Accepts different key names used by solvers (visited, visited_count, states, generated_count).
    """
    state_tuple = tuple(tuple(row) for row in current_maze)
    if state_tuple not in history_groups:
        history_groups[state_tuple] = {'maze': copy.deepcopy(current_maze), 'results': []}

    steps = len(result.get("path", []))
    visited = result.get("visited", result.get("visited_count", 0))
    generated = result.get("generated_count", result.get("states", 0))

    new_result = {
        'algorithm': algorithm,
        'steps': steps,
        'visited_count': visited,
        'generated_count': generated,
        'execution_time': round(execution_time, 2) if execution_time is not None else 0.0
    }
    history_groups[state_tuple]['results'].append(new_result)
    return history_groups

# === SOLVER WRAPPER / PREVIEW PROCESSING ==================================
def solve_maze(algorithm, current_maze, player_pos, history_groups):
    """
    Run selected solver and normalize its output for main:
    - path_result: dict with keys 'solving_path', 'preview_tiles', 'pending_solving_path'
    - history_groups updated with add_to_history
    """
    solvers = {
        "BFS": bfs_solve, "DFS": dfs_solve, "UCS": ucs_solve,
        "Greedy": greedy_solve, "Astar": astar_solve
    }

    path_result = {"solving_path": None, "preview_tiles": [], "pending_solving_path": None}
    if algorithm not in solvers:
        return path_result, history_groups

    start_time = time.time()
    try:
        result = solvers[algorithm](current_maze, player_pos)
    except Exception as e:
        print(f"⚠️ Error running solver {algorithm}: {e}")
        result = None
    execution_time = (time.time() - start_time) * 1000

    if result and "path" in result:
        explored = result.get("explored")
        if explored:
            # BFS returns dict(step -> list); other solvers may return list
            if isinstance(explored, dict):
                seq = []
                for k in sorted(explored.keys()):
                    seq.extend(explored[k])
                seen = set()
                preview = []
                for t in seq:
                    if t not in seen:
                        preview.append(t)
                        seen.add(t)
            else:
                preview = list(explored)
            path_result["preview_tiles"] = preview
            path_result["pending_solving_path"] = result["path"][:] if result["path"] else []
        else:
            path_result["solving_path"] = result["path"][:] if result["path"] else []

        history_groups = add_to_history(history_groups, algorithm, current_maze, result, execution_time)
    else:
        history_groups = add_to_history(history_groups, algorithm, current_maze, {"path": []}, execution_time)

    return path_result, history_groups

# === MAP IO ================================================================
def save_current_map_to_file(current_map_index, current_maze):
    """Save current map to src/maps_data/map_X.txt (X = 0..7)."""
    words = ['0', '1', '2', '3', '4', '5', '6', '7']
    try:
        idx = int(current_map_index)
    except Exception:
        print(f"⚠️ Invalid current_map_index (not int): {current_map_index}")
        return

    if 0 <= idx < len(words):
        fname = f"map_{words[idx]}.txt"
        # write into src/maps_data (same folder maps.py reads from)
        p = Path(__file__).parent / "maps_data" / fname
        try:
            # Ensure target directory exists (creates src/maps_data if missing)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('w', encoding='utf-8') as f:
                for row in current_maze:
                    f.write(' '.join(str(int(v)) for v in row) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to save map to {p}: {e}")
    else:
        print(f"⚠️ Invalid current_map_index: {current_map_index}")

# === MAIN MODULE INTERACTION HELPERS ======================================
def apply_state(state):
    """
    Apply a state dict into the main module namespace.
    Useful so main can do: state = reset_game(...); apply_state(state)
    """
    main_mod = sys.modules.get("__main__")
    if not main_mod:
        return
    try:
        for k, v in state.items():
            setattr(main_mod, k, v)
    except Exception as e:
        print(f"⚠️ apply_state failed: {e}")

def update_preview_interval():
    """
    Compute preview_tile_interval_run in main module using:
    pending_solving_path, preview_tiles, SOLVER_MOVE_INTERVAL, PREVIEW_TILE_INTERVAL
    Safe to call even if main hasn't set those variables yet.
    """
    main_mod = sys.modules.get("__main__")
    if not main_mod:
        return
    try:
        pending = getattr(main_mod, "pending_solving_path", None)
        preview_tiles = getattr(main_mod, "preview_tiles", [])
        SOLVER_MOVE_INTERVAL = getattr(main_mod, "SOLVER_MOVE_INTERVAL", None)
        PREVIEW_TILE_INTERVAL = getattr(main_mod, "PREVIEW_TILE_INTERVAL", 0.03)

        num_steps = len(pending) if pending else 0
        num_preview = max(1, len(preview_tiles) if preview_tiles is not None else 1)

        if SOLVER_MOVE_INTERVAL is None:
            main_mod.preview_tile_interval_run = PREVIEW_TILE_INTERVAL
        else:
            if num_steps > 0:
                main_mod.preview_tile_interval_run = (num_steps * SOLVER_MOVE_INTERVAL) / num_preview / 1000.0
            else:
                main_mod.preview_tile_interval_run = PREVIEW_TILE_INTERVAL
    except Exception:
        try:
            main_mod.preview_tile_interval_run = getattr(main_mod, "PREVIEW_TILE_INTERVAL", 0.03)
        except Exception:
            pass
