# main.py
import pygame
import copy
from config import *
from ui import *
from func_game import *
from BFS import bfs_solve
from DFS import dfs_solve
from UCS import ucs_solve
from Astar import astar_solve
from Greedy import greedy_solve
from maps import *

# --- KHỞI TẠO PYGAME VÀ CÁC THÀNH PHẦN ---
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
font_large = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 28)
clock = pygame.time.Clock()

# --- KHAI BÁO BIẾN TRẠNG THÁI ---
all_maps = {"LEVEL 1": LEVEL_ONE, "LEVEL 2": LEVEL_TWO, 
            "LEVEL 3": LEVEL_THREE, "LEVEL 4": LEVEL_FOUR,
            "LEVEL 5": LEVEL_FIVE, "LEVEL 6": LEVEL_SIX,
            "LEVEL 7": LEVEL_SEVEN}
map_names = list(all_maps.keys())
current_map_index = 0
current_maze = all_maps[map_names[current_map_index]]

maze_rows = len(current_maze)
maze_cols = len(current_maze[0])

algorithm = "Player"
move_count = 0

# KHỞI TẠO GAME LẦN ĐẦU
player_pos = [1, 1]
painted_tiles = [[False for _ in range(maze_cols)] for _ in range(maze_rows)]
painted_tiles[player_pos[0]][player_pos[1]] = True
board_before_player_moves = None
game_won = False
solving_path = None
history_list = []

time_since_last_move = 0
SOLVER_MOVE_INTERVAL = 100

# --- KHAI BÁO RECT CHO CÁC BUTTON ---
map_rect = pygame.Rect(840, 100, 240, 60)
player_rect = pygame.Rect(840, 320, 240, 60)
solver_rect = pygame.Rect(840, 400, 240, 60)
restart_rect = pygame.Rect(840, 480, 240, 60)
history_rect = pygame.Rect(840, 560, 240, 60)

# --- VÒNG LẶP CHÍNH ---
running = True
while running:
    dt = clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if not solving_path:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # NÚT MAP: Chuyển map
                if map_rect.collidepoint(event.pos):
                    current_map_index = (current_map_index + 1) % len(map_names)
                    current_maze = all_maps[map_names[current_map_index]]
                    # Reset inline
                    player_pos = [1, 1]
                    painted_tiles = [[False for _ in range(maze_cols)] for _ in range(maze_rows)]
                    painted_tiles[player_pos[0]][player_pos[1]] = True
                    board_before_player_moves = None
                    game_won = False
                    solving_path = None
                    move_count = 0

                # NÚT CHỌN THUẬT TOÁN
                elif player_rect.collidepoint(event.pos):
                    algo = ask_algorithm()
                    if algo:
                        algorithm = algo

                # NÚT SOLVE
                elif solver_rect.collidepoint(event.pos):
                    # Chỉ chạy khi thuật toán không phải là "Player"
                    if algorithm != "Player":
                        # 1. Reset trạng thái game về ban đầu để chuẩn bị giải
                        player_pos = [1, 1]
                        painted_tiles = [[False for _ in range(maze_cols)] for _ in range(maze_rows)]
                        painted_tiles[player_pos[0]][player_pos[1]] = True
                        board_before_player_moves = None
                        game_won = False
                        move_count = 0

                        # 2. Gọi hàm solver tương ứng với thuật toán đã chọn
                        result = None
                        if algorithm == "BFS":
                            result = bfs_solve(current_maze, [1,1])
                        elif algorithm == "DFS":
                            result = dfs_solve(current_maze, [1,1])
                        elif algorithm == "UCS":
                            result = ucs_solve(current_maze, [1,1])
                        elif algorithm == "Greedy":
                            result = greedy_solve(current_maze, [1,1])
                        elif algorithm == "Astar":
                            result = astar_solve(current_maze, [1,1])
                        
                        # 3. Xử lý kết quả trả về từ solver
                        if result:
                            # Nếu có lời giải, lấy đường đi để bắt đầu tự động chạy
                            solving_path = result["path"]
                            
                            # Lưu thông tin chi tiết vào lịch sử
                            history_list.append((
                                f"N{map_names}",    # Lượt chơi hiện tại
                                algorithm,              # Thuật toán đã dùng
                                result                  # Toàn bộ từ điển kết quả
                            ))
                        else:
                            # Nếu không có lời giải, vẫn lưu thông tin thất bại
                            history_list.append((
                                f"N{map_names}",
                                algorithm,
                                None
                            ))

                # NÚT RESTART
                elif restart_rect.collidepoint(event.pos):
                    player_pos = [1, 1]
                    painted_tiles = [[False for _ in range(maze_cols)] for _ in range(maze_rows)]
                    painted_tiles[player_pos[0]][player_pos[1]] = True
                    board_before_player_moves = None
                    game_won = False
                    solving_path = None
                    move_count = 0

                # NÚT HISTORY
                elif history_rect.collidepoint(event.pos):
                    history_list.clear()

            # Xử lý di chuyển bằng bàn phím
            if event.type == pygame.KEYDOWN and not game_won:
                direction = handle_input(event)
                if direction:
                    if board_before_player_moves is None:
                        board_before_player_moves = (copy.deepcopy(player_pos), [row[:] for row in painted_tiles])
                    move_count+=1                        
                    player_pos, painted_tiles = move_player(player_pos, MAZE_ROWS, MAZE_COLS, direction, current_maze, painted_tiles)
                    game_won = check_win_condition(current_maze, painted_tiles)

    # Tự động giải
    if solving_path:
        time_since_last_move += dt
        if time_since_last_move > SOLVER_MOVE_INTERVAL:
            time_since_last_move = 0
            if solving_path:
                next_move = solving_path.pop(0)
                player_pos, painted_tiles = move_player(player_pos,MAZE_ROWS, MAZE_COLS , next_move, current_maze, painted_tiles)
                move_count +=1
                if not solving_path:
                    game_won = check_win_condition(current_maze, painted_tiles)

    # --- VẼ LÊN MÀN HÌNH ---
    screen.fill(BLACK)
    draw_board(screen, current_maze, painted_tiles, player_pos, BOARD_X, BOARD_Y)

    draw_button(screen, font_small, map_rect, DARK_BLUE, f"MAP: {map_names[current_map_index]}")
    draw_button(screen, font_small, player_rect, DARK_BLUE, algorithm)
    draw_button(screen, font_small, solver_rect, DARK_BLUE, "SOLVE")
    draw_button(screen, font_small, restart_rect, DARK_BLUE, "RESTART")
    draw_button(screen, font_small, history_rect, DARK_BLUE, "CLEAR HISTORY")
    
    draw_move_count(screen, 840, 20, font_small, move_count)

    # draw_history_box(screen, font_small, history_list)
    
    if game_won:
        draw_win_message(screen, font_large)

    pygame.display.flip()
    
pygame.quit()