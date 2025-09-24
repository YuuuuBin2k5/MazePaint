# UCS.py
import heapq
import time
from config import MAZE_ROWS, MAZE_COLS
from func_algorithm import simulate_move, DIRECTIONS

def ucs_solve(maze, start_pos):
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    
    # Priority Queue: (cost, path, position, painted_tiles)
    # cost chính là độ ưu tiên
    pq = [(0, [], tuple(start_pos), initial_painted)] 
    visited = { (tuple(start_pos), initial_painted) }
    start_time = time.time()
    while pq:
        cost, path, current_pos, painted_tiles = heapq.heappop(pq)
        
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
                new_cost = cost + 1 # Chi phí tăng thêm 1
                heapq.heappush(pq, (new_cost, new_path, next_pos, new_painted_set))

    return None