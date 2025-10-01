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

def find_connected_components(maze):
    """
    Count 4-connected components of PATH tiles in the maze.
    Returns integer number of components (0 if no PATH tiles).
    """
    nodes_to_visit = set()
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0

    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == PATH:
                nodes_to_visit.add((r, c))

    component_count = 0
    dq = collections.deque()

    while nodes_to_visit:
        component_count += 1
        start_node = nodes_to_visit.pop()
        dq.append(start_node)

        while dq:
            r, c = dq.popleft()
            for dr, dc in MOVES.values():
                nr, nc = r + dr, c + dc
                neighbor = (nr, nc)
                if neighbor in nodes_to_visit:
                    nodes_to_visit.remove(neighbor)
                    dq.append(neighbor)

    return component_count

def is_solvable_by_connectivity(maze, start_pos=(1,1)):
    """
    Quick check: returns True if all PATH tiles are in the same connected component
    and the start_pos is a PATH tile. This is a fast necessary condition for solvable.
    (Does not fully guarantee sliding-solver existence but is a strong quick check.)
    """
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    sr, sc = start_pos
    if not (0 <= sr < rows and 0 <= sc < cols):
        return False
    if maze[sr][sc] != PATH:
        return False
    comps = find_connected_components(maze)
    return comps == 1

def find_reachable_by_slides(maze, start_pos):
    """
    Trả về tập các ô PATH có thể được "đi qua" hoặc dừng tại khi di chuyển theo luật sliding
    (player trượt tới khi gặp tường). Bao gồm cả ô start.
    """
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    sr, sc = start_pos
    if not (0 <= sr < rows and 0 <= sc < cols):
        return set()
    if maze[sr][sc] != PATH:
        return set()

    reachable = set()
    stop_positions = set()
    dq = collections.deque()

    # start is both reachable and a stop position (you can start sliding from here)
    reachable.add((sr, sc))
    stop_positions.add((sr, sc))
    dq.append((sr, sc))

    while dq:
        r, c = dq.popleft()
        # for each slide direction, simulate full slide
        for dr, dc in MOVES.values():
            nr, nc = r, c
            slid = []
            # move while next cell is PATH
            while 0 <= nr + dr < rows and 0 <= nc + dc < cols and maze[nr + dr][nc + dc] == PATH:
                nr += dr
                nc += dc
                slid.append((nr, nc))
            if not slid:
                continue
            # all tiles passed during slide are reachable (paintable)
            for t in slid:
                if t not in reachable:
                    reachable.add(t)
            stop = (nr, nc)
            # also consider the stop position as a node to expand further
            if stop not in stop_positions:
                stop_positions.add(stop)
                dq.append(stop)
    # include stop positions too (they are reachable by being at those coordinates)
    reachable |= stop_positions
    return reachable

def is_solvable_by_sliding(maze, start_pos=(1,1)):
    """
    Kiểm tra nhanh: trả về True nếu mọi ô PATH trong maze nằm trong tập reachable
    theo cơ chế slide-from-start. (Phù hợp với cơ chế trò chơi của bạn.)
    """
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    # collect all PATH tiles
    all_path = {(r,c) for r in range(rows) for c in range(cols) if maze[r][c] == PATH}
    if not all_path:
        return False
    reachable = find_reachable_by_slides(maze, start_pos)
    # tất cả ô PATH phải nằm trong reachable để có thể tô hết
    return all_path.issubset(reachable)
