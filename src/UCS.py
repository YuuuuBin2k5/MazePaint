# UCS.py
import heapq
import random
import time
from config import MAZE_ROWS, MAZE_COLS
from func_algorithm import simulate_move, MOVES, reconstruct_path_astar_ucs

def ucs_solve(maze, start_pos):
    """
    Tìm lời giải bằng thuật toán UCS với cấu trúc nhất quán.
    """
    print("Solving with UCS...")
    start_time = time.time()
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    start_state = (tuple(start_pos), initial_painted)
    
    tie_breaker = 0
    
    # Priority Queue: (cost, tie_breaker, state)
    # Trong UCS, cost chính là priority
    pq = [(0, tie_breaker, start_state)] 
    
    # Cấu trúc visited nhất quán với A*: { state: [min_cost, parent_state, move] }
    visited = {start_state: [0, None, None]}

    visited_count = 0
    num_of_states = 0

    while pq:
        cost, _, current_state = heapq.heappop(pq)
        visited_count += 1
        
        if cost > visited[current_state][0]:
            continue

        current_pos, painted_tiles = current_state
        if len(painted_tiles) == total_path_tiles:
            path = reconstruct_path_astar_ucs(visited, start_state, current_state)
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
            new_cost = cost + 1
            
            if new_state not in visited or new_cost < visited[new_state][0]:
                num_of_states += 1
                
                visited[new_state] = [new_cost, current_state, move]
                
                # Priority chính là new_cost
                priority = new_cost
                
                tie_breaker += 1
                heapq.heappush(pq, (priority, tie_breaker, new_state))               
    return None