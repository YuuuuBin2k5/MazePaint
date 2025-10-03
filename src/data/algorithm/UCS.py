import collections
import random
import time
import heapq
from config import MAZE_ROWS, MAZE_COLS, PATH
from .func_algorithm import simulate_move, MOVES, reconstruct_path_astar_ucs

def ucs_solve(maze, start_pos):
    """
    Giải quyết mê cung bằng Uniform Cost Search (Phiên bản chuẩn cuối cùng).
    
    Đã sửa lỗi logic cốt lõi về việc bỏ qua các nước đi không tô màu mới,
    đảm bảo thuật toán có thể giải được tất cả các map có lời giải.
    """
    total_path_tiles = sum(r.count(PATH) for r in maze)
    
    start_pos_tuple = tuple(start_pos)
    initial_painted = frozenset([start_pos_tuple])
    start_state = (start_pos_tuple, initial_painted)

    unique_id = 0
    pq = [(0, unique_id, start_state)]
    
    visited = {start_state: [0, None, None]}
    num_of_states = 0
    num_of_visited = 0
    start_time = time.time()

    explored = {0: [start_pos_tuple]}
    
    tiles_by_cost = collections.defaultdict(list)

    while pq:
        cost, _, current_state = heapq.heappop(pq)
        num_of_visited+=1
        if cost > visited[current_state][0]:
            continue

        current_pos, painted_tiles = current_state

        if len(painted_tiles) == total_path_tiles:
            sorted_costs = sorted(tiles_by_cost.keys())
            step = 1
            for c in sorted_costs:
                unique_new_tiles = sorted(list(set(tiles_by_cost[c])))
                if unique_new_tiles:
                    explored[step] = unique_new_tiles
                    step += 1
            
            path = reconstruct_path_astar_ucs(visited, start_state, current_state)
            return {
                "path": path, "steps": len(path), "visited": num_of_visited,
                "states": num_of_states, "time": time.time() - start_time, "explored": explored
            }
        shuffled_moves = list(MOVES.keys())
        random.shuffle(shuffled_moves)
        for move in shuffled_moves:
            next_pos, newly_painted = simulate_move(
                current_pos, MAZE_ROWS, MAZE_COLS, move, maze
            )

            if next_pos == current_pos:
                continue

            # Tạo trạng thái mới dựa trên vị trí mới và tập hợp ô đã tô mới.
            new_painted_set = painted_tiles.union(newly_painted)
            new_state = (next_pos, new_painted_set)
            new_cost = cost + 1

            # Chỉ khám phá nếu trạng thái mới chưa từng được ghé thăm
            # hoặc tìm thấy một con đường tốt hơn (chi phí thấp hơn) đến nó.
            if new_state not in visited or new_cost < visited[new_state][0]:
                visited[new_state] = [new_cost, current_state, move]
                unique_id += 1
                num_of_states += 1
                heapq.heappush(pq, (new_cost, unique_id, new_state))

                # Logic ghi lại hoạt ảnh vẫn chỉ tô các ô mới để hiệu ứng đẹp
                truly_new_tiles = new_painted_set - painted_tiles
                if truly_new_tiles:
                    tiles_by_cost[new_cost].extend(list(truly_new_tiles))
            
    # Tổng hợp hoạt ảnh và trả về kết quả
    sorted_costs = sorted(tiles_by_cost.keys())
    step = 1
    for c in sorted_costs:
        unique_new_tiles = sorted(list(set(tiles_by_cost[c])))
        if unique_new_tiles:
            explored[step] = unique_new_tiles
            step += 1

    return {
        "path": [], "steps": 0, "visited": len(visited), 
        "states": num_of_states, "time": time.time() - start_time, "explored": explored
    }