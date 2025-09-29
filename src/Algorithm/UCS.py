import collections
import random
import time
import heapq
from config import MAZE_ROWS, MAZE_COLS
from .func_algorithm import simulate_move, MOVES, reconstruct_path_astar_ucs

def ucs_solve(maze, start_pos):
    """
    Giải quyết mê cung bằng Uniform Cost Search với chi phí mỗi bước là 1.
    Thuật toán này đảm bảo tìm ra đường đi có số bước ngắn nhất.
    """
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    start_state = (tuple(start_pos), initial_painted)
    
    tie_breaker = 0
    pq = [(0, tie_breaker, start_state)] 
    
    visited = {start_state: [0, None, None]}
    
    explored = dict()
    stt = 0
    visited_count = 0
    num_of_states = 0
    start_time = time.time()

    while pq:
        cost, _, current_state = heapq.heappop(pq)
        
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
                if newly_painted:
                    new_painted_set = frozenset(painted_tiles.union(newly_painted))
                    new_state = (next_pos, new_painted_set)
                    next_steps_to_try.append((new_state, move))
        
        # **THAY ĐỔI:** Cập nhật cấu trúc explored theo yêu cầu
        explored[stt] = possible_new_paint
        stt += 1

        # GIAI ĐOẠN 2: HÀNH ĐỘNG
        for new_state, move in next_steps_to_try:
            new_cost = cost + 1
            
            if new_state not in visited or new_cost < visited[new_state][0]:
                if new_state not in visited:
                    num_of_states += 1
                visited[new_state] = [new_cost, current_state, move]
                tie_breaker += 1
                heapq.heappush(pq, (new_cost, tie_breaker, new_state))

    return None