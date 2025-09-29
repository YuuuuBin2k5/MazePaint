# func_algorithm.py
import math
from config import MAZE_ROWS, MAZE_COLS
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

def heuristic(painted_tiles, total_path_tiles):
    unpainted = total_path_tiles - len(painted_tiles)
    if unpainted == 0:
        return 0
    
    # Số ô tối đa có thể tô trong 1 nước đi là chiều dài hoặc chiều rộng của mê cung
    max_paint_per_move = max(MAZE_ROWS, MAZE_COLS)
    
    # h(n) = ceil(số ô còn lại / số ô tối đa có thể tô trong 1 lần)
    # Luôn đảm bảo không ước tính quá cao
    return math.ceil(unpainted / max_paint_per_move)
    # return total_path_tiles - len(painted_tiles)
    # return 1 if len(painted_tiles) < total_path_tiles else 0
