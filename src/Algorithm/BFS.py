# BFS.py
import collections
import random
import time
from config import MAZE_ROWS, MAZE_COLS
from .func_algorithm import simulate_move, MOVES, reconstruct_path

def bfs_solve(maze, start_pos):  
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    start_state = (tuple(start_pos), initial_painted)

    queue = collections.deque([start_state])
    
    # Visited lưu lại dấu vết: {trạng_thái_con: (trạng_thái_cha, hướng_đi)}
    visited = {start_state: (None, None)}
    num_of_states = 0
    visited_count = 0
    start_time = time.time()
    while queue:
        current_pos, painted_tiles = queue.popleft()
        current_state = (current_pos, painted_tiles)
        visited_count+=1

        if len(painted_tiles) == total_path_tiles:
            path = reconstruct_path(visited, start_state, current_state)
            return {
                "path": path,
                "steps": len(path),
                "visited": visited_count,
                "states": num_of_states,
                "time": time.time() - start_time
            }

        shuffled_moves = list(MOVES.keys())
        random.shuffle(shuffled_moves)
        for move in shuffled_moves:
            next_pos, newly_painted = simulate_move(current_pos, MAZE_ROWS, MAZE_COLS, move, maze)
            
            if next_pos == current_pos:
                continue
            
            new_painted_set = painted_tiles.union(newly_painted)
            new_state = (next_pos, new_painted_set)
            
            if new_state not in visited:
                num_of_states+=1
                visited[new_state] = (current_state, move)
                queue.append(new_state)
    return None