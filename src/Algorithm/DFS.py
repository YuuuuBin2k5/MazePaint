# import collections
# import random
# import time
# from config import MAZE_ROWS, MAZE_COLS
# from .func_algorithm import simulate_move, MOVES

# def dfs_solve(maze, start_pos):
#     total_path_tiles = sum(r.count(0) for r in maze)
#     start_time = time.time()
    
#     ui_log = dict()
#     visited_count = 0
#     num_of_states = 0 # Số trạng thái được sinh ra

#     shuffled_moves = list(MOVES.keys())
#     random.shuffle(shuffled_moves)

#     def _backtrack(current_pos, current_painted, current_path, path_states):
#         nonlocal visited_count, num_of_states
        
#         # 1. TRƯỜNG HỢP CƠ SỞ (THÀNH CÔNG)
#         if len(current_painted) == total_path_tiles:
#             return current_path

#         current_state = (current_pos, current_painted)

#         # 2. KIỂM TRA CHU TRÌNH
#         if current_state in path_states:
#             return None
        
#         visited_count += 1

#         # GIAI ĐOẠN 1: PHÂN TÍCH VÀ GHI LOG
#         possible_new_paint = set()
#         next_steps_to_try = []

#         for move in shuffled_moves:
#             next_pos, newly_painted = simulate_move(
#                 current_pos, MAZE_ROWS, MAZE_COLS, move, maze
#             )
            
#             if next_pos != current_pos:
#                 # Mỗi bước đi hợp lệ sẽ sinh ra một trạng thái mới
#                 num_of_states += 1
                
#                 possible_new_paint.update(newly_painted)
                
#                 new_painted_set = frozenset(current_painted.union(newly_painted))
#                 next_steps_to_try.append((next_pos, new_painted_set, move))

#         ui_log[current_state] = possible_new_paint

#         # GIAI ĐOẠN 2: HÀNH ĐỘNG
#         for next_pos, new_painted_set, move in next_steps_to_try:
#             new_path_states = path_states.union({current_state})
            
#             result = _backtrack(
#                 next_pos, 
#                 new_painted_set, 
#                 current_path + [move],
#                 new_path_states
#             )
            
#             if result is not None:
#                 return result
        
#         return None

#     # Bắt đầu quá trình
#     initial_pos = tuple(start_pos)
#     initial_painted = frozenset([initial_pos])
#     path = _backtrack(initial_pos, initial_painted, [], frozenset())
    
#     end_time = time.time()

#     if path:
#         return {
#             "path": path,
#             "steps": len(path),
#             "visited": visited_count,     # Số trạng thái duy nhất đã khám phá
#             "states": num_of_states,      # Tổng số trạng thái đã được sinh ra
#             "time": end_time - start_time,
#             "ui_log": ui_log,
#         }
#     else:
#         return None

import random
import time
from config import MAZE_ROWS, MAZE_COLS, PATH
from .func_algorithm import simulate_move, MOVES, reconstruct_path_astar_ucs

def dfs_solve(maze, start_pos):
    """
    Giải quyết mê cung bằng Depth-First Search.
    """
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    start_state = (tuple(start_pos), initial_painted)

    stack = [start_state]
    visited = {start_state: [0, None, None]}
    num_of_states = 0
    visited_count = 0
    start_time = time.time()

    # explored: dict(step_index -> ordered list of tiles explored at that step)
    explored = dict()
    stt = 0
    while stack:
        current_state = stack.pop()
        current_pos, painted_tiles = current_state
        visited_count += 1

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

        shuffled_moves = list(MOVES.keys())
        random.shuffle(shuffled_moves)

        possible_paint = []
        local_seen = set()

        for move in shuffled_moves:
            next_pos, newly_painted = simulate_move(
                current_pos, MAZE_ROWS, MAZE_COLS, move, maze
            )

            if next_pos == current_pos:
                continue

            dr, dc = MOVES.get(move, (0,0))
            r, c = current_pos
            slide_tiles = []
            while (0 <= r + dr < MAZE_ROWS and 0 <= c + dc < MAZE_COLS and
                   maze[r + dr][c + dc] == PATH):
                r += dr
                c += dc
                if (r, c) not in local_seen:
                    slide_tiles.append((r, c))
                    local_seen.add((r, c))

            for t in slide_tiles:
                if t not in possible_paint:
                    possible_paint.append(t)

            new_painted_set = painted_tiles.union(newly_painted)
            new_state = (next_pos, new_painted_set)
            if new_state not in visited:
                num_of_states += 1
                visited[new_state] = [0, current_state, move]
                stack.append(new_state)

        explored[stt] = possible_paint
        stt += 1

    return None