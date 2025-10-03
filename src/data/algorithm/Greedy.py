import heapq
import random
import time
from config import MAZE_ROWS, MAZE_COLS, PATH
from .func_algorithm import simulate_move, MOVES, reconstruct_path, get_heuristic_function

def greedy_solve(maze, start_pos, heuristic_type="unpainted_count"):
    """
    Giải quyết mê cung bằng Greedy Best-First Search (Phiên bản chuẩn cuối cùng).
    
    Đã sửa lỗi logic cốt lõi về việc bỏ qua các nước đi không tô màu mới,
    đảm bảo thuật toán có thể giải được tất cả các map có lời giải.
    Đồng thời cải tiến để tránh xử lý lại các trạng thái đã khám phá xong.
    """
    total_path_tiles = set([(i, j) for i in range(len(maze)) for j in range(len(maze[0])) if maze[i][j] == 0])
    start_pos_tuple = tuple(start_pos)
    initial_painted = frozenset([start_pos_tuple])
    start_state = (start_pos_tuple, initial_painted)

    heuristic_func = get_heuristic_function(heuristic_type, maze)

    unique_id = 0
    pq = [(heuristic_func(initial_painted, total_path_tiles), unique_id, start_state)]
    
    visited = {start_state: (None, None)}
    num_of_states = 0
    num_of_visited = 0
    start_time = time.time()
    
    # Set để lưu các trạng thái đã được lấy ra khỏi queue và xử lý xong
    explored_states = set()

    explored = {0: [start_pos_tuple]}
    step = 1

    while pq:
        _, _, current_state = heapq.heappop(pq)
        num_of_visited+=1
        # Nếu trạng thái này đã xử lý xong, bỏ qua
        if current_state in explored_states:
            continue
        
        current_pos, painted_tiles = current_state

        # Ghi lại hoạt ảnh cho bước đi này
        parent_state, last_move = visited[current_state]
        if parent_state:
            _, newly_painted = simulate_move(
                parent_state[0], MAZE_ROWS, MAZE_COLS, last_move, maze
            )
            truly_new_tiles_for_anim = newly_painted - parent_state[1]
            if truly_new_tiles_for_anim:
                explored[step] = sorted(list(truly_new_tiles_for_anim))
                step += 1
        
        # Đánh dấu trạng thái này là đã xử lý xong
        explored_states.add(current_state)

        # Điều kiện thắng
        if len(painted_tiles) == len(total_path_tiles):
            path = reconstruct_path(visited, start_state, current_state)
            return {
                "path": path, "steps": len(path), "visited": num_of_visited,
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
                visited[new_state] = (current_state, move)
                unique_id += 1
                heapq.heappush(pq, (heuristic_func(new_painted_frozenset, total_path_tiles), unique_id, new_state))

    # Trường hợp không tìm thấy đường đi
    return {
        "path": [], "steps": 0, "visited": len(visited),
        "states": num_of_states, "time": time.time() - start_time, "explored": explored
    }