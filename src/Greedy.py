# GBFS.py
import heapq
import time
from config import MAZE_ROWS, MAZE_COLS
from func_algorithm import simulate_move, DIRECTIONS, heuristic

def greedy_solve(maze, start_pos):
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    
    initial_h = heuristic(initial_painted, total_path_tiles)
    pq = [(initial_h, [], tuple(start_pos), initial_painted)] 
    visited = { (tuple(start_pos), initial_painted) }
    
    start_time = time.time()
    while pq:
        _, path, current_pos, painted_tiles = heapq.heappop(pq)
        
        if len(painted_tiles) == total_path_tiles:
            return {
                "path": path, "steps": len(path), "visited": len(visited),
                "states": len(pq), "time": time.time() - start_time
            }

        for direction in DIRECTIONS:
            next_pos, newly_painted = simulate_move(current_pos, MAZE_ROWS, MAZE_COLS, direction, maze)
            
            if next_pos == current_pos:
                continue
            
            new_painted_set = painted_tiles.union(newly_painted)
            new_state = (next_pos, new_painted_set)
            
            if new_state not in visited:
                visited.add(new_state)
                new_path = path + [direction]
                new_h = heuristic(new_painted_set, total_path_tiles)
                heapq.heappush(pq, (new_h, new_path, next_pos, new_painted_set))
    return None