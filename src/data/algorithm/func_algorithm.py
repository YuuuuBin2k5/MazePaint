import math
import collections
from config import MAZE_ROWS, MAZE_COLS, PATH
# Biến chứa 4 hướng di chuyển (dòng, cột)
MOVES = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}
def reconstruct_path_astar_ucs (visited, start_state, end_state):
    path = []
    current = end_state
    while current != start_state:
        _, parent, move = visited.get(current, [0, None, None])
        if parent is None:
            return []
        path.append(move)
        current = parent
    path.reverse()
    return path

def reconstruct_path(visited, start_state, end_state):
    """Hàm trợ giúp để tái tạo đường đi từ đích về điểm xuất phát."""
    path = []
    current = end_state
    while current != start_state:
        parent, move = visited[current]
        path.append(move)
        current = parent
    path.reverse() # Đảo ngược để có thứ tự từ đầu đến cuối
    return path

def simulate_move(start_pos, MAZE_ROWS, MAZE_COLS, direction, maze):
    """
    Giả lập một nước đi trượt trong game.
    Hàm này giờ sử dụng biến MOVES để code gọn gàng hơn.
    """
    row, col = start_pos
    path_painted = {start_pos}
    
    # Lấy vector di chuyển từ biến MOVES
    dr, dc = MOVES[direction]
    
    # Vòng lặp "trượt" cho đến khi gặp tường
    while 0<=row+dr< MAZE_ROWS and 0<=col+dc<MAZE_COLS and maze[row + dr][col + dc] == 0:
        row += dr
        col += dc
        path_painted.add((row, col))
    #vị trí sau khi di chuyển và những ô đã tô được    
    return (row, col), path_painted

def heuristic_is_not_done(painted_tiles, total_path_tiles):
    if len(painted_tiles) >= len(total_path_tiles):
        return 0
    # Thêm tie-breaker: số ô chưa tô làm secondary metric  
    return 1.0 + (len(total_path_tiles) - len(painted_tiles)) * 0.001

def heuristic_unpainted_count(painted_tiles, total_path_tiles):
    return len(total_path_tiles) - len(painted_tiles)

def heuristic_line_count(painted_tiles, total_path_tiles):
    unpainted_tiles = total_path_tiles - painted_tiles
    
    if not unpainted_tiles:
        return 0

    rows_with_unpainted_tiles = set()
    cols_with_unpainted_tiles = set()

    for r, c in unpainted_tiles:
        rows_with_unpainted_tiles.add(r)
        cols_with_unpainted_tiles.add(c)

    return min(len(rows_with_unpainted_tiles), len(cols_with_unpainted_tiles))

# Tìm các ô có thể tiếp cận bằng cách trượt
def find_connected_components(maze, start_pos):
    nodes_to_visit = {(r, c) for r in range(MAZE_ROWS) for c in range(MAZE_COLS) if maze[r][c] == 0}
    if not nodes_to_visit:
        return 0

    def bfs(start):
        dq = collections.deque([start])
        if start in nodes_to_visit:
            nodes_to_visit.remove(start)
        
        while dq:
            current_pos = dq.popleft()
            for direction in MOVES:
                reachable_node, reachable_paint = simulate_move(current_pos, MAZE_ROWS, MAZE_COLS, direction, maze)
                
                # Tìm ra những ô mới thực sự được tô trong cú trượt này
                newly_painted_tiles = reachable_paint & nodes_to_visit

                # THAY ĐỔI THEO YÊU CẦU:
                # Chỉ xử lý nếu cú trượt này tô được ít nhất một ô mới.
                if newly_painted_tiles:
                    
                    # Xóa tất cả các ô mới được tô khỏi tập nodes_to_visit
                    nodes_to_visit.difference_update(newly_painted_tiles)
                    
                    # Thêm điểm cuối vào hàng đợi để tiếp tục khám phá,
                    # nhưng chỉ khi điểm cuối đó chưa từng được thêm vào hàng đợi trước đây.
                    # Điều kiện `reachable_node in newly_painted_tiles` đảm bảo điều này.
                    if reachable_node in newly_painted_tiles:
                        dq.append(reachable_node)

    component_count = 0
    while nodes_to_visit:
        if start_pos in nodes_to_visit:
            bfs(start_pos)
        else:
            bfs(next(iter(nodes_to_visit)))
        component_count += 1
    
    return component_count

def get_heuristic_function(heuristic_type, maze):
    """
    Trả về hàm heuristic tương ứng với loại được chỉ định.
    CHỈ CÓ 2 HEURISTIC: not_done và optimistic_moves
    """
    
    if heuristic_type == "not_done":
        return lambda painted, total: heuristic_is_not_done(painted, total)
    elif heuristic_type == "line_count":
        return lambda painted, total: heuristic_line_count(painted, total)
    elif heuristic_type == "unpainted_count":
        return lambda painted, total: heuristic_unpainted_count(painted, total)
