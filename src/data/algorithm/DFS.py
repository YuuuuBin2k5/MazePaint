import random
import time
from config import MAZE_ROWS, MAZE_COLS, PATH
from .func_algorithm import simulate_move, MOVES, reconstruct_path_astar_ucs

def dfs_solve(maze, start_pos):
    """
    Giải quyết mê cung bằng Depth-First Search (Phiên bản chuẩn cuối cùng).
    
    Đã sửa lỗi logic cốt lõi về việc bỏ qua các nước đi không tô màu mới,
    đảm bảo thuật toán có thể giải được tất cả các map có lời giải.
    """
    total_path_tiles = sum(r.count(0) for r in maze)
    start_pos_tuple = tuple(start_pos)
    initial_painted = frozenset([start_pos_tuple])
    start_state = (start_pos_tuple, initial_painted)

    # Stack chứa (state, path_to_state)
    stack = [(start_state, [])]
    visited = {start_state: [0, None, None]}
    num_of_states = 0
    num_of_visited = 0
    start_time = time.time()

    explored = {0: [start_pos_tuple]}
    step = 1

    while stack:
        current_state, path = stack.pop()
        num_of_visited+=1
        current_pos, painted_tiles = current_state

        # Ghi lại hoạt ảnh cho bước đi sâu này
        if path:
            last_move = path[-1]
            parent_state = visited[current_state][1]
            if parent_state:
                 _, newly_painted = simulate_move(
                    parent_state[0], MAZE_ROWS, MAZE_COLS, last_move, maze
                )
                 truly_new_tiles_for_anim = newly_painted - parent_state[1]
                 if truly_new_tiles_for_anim:
                    explored[step] = sorted(list(truly_new_tiles_for_anim))
                    step += 1

        # Điều kiện thắng
        if len(painted_tiles) == total_path_tiles:
            final_path = reconstruct_path_astar_ucs(visited, start_state, current_state)
            return {
                "path": final_path, "steps": len(final_path), "visited": len(visited),
                "states": num_of_states, "time": time.time() - start_time, "explored": explored
            }
        shuffled_moves = list(MOVES.keys())
        random.shuffle(shuffled_moves)
        # Khám phá các nước đi tiếp theo
        for move in shuffled_moves:
            next_pos, newly_painted_by_move = simulate_move(
                current_pos, MAZE_ROWS, MAZE_COLS, move, maze
            )

            if next_pos == current_pos:
                continue

            # Tạo trạng thái mới dựa trên vị trí mới và tập hợp ô đã tô mới.
            new_painted_frozenset = painted_tiles.union(newly_painted_by_move)
            new_state = (next_pos, new_painted_frozenset)

            # Chỉ khám phá nếu trạng thái mới này chưa từng được ghé thăm.
            # Điều này cho phép các nước đi di chuyển qua ô đã tô.
            if new_state not in visited:
                num_of_states += 1
                visited[new_state] = [0, current_state, move]
                stack.append((new_state, path + [move]))

    # Trường hợp không tìm thấy đường đi
    return {
        "path": [], "steps": 0, "visited": len(visited),
        "states": num_of_states, "time": time.time() - start_time, "explored": explored
    }