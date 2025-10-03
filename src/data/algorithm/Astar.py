import heapq
import random
import time
from config import MAZE_ROWS, MAZE_COLS, PATH
from .func_algorithm import simulate_move, MOVES, reconstruct_path, get_heuristic_function

def astar_solve(maze, start_pos, heuristic_type="line_count"):
    """
    Giải quyết mê cung bằng thuật toán A* (A-star).

    Thuật toán này tìm ra đường đi có số bước di chuyển (trượt) ít nhất
    bằng cách cân bằng giữa hai yếu tố:
    1. g(n): Chi phí thực tế từ điểm bắt đầu đến trạng thái hiện tại (số bước đi).
    2. h(n): Chi phí ước tính (heuristic) từ trạng thái hiện tại đến đích.

    f(n) = g(n) + h(n)
    
    Lưu ý: Để A* đảm bảo tìm ra đường đi tối ưu, hàm heuristic (h) phải là
    "admissible" (không bao giờ đánh giá quá cao chi phí thực tế).
    `heuristic_line_count` là một lựa chọn tốt cho tiêu chí này.
    """
    total_path_tiles = set([(i, j) for i in range(len(maze)) for j in range(len(maze[0])) if maze[i][j] == 0])
    start_pos_tuple = tuple(start_pos)
    initial_painted = frozenset([start_pos_tuple])
    start_state = (start_pos_tuple, initial_painted)

    heuristic_func = get_heuristic_function(heuristic_type, maze)

    # --- A* отличия ---
    # g_score lưu chi phí (số bước đi) từ đầu đến một trạng thái.
    # Mặc định là vô cực cho mọi trạng thái.
    g_score = {start_state: 0}

    # f_score = g_score + heuristic. Hàng đợi sẽ ưu tiên f_score nhỏ nhất.
    initial_h_score = heuristic_func(initial_painted, total_path_tiles)
    f_score = {start_state: initial_h_score}

    unique_id = 0
    # Hàng đợi ưu tiên (priority queue) lưu (f_score, unique_id, state)
    pq = [(initial_h_score, unique_id, start_state)]
    
    # came_from thay thế cho 'visited' để lưu lại đường đi
    came_from = {start_state: (None, None)}
    
    num_of_states = 0
    num_of_visited = 0
    start_time = time.time()
    
    # Giữ lại logic hoạt ảnh tạm thời
    explored_for_anim = {0: [start_pos_tuple]}
    step_for_anim = 1

    while pq:
        _, _, current_state = heapq.heappop(pq)
        num_of_visited+=1
        
        current_pos, painted_tiles = current_state

        # Điều kiện thắng
        if len(painted_tiles) == len(total_path_tiles):
            path = reconstruct_path(came_from, start_state, current_state)
            return {
                "path": path, "steps": len(path), "visited": num_of_visited,
                "states": num_of_states, "time": time.time() - start_time, "explored": explored_for_anim
            }

        # --- Logic hoạt ảnh (tạm thời giữ lại) ---
        parent_state, last_move = came_from[current_state]
        if parent_state:
            _, newly_painted = simulate_move(
                parent_state[0], MAZE_ROWS, MAZE_COLS, last_move, maze
            )
            truly_new_tiles_for_anim = newly_painted - parent_state[1]
            if truly_new_tiles_for_anim:
                # Logic này có thể không tạo ra hoạt ảnh mượt mà cho A*
                # vì A* có thể chuyển giữa các nhánh khác nhau.
                explored_for_anim[step_for_anim] = sorted(list(truly_new_tiles_for_anim))
                step_for_anim += 1

        shuffled_moves = list(MOVES.keys())
        random.shuffle(shuffled_moves)
        # Khám phá các nước đi tiếp theo
        for move in shuffled_moves:
            next_pos, newly_painted_by_move = simulate_move(
                current_pos, MAZE_ROWS, MAZE_COLS, move, maze
            )

            if next_pos == current_pos:
                continue

            new_painted_frozenset = painted_tiles.union(newly_painted_by_move)
            new_state = (next_pos, new_painted_frozenset)

            # --- A* отличия ---
            # Chi phí để đến trạng thái lân cận này là chi phí đến trạng thái hiện tại + 1
            tentative_g_score = g_score.get(current_state, float('inf')) + 1

            # Nếu con đường mới này tốt hơn con đường cũ đã biết
            if tentative_g_score < g_score.get(new_state, float('inf')):
                # Cập nhật lại thông tin
                came_from[new_state] = (current_state, move)
                g_score[new_state] = tentative_g_score
                
                h_score = heuristic_func(new_painted_frozenset, total_path_tiles)
                new_f_score = tentative_g_score + h_score
                
                # Chỉ thêm vào hàng đợi nếu nó là một đường đi tốt hơn
                # hoặc là một trạng thái hoàn toàn mới.
                if new_state not in [item[2] for item in pq]:
                    num_of_states += 1
                    unique_id += 1
                    heapq.heappush(pq, (new_f_score, unique_id, new_state))

    # Trường hợp không tìm thấy đường đi
    return {
        "path": [], "steps": 0, "visited": len(came_from),
        "states": num_of_states, "time": time.time() - start_time, "explored": explored_for_anim
    }