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
from data.maps import *

# Solver imports (kept here to avoid circular import when possible)
from data.algorithm.BFS import bfs_solve
from data.algorithm.DFS import dfs_solve
from data.algorithm.UCS import ucs_solve
from data.algorithm.Greedy import greedy_solve
from data.algorithm.Astar import astar_solve
from manager import sound_manager
from Ui.widgets.cosmic_selector import cosmic_algorithm_selector


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
        "is_solving": False,
        "solving_start_time": 0,
    }

def reset_game(current_map_index, all_maps):
    """
    Reset game state for current map.
    Returns a dict of state variables.
    """
    # Tạo deep copy để tránh thay đổi all_maps
    current_maze = copy.deepcopy(all_maps[list(all_maps.keys())[current_map_index]])
    
    state = {}
    state['current_maze'] = current_maze
    state['maze_rows'] = len(current_maze)
    state['maze_cols'] = len(current_maze[0])

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
    
    # Loading state reset
    state['is_solving'] = False
    state['solving_start_time'] = 0

    clear_movement_queue()
    return state

# === HISTORY / RESULT RECORDING ===========================================
def add_to_history(history_groups, algorithm, current_maze, result, execution_time, heuristic_info=None):
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
        'execution_time': round(execution_time, 2) if execution_time is not None else 0.0,
        'heuristic_info': heuristic_info
    }
    history_groups[state_tuple]['results'].append(new_result)
    return history_groups

# === SOLVER WRAPPER / PREVIEW PROCESSING ==================================
def solve_maze(algorithm, current_maze, player_pos, history_groups):
    """
    Giải maze bằng thuật toán được chọn
    """
    start_time = time.time()
    result = None
    
    
    # THÊM: Parse algorithm name và heuristic type
    base_algorithm = algorithm.split("_")[0] if "_" in algorithm else algorithm
    heuristic_type = "not_done"  # Default
    heuristic_info = None  # Thông tin để hiển thị trong history
    
    # Parse heuristic index nếu có (format: "Greedy_[2]" hoặc "Astar_[1]")
    if "_[" in algorithm and "]" in algorithm:
        try:
            heuristic_index = int(algorithm.split("[")[1].split("]")[0])
            # Map index to heuristic type names - PHẢI KHỚP với cosmic_selector
            heuristic_types = {1: "not_done", 2: "unpainted_count", 3:"line_count"}
            if heuristic_index in heuristic_types:
                heuristic_type = heuristic_types[heuristic_index]
                # Map heuristic names for display
                heuristic_display_names = {
                    "not_done": "Not Done",
                    "unpainted_count": "Unpainted Count", 
                    "line_count": "Line Count"
                }
                heuristic_info = heuristic_display_names.get(heuristic_type, heuristic_type)
        except Exception as e:
            print(f"DEBUG func_game - Error parsing heuristic: {e}")
    
    # Xác định heuristic info cho các thuật toán
    if base_algorithm in ["Greedy", "Astar"]:
        if heuristic_info is None:
            heuristic_info = "h1 (Not Done)"  # Default heuristic
    else:
        heuristic_info = "X"  # Không có heuristic
    
    # Gọi thuật toán
    if base_algorithm == "BFS":
        result = bfs_solve(current_maze, player_pos)
    elif base_algorithm == "DFS":
        # DFS bình thường - stable version
        result = dfs_solve(current_maze, player_pos)
    elif base_algorithm == "UCS":
        result = ucs_solve(current_maze, player_pos)
    elif base_algorithm == "Greedy":
        result = greedy_solve(current_maze, player_pos, heuristic_type)
    elif base_algorithm == "Astar":
        result = astar_solve(current_maze, player_pos, heuristic_type)
    else:
        return {
            "solving_path": None,
            "pending_solving_path": None,
            "preview_tiles": [],
            "explored": None
        }, history_groups
    
    if not result:
        return {
            "solving_path": None,
            "pending_solving_path": None,
            "preview_tiles": [],
            "explored": None
        }, history_groups
    
    
    # Lấy path
    directions = result.get("path", [])
    
    # Lấy explored - QUAN TRỌNG
    explored = result.get("explored")
    
    # GIỚI HẠN explored
    MAX_PREVIEW_STEPS = 300
    if explored and len(explored) > MAX_PREVIEW_STEPS:
        step_keys = sorted(explored.keys())
        step_interval = len(step_keys) // MAX_PREVIEW_STEPS
        sampled_explored = {}
        for i, key in enumerate(step_keys[::max(1, step_interval)]):
            sampled_explored[i] = explored[key]
        explored = sampled_explored
    
    # Tính preview_tiles
    preview_tiles = []
    if explored:
        for step in sorted(explored.keys()):
            if explored[step]:
                for tile in explored[step]:
                    if isinstance(tile, (list, tuple)) and len(tile) >= 2:
                        preview_tiles.append((tile[0], tile[1]))
    
    # Lưu history
    elapsed_ms = (time.time() - start_time) * 1000
    try:
        history_groups = add_to_history(history_groups, algorithm, current_maze, result, elapsed_ms, heuristic_info)
    except Exception as e:
        print(f"Warning: Failed to add to history: {e}")
    
    return {
        "solving_path": directions,
        "pending_solving_path": directions,
        "preview_tiles": preview_tiles,
        "explored": explored
    }, history_groups

