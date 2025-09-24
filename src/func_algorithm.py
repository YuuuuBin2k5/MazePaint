# func_algorithm.py
from config import MAZE_ROWS, MAZE_COLS
# Biến chứa 4 hướng di chuyển (dòng, cột)
DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}

def simulate_move(start_pos, MAZE_ROWS, MAZE_COLS, direction, maze):
    """
    Giả lập một nước đi trượt trong game.
    Hàm này giờ sử dụng biến DIRECTIONS để code gọn gàng hơn.
    """
    row, col = start_pos
    path_painted = set()
    
    # Lấy vector di chuyển từ biến DIRECTIONS
    dr, dc = DIRECTIONS[direction]
    
    # Vòng lặp "trượt" cho đến khi gặp tường
    while 0<=row+dr< MAZE_ROWS and 0<=col+dc<MAZE_COLS and maze[row + dr][col + dc] == 0:
        row += dr
        col += dc
        path_painted.add((row, col))
    #vị trí sau khi di chuyển và những ô đã tô được    
    return (row, col), path_painted
# func_algorithm.py

def heuristic(painted_tiles, total_path_tiles):
    """
    Hàm heuristic (hàm ước tính):
    Ước tính chi phí còn lại để đến đích bằng cách đếm số ô chưa được tô màu.
    """
    """
    Heuristic hợp lệ (admissible) và đơn giản nhất.
    Nó ước tính rằng chúng ta cần ít nhất 1 bước nữa để thắng.
    """
    return 1 if len(painted_tiles) < total_path_tiles else 0

def manhattan_distance_heuristic(player_pos, painted_tiles, maze):
    """
    Heuristic hiệu quả hơn: Tìm khoảng cách Manhattan đến ô chưa được tô xa nhất.
    """
    unpainted_coords = []
    # Tìm tất cả các ô chưa được tô
    for r, row_data in enumerate(maze):
        for c, tile in enumerate(row_data):
            if tile == 0 and (r, c) not in painted_tiles:
                unpainted_coords.append((r, c))

    if not unpainted_coords:
        return 0 # Không còn ô nào để tô

    max_dist = 0
    px, py = player_pos
    # Tìm khoảng cách lớn nhất từ người chơi đến một ô chưa được tô
    for tx, ty in unpainted_coords:
        dist = abs(px - tx) + abs(py - ty)
        if dist > max_dist:
            max_dist = dist
    
    return max_dist