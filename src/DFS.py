# # DFS.py
# import random
# import time
# from config import MAZE_ROWS, MAZE_COLS
# from func_algorithm import simulate_move, MOVES, reconstruct_path

# def dfs_solve(maze, start_pos):
#     print("Solving with DFS...")
#     total_path_tiles = sum(r.count(0) for r in maze)
#     initial_painted = frozenset([tuple(start_pos)])
#     start_state = (tuple(start_pos), initial_painted)


#     stack = [start_state]
    
#     visited = {start_state: (None, None)}
    
#     num_of_states = 0
#     visited_count = 0
#     start_time = time.time()
#     while stack:
#         current_pos, painted_tiles = stack.pop()
#         current_state = (current_pos, painted_tiles)
#         visited_count += 1

#         if len(painted_tiles) == total_path_tiles:
#             path = reconstruct_path(visited, start_state, current_state)
#             return {
#                 "path": path,
#                 "steps": len(path),
#                 "visited": visited_count,
#                 "states": num_of_states,
#                 "time": time.time() - start_time
#             }

#         # Logic shuffle giống hệt file BFS bạn gửi
#         shuffled_moves = list(MOVES.keys())
#         random.shuffle(shuffled_moves)
#         for move in shuffled_moves:
#             next_pos, newly_painted = simulate_move(current_pos, MAZE_ROWS, MAZE_COLS, move, maze)
            
#             if next_pos == current_pos:
#                 continue
            
#             new_painted_set = painted_tiles.union(newly_painted)
#             new_state = (next_pos, new_painted_set)
            
#             if new_state not in visited:
#                 num_of_states += 1
#                 visited[new_state] = (current_state, move)
#                 stack.append(new_state)              
#     return None
# DFS_backtracking.py
import random
import time
from config import MAZE_ROWS, MAZE_COLS
from func_algorithm import simulate_move, MOVES

def dfs_backtrack(maze, pos, painted, path, total_path_tiles, visited_states, counters):
    # Mỗi lần vào một state -> tăng visited_count
    counters["visited_count"] += 1

    # Nếu đã tô hết thì trả về kết quả
    if len(painted) == total_path_tiles:
        return path

    # Trộn thứ tự di chuyển để tránh bias
    moves = list(MOVES.keys())
    random.shuffle(moves)

    for move in moves:
        next_pos, newly_painted = simulate_move(pos, MAZE_ROWS, MAZE_COLS, move, maze)

        if next_pos == pos:
            continue

        new_painted = painted.union(newly_painted)
        new_state = (next_pos, new_painted)

        # Nếu state này đã thấy thì bỏ qua
        if new_state in visited_states:
            continue

        # Ghi nhận state mới
        visited_states.add(new_state)
        counters["num_of_states"] += 1

        # Đi sâu hơn
        result = dfs_backtrack(
            maze, next_pos, new_painted, path + [move], total_path_tiles, visited_states, counters
        )
        if result is not None:
            return result  # tìm thấy lời giải

        # Nếu không có đường, backtrack (visited_states vẫn giữ để tránh vòng lặp)
    return None


def dfs_solve(maze, start_pos):
    total_path_tiles = sum(r.count(0) for r in maze)
    start = tuple(start_pos)
    painted = frozenset([start])

    # Các biến đếm
    counters = {
        "visited_count": 0,
        "num_of_states": 0
    }

    visited_states = set()
    visited_states.add((start, painted))

    start_time = time.time()
    path = dfs_backtrack(maze, start, painted, [], total_path_tiles, visited_states, counters)

    if path is not None:
        return {
            "path": path,
            "steps": len(path),
            "visited": counters["visited_count"],
            "states": counters["num_of_states"],
            "time": time.time() - start_time
        }
    else:
        return None
