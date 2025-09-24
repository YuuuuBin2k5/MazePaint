# Astar.py
import heapq
import time
from config import MAZE_ROWS, MAZE_COLS
from func_algorithm import simulate_move, DIRECTIONS, heuristic # Sử dụng heuristic đơn giản

def astar_solve(maze, start_pos):
    """
    Tìm lời giải bằng thuật toán A* (phiên bản đảm bảo tối ưu).
    """
    print("Solving with A* (Optimal Version)...")
    start_time = time.time()
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    
    tie_breaker = 0
    
    initial_h = heuristic(initial_painted, total_path_tiles)
    # Priority Queue: (priority, tie_breaker, cost, path, position, painted_tiles)
    pq = [(initial_h, tie_breaker, 0, [], tuple(start_pos), initial_painted)] 
    
    # `visited` lưu chi phí nhỏ nhất để đến một trạng thái
    visited = { (tuple(start_pos), initial_painted): 0 }

    while pq:
        _, _, cost, path, current_pos, painted_tiles = heapq.heappop(pq)
        
        current_state = (current_pos, painted_tiles)
        if cost > visited[current_state]:
            continue

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
            new_cost = cost + 1
            
            if new_state not in visited or new_cost < visited[new_state]:
                visited[new_state] = new_cost
                
                new_h = heuristic(new_painted_set, total_path_tiles)
                priority = new_cost + new_h # f(n) = g(n) + h(n)
                
                new_path = path + [direction]
                tie_breaker += 1
                heapq.heappush(pq, (priority, tie_breaker, new_cost, new_path, next_pos, new_painted_set))
                
    print("Không có lời giải")
    return None