# BFS.py
import collections
import time
from config import MAZE_ROWS, MAZE_COLS
from func_algorithm import simulate_move, DIRECTIONS

def bfs_solve(maze, start_pos): # Đổi tên hàm
    print("Solving with BFS...")
    start_time = time.time()
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    queue = collections.deque([(tuple(start_pos), [], initial_painted)])
    visited = { (tuple(start_pos), initial_painted) }

    while queue:
        current_pos, path, painted_tiles = queue.popleft()
        
        if len(painted_tiles) == total_path_tiles:
            return {
                "path": path,
                "steps": len(path),
                "visited": len(visited),
                "states": len(queue),
                "time": time.time() - start_time
            }

        # Lặp qua các hướng di chuyển từ biến DIRECTIONS
        for direction in DIRECTIONS:
            next_pos, newly_painted = simulate_move(current_pos, MAZE_ROWS, MAZE_COLS, direction, maze)
            
            if next_pos == current_pos:
                continue
            
            new_painted_set = painted_tiles.union(newly_painted)
            new_state = (next_pos, new_painted_set)
            
            if new_state not in visited:
                visited.add(new_state)
                new_path = path + [direction]
                queue.append((next_pos, new_path, new_painted_set))
    print("Không có lời giải")            
    return None