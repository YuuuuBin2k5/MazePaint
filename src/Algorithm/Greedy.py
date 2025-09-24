# GBFS.py
import heapq
import time
import random
from config import MAZE_ROWS, MAZE_COLS
from .func_algorithm import simulate_move, MOVES, reconstruct_path, heuristic

def greedy_solve(maze, start_pos):
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    start_state = (tuple(start_pos), initial_painted)

    # Priority Queue: (heuristic, tie_breaker, state)
    # Heuristic là độ ưu tiên chính
    tie_breaker = 0
    initial_h = heuristic(initial_painted, total_path_tiles)
    pq = [(initial_h, tie_breaker, start_state)] 
    
    # Visited dùng để truy vết ngược
    visited = {start_state: (None, None)}
    num_of_states = 0
    visited_count = 0
    start_time = time.time()
    while pq:
        _, _, current_state = heapq.heappop(pq)
        current_pos, painted_tiles = current_state
        visited_count += 1
        
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
                num_of_states += 1
                visited[new_state] = (current_state, move)
                # Độ ưu tiên chỉ dựa vào heuristic
                new_h = heuristic(new_painted_set, total_path_tiles)
                tie_breaker += 1
                heapq.heappush(pq, (new_h, tie_breaker, new_state))                
    return None