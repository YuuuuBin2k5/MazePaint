import heapq
import random
import time
from config import MAZE_ROWS, MAZE_COLS
# Đảm bảo import đúng hàm heuristic và hàm dựng lại đường đi
from .func_algorithm import simulate_move, MOVES, reconstruct_path_astar_ucs, heuristic

def astar_solve(maze, start_pos):
    """
    Giải quyết mê cung bằng A* Search và ghi lại log tuần tự.
    """
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    start_state = (tuple(start_pos), initial_painted)
    
    tie_breaker = 0
    # Priority Queue: (priority, tie_breaker, cost, state)
    # priority = cost + heuristic
    initial_h = heuristic(initial_painted, total_path_tiles)
    pq = [(initial_h, tie_breaker, 0, start_state)] 
    
    # Visited: { state: [min_cost, parent_state, move] }
    visited = {start_state: [0, None, None]}

    # **CẢI TIẾN:** Thêm explored và stt
    explored = dict()
    stt = 0

    visited_count = 0
    num_of_states = 0
    start_time = time.time()

    while pq:
        _, _, cost, current_state = heapq.heappop(pq)
        
        if cost > visited[current_state][0]:
            continue

        visited_count += 1
        current_pos, painted_tiles = current_state

        if len(painted_tiles) == total_path_tiles:
            path = reconstruct_path_astar_ucs(visited, start_state, current_state)
            return {
                "path": path,
                "steps": len(path),
                "visited": visited_count,
                "states": num_of_states,
                "time": time.time() - start_time,
                "explored": explored
            }

        
        # GIAI ĐOẠN 1: PHÂN TÍCH
        possible_new_paint = set()
        next_steps_to_try = []
        shuffled_moves = list(MOVES.keys())
        random.shuffle(shuffled_moves)
        
        for move in shuffled_moves:
            next_pos, newly_painted = simulate_move(current_pos, MAZE_ROWS, MAZE_COLS, move, maze)
            if next_pos != current_pos:
                possible_new_paint.update(newly_painted)
                new_painted_set = frozenset(painted_tiles.union(newly_painted))
                new_state = (next_pos, new_painted_set)
                next_steps_to_try.append((new_state, move, new_painted_set))
        
        explored[stt] = possible_new_paint
        stt += 1
        
        # GIAI ĐOẠN 2: HÀNH ĐỘNG
        for new_state, move, new_painted_set in next_steps_to_try:
            new_cost = cost + 1 # cost là g(n), chi phí thực tế từ điểm bắt đầu
            
            if new_state not in visited or new_cost < visited[new_state][0]:
                if new_state not in visited:
                    num_of_states += 1
                
                visited[new_state] = [new_cost, current_state, move]
                
                # new_h là h(n), chi phí ước tính đến đích
                new_h = heuristic(new_painted_set, total_path_tiles)
                # priority là f(n) = g(n) + h(n)
                priority = new_cost + new_h
                
                tie_breaker += 1
                heapq.heappush(pq, (priority, tie_breaker, new_cost, new_state))

    return None