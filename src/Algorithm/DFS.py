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

import collections
import random
import time
from config import MAZE_ROWS, MAZE_COLS
from .func_algorithm import simulate_move, MOVES

def dfs_solve(maze, start_pos):
    """
    Giải quyết mê cung bằng backtracking thuần túy, sử dụng 'explored' để ghi log tuần tự.
    """
    total_path_tiles = sum(r.count(0) for r in maze)
    start_time = time.time()
    
    explored = dict()
    stt = 0
    
    visited_count = 0
    num_of_states = 0

    shuffled_moves = list(MOVES.keys())
    random.shuffle(shuffled_moves)

    def _backtrack(current_pos, current_painted, current_path, path_states):
        nonlocal visited_count, num_of_states, stt
        
        if len(current_painted) == total_path_tiles:
            return current_path

        current_state = (current_pos, current_painted)

        if current_state in path_states:
            return None
        
        visited_count += 1

        possible_paint = set()
        next_steps_to_try = []

        for move in shuffled_moves:
            next_pos, newly_painted = simulate_move(
                current_pos, MAZE_ROWS, MAZE_COLS, move, maze
            )
            
            if next_pos != current_pos:
                num_of_states += 1
                possible_paint.update(newly_painted)
                new_painted_set = frozenset(current_painted.union(newly_painted))
                next_steps_to_try.append((next_pos, new_painted_set, move))

        # **CẢI TIẾN:** Ghi log vào `explored` với key là số thứ tự `stt`
        explored[stt] = possible_paint
        stt+=1

        # GIAI ĐOẠN 2: HÀNH ĐỘNG
        for next_pos, new_painted_set, move in next_steps_to_try:
            new_path_states = path_states.union({current_state})
            
            result = _backtrack(
                next_pos, 
                new_painted_set, 
                current_path + [move],
                new_path_states
            )
            
            if result is not None:
                return result
        
        return None

    initial_pos = tuple(start_pos)
    initial_painted = frozenset([initial_pos])
    path = _backtrack(initial_pos, initial_painted, [], frozenset())
    
    end_time = time.time()

    if path:
        return {
            "path": path,
            "steps": len(path),
            "visited": visited_count,
            "states": num_of_states,
            "time": end_time - start_time,
            "explored": explored
        }
    else:
        return None