# === MAP IO ================================================================
def save_current_map_to_file(current_map_index, current_maze):
    """
    Save current map to src/data/maps_data/map_X.txt (X = 0..7).
    Returns True if successful, False otherwise.
    """
    words = ['0', '1', '2', '3', '4', '5', '6', '7']
    
    # Validate map index
    try:
        idx = int(current_map_index)
    except (ValueError, TypeError) as e:
        return False

    if not (0 <= idx < len(words)):
        return False
    
    # Validate maze data
    if not current_maze or not isinstance(current_maze, (list, tuple)):
        return False
    
    fname = f"map_{words[idx]}.txt"
    # write into src/data/maps_data (same folder maps.py reads from)
    p = Path("src") / "data" / "maps_data" / fname

    try:
        # Ensure target directory exists (creates src/data/maps_data if missing)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        # Write maze data
        with p.open('w', encoding='utf-8') as f:
            for i, row in enumerate(current_maze):
                if not isinstance(row, (list, tuple)):
                    return False
                line = ' '.join(str(int(v)) for v in row)
                f.write(line + "\n")
        
        # Verify file was written
        if p.exists() and p.stat().st_size > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"⚠️ Failed to save map to {p}: {e}")
        return False

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

# === FUNCTIONS ===
def solve_in_background(algorithm, current_maze, player_pos, history_groups):
    """
    Chạy thuật toán solving trong background thread
    """
    import sys
    main_mod = sys.modules.get("__main__")
    
    try:
        result = solve_maze(algorithm, current_maze, player_pos, history_groups)
        if main_mod:
            main_mod.solving_result = result
            main_mod.solving_result_ready = True
    except Exception as e:
        print(f"Error in background solving: {e}")
        if main_mod:
            main_mod.solving_result = None
            main_mod.solving_result_ready = True

# === HELPER FUNCTIONS ===
def save_and_exit_edit_mode():
    """Save current map and exit edit mode"""
    main_mod = sys.modules.get("__main__")
    if not main_mod:
        return
    
    if getattr(main_mod, 'edit_mode', False):
        current_map_index = getattr(main_mod, 'current_map_index', 0)
        current_maze = getattr(main_mod, 'current_maze', [])
        all_maps = getattr(main_mod, 'all_maps', {})
        map_names = getattr(main_mod, 'map_names', [])
        
        success = save_current_map_to_file(current_map_index, current_maze)
        if success and map_names and current_map_index < len(map_names):
            all_maps[map_names[current_map_index]] = copy.deepcopy(current_maze)
            sound_manager.play_button_sound()
        
        # Set variables back to main module
        main_mod.edit_mode = False
        main_mod.edit_pending_save = False