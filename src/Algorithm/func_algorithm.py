# func_algorithm.py
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
    path_painted = set()
    
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
    return 1 if len(painted_tiles) < total_path_tiles else 0

def heuristic_unpainted_count(painted_tiles, total_path_tiles):
    return total_path_tiles - len(painted_tiles)

def heuristic_optimistic_moves(painted_tiles, total_path_tiles):
    unpainted = total_path_tiles - len(painted_tiles)
    if unpainted == 0:
        return 0
    
    # Số ô tối đa có thể tô trong 1 nước đi là chiều dài hoặc chiều rộng của mê cung
    max_paint_per_move = max(MAZE_ROWS, MAZE_COLS)
    return math.ceil(unpainted / max_paint_per_move)

def _count_unpainted_components_helper(painted_tiles, maze):
    nodes_to_visit = set()
    for r in range(MAZE_ROWS):
        for c in range(MAZE_COLS):
            # 0 là giá trị của đường đi (PATH)
            if maze[r][c] == 0 and (r, c) not in painted_tiles:
                nodes_to_visit.add((r, c))

    if not nodes_to_visit:
        return 0

    component_count = 0
    moves_4_dir = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
    
    while nodes_to_visit:
        component_count += 1
        start_node = nodes_to_visit.pop()
        dq = collections.deque([start_node])
        
        while dq:
            r, c = dq.popleft()
            for dr, dc in moves_4_dir:
                neighbor = (r + dr, c + dc)
                if neighbor in nodes_to_visit:
                    nodes_to_visit.remove(neighbor)
                    dq.append(neighbor)
    
    return component_count

def heuristic_unpainted_components(painted_tiles, total_path_tiles, maze):
    unpainted_count = total_path_tiles - len(painted_tiles)
    if unpainted_count == 0:
        return 0

    return _count_unpainted_components_helper(painted_tiles, maze)  # Bỏ MAZE_ROWS, MAZE_COLS

# ...existing code...
def heuristic(painted_tiles, total_path_tiles):
    """
    Hàm heuristic gốc - trả về số ô chưa tô (admissible).
    """
    return total_path_tiles - len(painted_tiles)

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
    """
    if heuristic_type == "not_done":
        return lambda painted, total: heuristic_is_not_done(painted, total)
    elif heuristic_type == "unpainted_count":
        return lambda painted, total: heuristic_unpainted_count(painted, total)
    elif heuristic_type == "optimistic_moves":
        return lambda painted, total: heuristic_optimistic_moves(painted, total)
    elif heuristic_type == "unpainted_components":
        return lambda painted, total: heuristic_unpainted_components(painted, total, maze)
    else:
        # Default fallback to original heuristic
        return lambda painted, total: heuristic(painted, total)
