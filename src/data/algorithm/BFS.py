import collections
import random
import time
from config import MAZE_ROWS, MAZE_COLS, PATH
from .func_algorithm import simulate_move, MOVES, reconstruct_path


def bfs_solve(maze, start_pos):
    """
    Giải quyết mê cung bằng thuật toán BFS (Phiên bản chuẩn cuối cùng).
    
    Đã sửa lỗi logic cốt lõi về việc bỏ qua các nước đi không tô màu mới,
    đảm bảo thuật toán có thể giải được tất cả các map có lời giải.
    """
    total_path_tiles = sum(r.count(PATH) for r in maze)
    
    start_pos_tuple = tuple(start_pos)
    initial_painted = frozenset([start_pos_tuple])
    start_state = (start_pos_tuple, initial_painted)

    queue = collections.deque([start_state])
    visited = {start_state: (None, None)}
    
    num_of_states = 0
    num_of_visited = 0
    start_time = time.time()

    explored = {0: [start_pos_tuple]}
    step = 1
    
    while queue:
        level_size = len(queue)
        if level_size == 0:
            break

        tiles_discovered_in_this_level = []

        for _ in range(level_size):
            current_pos, painted_tiles = queue.popleft()
            num_of_visited+=1
            current_state = (current_pos, painted_tiles)

            if len(painted_tiles) == total_path_tiles:
                path = reconstruct_path(visited, start_state, current_state)
                if tiles_discovered_in_this_level:
                     explored[step] = sorted(list(set(tiles_discovered_in_this_level)))
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

                # Một trạng thái mới được định nghĩa bởi (vị trí mới, tập hợp ô đã tô mới).
                new_painted_set = painted_tiles.union(newly_painted)
                new_state = (next_pos, new_painted_set)

                if new_state not in visited:
                    visited[new_state] = (current_state, move)
                    num_of_states+=1
                    queue.append(new_state)

                    # Logic ghi lại hoạt ảnh vẫn chỉ tô các ô mới để hiệu ứng đẹp
                    truly_new_tiles = new_painted_set - painted_tiles
                    if truly_new_tiles:
                        tiles_discovered_in_this_level.extend(list(truly_new_tiles))

        if tiles_discovered_in_this_level:
            unique_new_tiles = sorted(list(set(tiles_discovered_in_this_level)))
            explored[step] = unique_new_tiles
            step += 1
            
    # Chỉ return ở đây khi và chỉ khi queue thực sự rỗng (không còn gì để khám phá)
    return {
        "path": [], "steps": 0, "visited": len(visited), 
        "states": num_of_states, "time": time.time() - start_time, "explored": explored
    }