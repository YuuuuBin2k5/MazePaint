# main.py
import pygame
import copy
from config import *
from ui import *
from spaceship import update_star_particles, draw_star_particles
from func_game import *
from BFS import bfs_solve
from DFS import dfs_solve
from UCS import ucs_solve
from Greedy import greedy_solve
from Astar import astar_solve
from maps import *

# --- KHỞI TẠO PYGAME VÀ CÁC THÀNH PHẦN ---
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
font_large = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 28)
clock = pygame.time.Clock()

# --- KHAI BÁO BIẾN TRẠNG THÁI ---~
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

# Smooth movement variables
player_visual_pos = [1, 1]  # Vị trí hiển thị (có thể ở giữa các ô)
player_target_pos = [1, 1]  # Vị trí đích
is_moving_smooth = False    # Có đang di chuyển mượt không
movement_progress = 0.0     # Tiến độ di chuyển (0.0 -> 1.0)
current_auto_direction = None  # Hướng di chuyển khi auto solve
last_auto_direction = None  # Lưu direction cuối cùng để dùng khi smooth movement
SMOOTH_MOVE_SPEED = 1.0    # Giảm tốc độ từ 8.0 xuống 6.0 để mượt mà hơn

time_since_last_move = 0
time_since_last_player_move = 0  # Thêm cooldown cho player
SOLVER_MOVE_INTERVAL = 100
PLAYER_MOVE_INTERVAL = 180  # Tăng lên 180ms để có thời gian cho smooth movement

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
    
    # Update star particles
    update_star_particles(dt)
    
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()  # Lấy trạng thái phím bấm

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
                    player_visual_pos = [1, 1]
                    player_target_pos = [1, 1]
                    is_moving_smooth = False
                    movement_progress = 0.0
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
                        player_visual_pos = [1, 1]
                        player_target_pos = [1, 1]
                        is_moving_smooth = False
                        movement_progress = 0.0
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
                    player_visual_pos = [1, 1]
                    player_target_pos = [1, 1]
                    is_moving_smooth = False
                    movement_progress = 0.0
                    current_auto_direction = None
                    last_auto_direction = None
                    painted_tiles = [[False for _ in range(maze_cols)] for _ in range(maze_rows)]
                    painted_tiles[player_pos[0]][player_pos[1]] = True
                    board_before_player_moves = None
                    game_won = False
                    solving_path = None
                    move_count = 0

                # NÚT HISTORY
                elif history_rect.collidepoint(event.pos):
                    history_list.clear()

       
    # Xử lý di chuyển bằng bàn phím - chỉ khi không auto solve
    if not game_won and not solving_path:
        # Xử lý input chỉ khi không đang di chuyển mượt
        if not is_moving_smooth:
            # Cập nhật thời gian di chuyển
            time_since_last_player_move += dt
            
            # Kiểm tra phím liên tục cho di chuyển mượt mà
            if time_since_last_player_move >= PLAYER_MOVE_INTERVAL:
                # Kiểm tra phím di chuyển - chuyển thành uppercase cho move_player
                move_direction = None
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    move_direction = "UP"
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    move_direction = "DOWN" 
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    move_direction = "LEFT"
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    move_direction = "RIGHT"
                
                # Di chuyển nếu có hướng
                if move_direction:
                    # Tối ưu: chỉ backup board khi thực sự cần
                    if board_before_player_moves is None:
                        board_before_player_moves = (copy.deepcopy(player_pos), [row[:] for row in painted_tiles])
                    
                    old_pos = player_pos[:]  # Lưu vị trí cũ để check thay đổi
                    new_pos, painted_tiles = move_player(player_pos, MAZE_ROWS, MAZE_COLS, move_direction, current_maze, painted_tiles)
                    
                    # Nếu position thay đổi, bắt đầu smooth movement
                    if old_pos != new_pos:
                        player_target_pos = new_pos[:]
                        is_moving_smooth = True
                        movement_progress = 0.0
                        game_won = check_win_condition(current_maze, painted_tiles)
                        
                    time_since_last_player_move = 0  # Reset cooldown
                    move_count += 1
                
     # Xử lý smooth movement - áp dụng cho cả manual và auto solve
    if is_moving_smooth:
        # Tính toán vị trí hiển thị theo interpolation
        start_row, start_col = player_pos
        target_row, target_col = player_target_pos
        
        # Lerp (Linear interpolation) giữa vị trí hiện tại và đích
        player_visual_pos[0] = start_row + (target_row - start_row) * movement_progress
        player_visual_pos[1] = start_col + (target_col - start_col) * movement_progress
        
        # Cập nhật progress
        movement_progress += SMOOTH_MOVE_SPEED / TILE_SIZE
        
        # Hoàn thành di chuyển
        if movement_progress >= 1.0:
            movement_progress = 0.0
            is_moving_smooth = False
            player_pos = player_target_pos[:]
            player_visual_pos = player_target_pos[:]
            # Reset direction nếu không còn path để đi
            if not solving_path:
                current_auto_direction = None
                last_auto_direction = None

    # Tự động giải - chỉ khi không đang smooth movement
    if solving_path and not is_moving_smooth:
        time_since_last_move += dt
        if time_since_last_move > SOLVER_MOVE_INTERVAL:
            time_since_last_move = 0
            if solving_path:
                next_move = solving_path.pop(0)
                old_pos = player_pos[:]  # Lưu vị trí cũ
                new_pos, painted_tiles = move_player(player_pos, MAZE_ROWS, MAZE_COLS, next_move, current_maze, painted_tiles)
                
                # Lưu direction cho phi thuyền
                current_auto_direction = next_move
                last_auto_direction = next_move  # Backup direction
                
                # Nếu position thay đổi, bắt đầu smooth movement cho auto solve
                if old_pos != new_pos:
                    # Đặt player_visual_pos tại vị trí hiện tại (old_pos)
                    player_visual_pos = old_pos[:]
                    # Đặt target là vị trí mới
                    player_target_pos = new_pos[:]
                    # Cập nhật player_pos logic
                    player_pos = old_pos[:]  # Giữ player_pos tại vị trí cũ để interpolate
                    # Bắt đầu smooth movement
                    is_moving_smooth = True
                    movement_progress = 0.0
                move_count += 1
                
                if not solving_path:
                    game_won = check_win_condition(current_maze, painted_tiles)
                    # Chỉ reset direction khi không còn smooth movement
                    if not is_moving_smooth:
                        current_auto_direction = None  # Reset direction khi hoàn thành
                        last_auto_direction = None     # Reset backup direction

    # --- VẼ LÊN MÀN HÌNH ---
    screen.fill(BLACK)
    
    # --- Vẽ background sau khi fill màn hình ---
    draw_stars(screen)
    # Hệ thống planet wave mới - có trật tự và không trùng lặp
    update_planet_system()
    draw_planets(screen)
    # Sử dụng direction phù hợp: ưu tiên current, fallback sang last khi đang auto solve hoặc smooth movement
    auto_dir_to_use = current_auto_direction if current_auto_direction else (last_auto_direction if (solving_path or is_moving_smooth) else None)
    # if auto_dir_to_use:
    #     print(f"📡 Truyền direction vào draw_board: '{auto_dir_to_use}'")
    draw_board(screen, current_maze, painted_tiles, player_visual_pos, BOARD_X, BOARD_Y, keys, player_pos, auto_dir_to_use)

    # Draw star particles on top of everything
    draw_star_particles(screen)

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