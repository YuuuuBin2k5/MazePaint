# DFS.py
import time
from config import MAZE_ROWS, MAZE_COLS
from func_algorithm import simulate_move, DIRECTIONS

def dfs_solve(maze, start_pos):
    """Tìm lời giải bằng thuật toán DFS."""
    print("Solving with DFS...")
    start_time = time.time()
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    stack = [(tuple(start_pos), [], initial_painted)]
    visited = { (tuple(start_pos), initial_painted) }

    while stack:
        current_pos, path, painted_tiles = stack.pop()
        
        if len(painted_tiles) == total_path_tiles:
            return { "path": path, "steps": len(path), "visited": len(visited), "states": len(stack), "time": time.time() - start_time }

        for direction in DIRECTIONS:

            next_pos, newly_painted = simulate_move(current_pos, MAZE_ROWS, MAZE_COLS, direction, maze)
            
            if next_pos == current_pos:
                continue
            
            new_painted_set = painted_tiles.union(newly_painted)
            new_state = (next_pos, new_painted_set)
            
            if new_state not in visited:
                visited.add(new_state)
                new_path = path + [direction]
                stack.append((next_pos, new_path, new_painted_set))
                
    print("Không có lời giải")
    return None