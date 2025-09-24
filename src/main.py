# main.py
import pygame
import copy
from config import *
from Ui.ui import *
from Ui.spaceship import update_star_particles, draw_star_particles, ease_in_out_quart
from func_game import *
from Algorithm.BFS import bfs_solve
from Algorithm.DFS import dfs_solve
from Algorithm.UCS import ucs_solve
from Algorithm.Greedy import greedy_solve
from Algorithm.Astar import astar_solve
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

# Smooth movement variables
player_visual_pos = [1, 1]  # Vị trí hiển thị (có thể ở giữa các ô)
player_target_pos = [1, 1]  # Vị trí đích
is_moving_smooth = False    # Có đang di chuyển mượt không
movement_progress = 0.0     # Tiến độ di chuyển (0.0 -> 1.0)
current_auto_direction = None  # Hướng di chuyển khi auto solve
last_auto_direction = None  # Lưu direction cuối cùng để dùng khi smooth movement

time_since_last_move = 0
time_since_last_player_move = 0  # Thêm cooldown cho player

# --- KHAI BÁO RECT CHO CÁC BUTTON ---
map_rect = pygame.Rect(BUTTON_X, MAP_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
player_rect = pygame.Rect(BUTTON_X, PLAYER_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
solver_rect = pygame.Rect(BUTTON_X, SOLVER_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
restart_rect = pygame.Rect(BUTTON_X, RESTART_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
history_rect = pygame.Rect(BUTTON_X, HISTORY_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

# Speed control buttons
speed_decrease_rect = pygame.Rect(SPEED_DECREASE_X, SPEED_BUTTONS_Y, SPEED_BUTTON_WIDTH, SPEED_BUTTON_HEIGHT)
speed_increase_rect = pygame.Rect(SPEED_INCREASE_X, SPEED_BUTTONS_Y, SPEED_BUTTON_WIDTH, SPEED_BUTTON_HEIGHT)
speed_display_rect = pygame.Rect(SPEED_DISPLAY_X, SPEED_BUTTONS_Y, SPEED_DISPLAY_WIDTH, SPEED_BUTTON_HEIGHT)

# Frame counter cho hiệu ứng
frame = 0
victory_frame = 0  # Frame counter riêng cho victory animation

# --- VÒNG LẶP CHÍNH ---
running = True
while running:
    dt = clock.tick(FPS)
    frame += 1  # Tăng frame counter
    
    # Tăng victory frame counter nếu đang chiến thắng
    if game_won:
        victory_frame += 1
    
    # Update star particles
    update_star_particles(dt)
    
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()  # Lấy trạng thái phím bấm

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Xử lý nhấp chuột để chơi lại khi thắng game
        if game_won and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Reset game về trạng thái ban đầu
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
            victory_frame = 0  # Reset victory frame counter
        
        if not solving_path and not game_won:
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
                    victory_frame = 0  # Reset victory frame counter

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
                        victory_frame = 0  # Reset victory frame counter
                        
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
                    victory_frame = 0  # Reset victory frame counter

                # NÚT HISTORY
                elif history_rect.collidepoint(event.pos):
                    history_list.clear()

        # Speed control buttons - có thể dùng mọi lúc, kể cả khi đang auto solve
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # NÚT GIẢM TỐC ĐỘ AUTO SOLVE
            if speed_decrease_rect.collidepoint(event.pos):
                SOLVER_MOVE_INTERVAL = min(SOLVER_MOVE_INTERVAL + 100, 4000)  # Tăng interval = chậm hơn, max 4000ms (0.2x)

            # NÚT TĂNG TỐC ĐỘ AUTO SOLVE
            elif speed_increase_rect.collidepoint(event.pos):
                SOLVER_MOVE_INTERVAL = max(SOLVER_MOVE_INTERVAL - 100, 100)   # Giảm interval = nhanh hơn, min 100ms (8x)

       
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
                    
                    # Chỉ tính toán vị trí mới mà không tô màu ngay
                    row, col = player_pos[0], player_pos[1]
                    dr, dc = 0, 0
                    if move_direction == "UP": dr = -1
                    elif move_direction == "DOWN": dr = 1
                    elif move_direction == "LEFT": dc = -1
                    elif move_direction == "RIGHT": dc = 1
                    
                    # Tính toán vị trí mới mà không tô màu
                    while (0 <= row + dr < maze_rows and 0 <= col + dc < maze_cols and 
                           current_maze[row + dr][col + dc] == PATH):
                        row += dr
                        col += dc
                    
                    new_pos = [row, col]
                    
                    # Nếu position thay đổi, bắt đầu smooth movement
                    if old_pos != new_pos:
                        player_target_pos = new_pos[:]
                        is_moving_smooth = True
                        movement_progress = 0.0
                        
                    time_since_last_player_move = 0  # Reset cooldown
                    move_count += 1
                
     # Xử lý smooth movement - áp dụng cho cả manual và auto solve
    if is_moving_smooth:
        # Tính toán vị trí hiển thị theo interpolation với easing
        start_row, start_col = player_pos
        target_row, target_col = player_target_pos

        # Cập nhật progress - tự động điều chỉnh tốc độ khi auto solve
        if solving_path:
            # Auto solve: điều chỉnh tốc độ smooth movement theo SOLVER_MOVE_INTERVAL
            # Đảm bảo smooth movement hoàn thành trong khoảng thời gian SOLVER_MOVE_INTERVAL
            target_smooth_duration = SOLVER_MOVE_INTERVAL * 0.8  # 80% của interval để có buffer
            required_speed = (TILE_SIZE / target_smooth_duration) * (1000 / 60)  # Tính tốc độ cần thiết
            movement_progress += max(required_speed, SMOOTH_MOVE_SPEED) / TILE_SIZE
        else:
            # Manual: dùng tốc độ cố định
            movement_progress += SMOOTH_MOVE_SPEED / TILE_SIZE
        
        # Áp dụng easing function để có chuyển động mượt mà hơn
        if movement_progress <= 1.0:
            # Sử dụng ease_in_out_quart để có chuyển động chậm hơn ở đầu và cuối
            eased_progress = ease_in_out_quart(min(movement_progress, 1)) 
            
            # Tính toán vị trí hiển thị với easing
            player_visual_pos[0] = start_row + (target_row - start_row) * eased_progress
            player_visual_pos[1] = start_col + (target_col - start_col) * eased_progress

        # Tô màu tất cả các ô trên đường đi dựa trên eased progress để đồng bộ với phi thuyền
        # Tạo danh sách các ô từ start đến target
        path_tiles = []
        current_r, current_c = start_row, start_col
        dr = 1 if target_row > start_row else (-1 if target_row < start_row else 0)
        dc = 1 if target_col > start_col else (-1 if target_col < start_col else 0)
        
        # Thu thập tất cả ô trên đường đi
        while current_r != target_row or current_c != target_col:
            path_tiles.append((current_r, current_c))
            if current_r != target_row:
                current_r += dr
            if current_c != target_col:
                current_c += dc
        path_tiles.append((target_row, target_col))  # Thêm ô đích
        
        # Tô màu dần theo eased progress để đồng bộ với chuyển động phi thuyền
        if len(path_tiles) > 0:
            # Sử dụng eased_progress thay vì movement_progress để đồng bộ
            progress_to_use = ease_in_out_quart(min(movement_progress, 1.0)) if movement_progress <= 1.0 else 1.0
            tiles_to_paint = int(progress_to_use * len(path_tiles))
            for i in range(min(tiles_to_paint + 1, len(path_tiles))):  # +1 để luôn tô ít nhất 1 ô
                tile_row, tile_col = path_tiles[i]
                if (0 <= tile_row < maze_rows and 0 <= tile_col < maze_cols and 
                    current_maze[tile_row][tile_col] == PATH):
                    painted_tiles[tile_row][tile_col] = True
        
        # Hoàn thành di chuyển
        if movement_progress >= 1.0:
            movement_progress = 0.0
            is_moving_smooth = False
            player_pos = player_target_pos[:]
            player_visual_pos = player_target_pos[:]
            
            # Đảm bảo ô cuối được tô màu
            if (0 <= player_pos[0] < maze_rows and 
                0 <= player_pos[1] < maze_cols and 
                current_maze[player_pos[0]][player_pos[1]] == PATH):
                painted_tiles[player_pos[0]][player_pos[1]] = True
            
            # Kiểm tra win condition sau khi hoàn thành di chuyển
            prev_game_won = game_won  # Lưu trạng thái cũ
            game_won = check_win_condition(current_maze, painted_tiles)
            
            # Reset victory frame counter khi vừa chiến thắng
            if game_won and not prev_game_won:
                victory_frame = 0
            
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
                
                # Chỉ tính toán vị trí mới mà không tô màu ngay (giống manual control)
                row, col = player_pos[0], player_pos[1]
                dr, dc = 0, 0
                if next_move == "UP": dr = -1
                elif next_move == "DOWN": dr = 1
                elif next_move == "LEFT": dc = -1
                elif next_move == "RIGHT": dc = 1
                
                # Tính toán vị trí mới mà không tô màu
                while (0 <= row + dr < maze_rows and 0 <= col + dc < maze_cols and 
                       current_maze[row + dr][col + dc] == PATH):
                    row += dr
                    col += dc
                
                new_pos = [row, col]
                
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
                
                # Chỉ kiểm tra win khi không còn solving_path và không đang smooth movement
                if not solving_path and not is_moving_smooth:
                    # Chỉ reset direction khi không còn smooth movement
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
    draw_board(screen, current_maze, painted_tiles, player_visual_pos, BOARD_X, BOARD_Y, keys, player_pos, auto_dir_to_use)

    # Draw star particles on top of everything
    draw_star_particles(screen)

    # UI Buttons with 3D cosmic style
    draw_button(screen, font_small, map_rect, DARK_BLUE, f"MAP: {map_names[current_map_index]}", "info")
    draw_button(screen, font_small, player_rect, DARK_BLUE, algorithm, "info") 
    draw_button(screen, font_small, solver_rect, DARK_BLUE, "SOLVE", "primary")
    draw_button(screen, font_small, restart_rect, DARK_BLUE, "RESTART", "success")
    draw_button(screen, font_small, history_rect, DARK_BLUE, "CLEAR HISTORY", "info")

    # Speed control buttons with warning style  
    draw_button(screen, font_small, speed_decrease_rect, DARK_BLUE, "-", "warning")
    draw_button(screen, font_small, speed_increase_rect, DARK_BLUE, "+", "warning")
    draw_button(screen, font_small, restart_rect, DARK_BLUE, "RESTART")
    draw_button(screen, font_small, history_rect, DARK_BLUE, "HISTORY")

    # Speed control UI
    draw_button(screen, font_small, speed_decrease_rect, DARK_BLUE, "-")
    draw_button(screen, font_small, speed_increase_rect, DARK_BLUE, "+")
    
    # Speed display - tính dựa trên BASE_SOLVER_INTERVAL
    speed_multiplier = BASE_SOLVER_INTERVAL / SOLVER_MOVE_INTERVAL
    speed_text = f"Speed: {speed_multiplier:.1f}x"  # Hiển thị tốc độ với 1 chữ số thập phân
    pygame.draw.rect(screen, DARK_BLUE, speed_display_rect)
    pygame.draw.rect(screen, WHITE, speed_display_rect, 2)
    text_surface = font_small.render(speed_text, True, WHITE)
    text_rect = text_surface.get_rect(center=speed_display_rect.center)
    screen.blit(text_surface, text_rect)

    draw_move_count(screen, MOVE_COUNT_X, MOVE_COUNT_Y, font_small, move_count)
    
    if game_won:
        draw_cosmic_victory(screen, WINDOW_WIDTH, WINDOW_HEIGHT, victory_frame)

    pygame.display.flip()
    
pygame.quit()