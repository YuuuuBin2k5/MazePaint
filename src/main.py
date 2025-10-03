# -*- coding: utf-8 -*-
# main.py
import pygame
import copy
import time
import threading
from pathlib import Path
from config import *
from Ui.renderer import *
from Ui.player.spaceship import update_star_particles, draw_star_particles, ease_in_out_quart, reload_spaceship
from core.func_game import *
from data.algorithm.func_algorithm import find_connected_components
from data.maps import *
import math
from Ui.widgets.cosmic_selector import CosmicAlgorithmSelector
from manager.sound_manager import sound_manager
from core.game_manager import GameManager
from Ui.animations.intro import get_intro_animation, reset_intro
from Ui.custom_titlebar import draw_modern_titlebar
from manager.font_manager import font_edit_panel, font_large, font_small

# --- KHỞI TẠO PYGAME VÀ CÁC THÀNH PHẦN ---
pygame.init()

# Tạo borderless window (không có title bar của Windows)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption(WINDOW_TITLE)
pygame.display.set_icon(pygame.image.load(ICON_PATH))


# Global fonts and colors for UI
fonts = {
    'title': font_large,
    'state': font_large,
    'btn': font_small,
    'label': font_small
}

colors = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'bg': (40, 50, 70),
    'border': (120, 150, 200),
    'title': (200, 220, 255),
    'box': (60, 80, 120),
    'wall': (100, 100, 100),
    'path': (50, 50, 50)
}


clock = pygame.time.Clock()

# Khởi tạo game manager
game_manager = GameManager(WINDOW_WIDTH, WINDOW_HEIGHT)

# === THÊM INTRO ===
show_intro = True
intro_animation = get_intro_animation(WINDOW_WIDTH, WINDOW_HEIGHT)

# Khởi tạo cosmic selector
cosmic_selector = CosmicAlgorithmSelector(WINDOW_WIDTH, WINDOW_HEIGHT)
show_algorithm_selector = False
edit_mode = False  # When True, clicking on board toggles wall/path
edit_pending_save = False  # When True, user is in edit mode but hasn't saved yet
# Edit painting state
is_mouse_editing = False
edit_paint_value = None  # either WALL or PATH while dragging
last_edited_cell = (-1, -1)

# --- KHAI BÁO BIẾN TRẠNG THÁI ---
# Speed control system - x1, x5, x10, x20
speed_multipliers = [1, 5, 10, 20]
current_speed_index = 0  # Bắt đầu với x1
SOLVER_MOVE_INTERVAL = BASE_SOLVER_INTERVAL // speed_multipliers[current_speed_index]

all_maps = {"0": MAP_ZERO, "1": MAP_ONE, "2": MAP_TWO, 
            "3": MAP_THREE, "4": MAP_FOUR,
            "5": MAP_FIVE, "6": MAP_SIX,
            "7": MAP_SEVEN}
map_names = list(all_maps.keys())
current_map_index = 0
current_maze = all_maps[map_names[current_map_index]]

maze_rows = len(current_maze)
maze_cols = len(current_maze[0])

algorithm = "Player"
move_count = 0
level_start_time = None

# Victory information tracking  
last_victory_info = {
    "algorithm": "Player",
    "steps": 0,
    "execution_time": None
}

# KHỞI TẠO GAME LẦN ĐẦU
player_pos = [1, 1]
painted_tiles = [[False for _ in range(maze_cols)] for _ in range(maze_rows)]
painted_tiles[player_pos[0]][player_pos[1]] = True
board_before_player_moves = None
game_won = False
solving_path = None
history_list = []
history_groups = {}  # Nhóm lịch sử theo maze state
show_history_panel = False  # Trạng thái hiển thị panel
history_scroll_offset = 0  # Scroll offset cho panel

# Smooth movement variables
player_visual_pos = [1, 1]  # Vị trí hiển thị (có thể ở giữa các ô)
player_target_pos = [1, 1]  # Vị trí đích
is_moving_smooth = False    # Có đang di chuyển mượt không
movement_progress = 0.0     # Tiến độ di chuyển (0.0 -> 1.0)
current_auto_direction = None  # Hướng di chuyển khi auto solve
last_auto_direction = None  # Lưu direction cuối cùng để dùng khi smooth movement

is_moving_smooth = False    # Có đang di chuyển mượt không
movement_progress = 0.0     # Tiến độ di chuyển (0.0 -> 1.0)
current_auto_direction = None  # Hướng di chuyển khi auto solve
last_auto_direction = None  # Lưu direction cuối cùng để dùng khi smooth movement

# Smart Input Queue System - now imported from movement_queue.py
time_since_last_move = 0
time_since_last_player_move = 0  # Thêm cooldown cho player

# --- KHAI BÁO RECT CHO CÁC BUTTON ---
map_rect = pygame.Rect(BUTTON_X, MAP_BUTTON_Y, BUTTON_WIDTH - 70, BUTTON_HEIGHT)
# Edit button width (computed dynamically to avoid going off-window)
EDIT_BUTTON_WIDTH = 80
edit_rect = pygame.Rect(BUTTON_X + BUTTON_WIDTH - 70, MAP_BUTTON_Y, EDIT_BUTTON_WIDTH, BUTTON_HEIGHT)

# --- KHỞI TẠO HỆ THỐNG ÂM THANH ---
# Start background music
sound_manager.play_music()
player_rect = pygame.Rect(BUTTON_X, PLAYER_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
solver_rect = pygame.Rect(BUTTON_X, SOLVER_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
restart_rect = pygame.Rect(BUTTON_X, RESTART_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
history_rect = pygame.Rect(BUTTON_X, HISTORY_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

# Rect for in-game Menu button (will be set when drawing)
menu_button_rect = None

# Header close button rect (will be set when drawing header)
header_close_button_rect = None

# Speed control buttons
speed_decrease_rect = pygame.Rect(SPEED_DECREASE_X, SPEED_BUTTONS_Y, SPEED_BUTTON_WIDTH, SPEED_BUTTON_HEIGHT)
speed_increase_rect = pygame.Rect(SPEED_INCREASE_X, SPEED_BUTTONS_Y, SPEED_BUTTON_WIDTH, SPEED_BUTTON_HEIGHT)
speed_display_rect = pygame.Rect(SPEED_DISPLAY_X, SPEED_BUTTONS_Y, SPEED_DISPLAY_WIDTH, SPEED_BUTTON_HEIGHT)

# Frame counter cho hiệu ứng
frame = 0
victory_frame = 0  # Frame counter riêng cho victory animation
victory_phase3_sound_played = False  # Flag để đảm bảo âm thanh phase 3 chỉ phát 1 lần

# THÊM: Biến trạng thái cho algorithm solving
is_solving_algorithm = False  # Đang chạy thuật toán trên thread
solving_result_ready = False  # Kết quả đã sẵn sàng
solving_start_time = 0        # Thời điểm bắt đầu solving
solving_result = None         # Lưu kết quả solving


# --- PREVIEW EXPLORED (HIỂN THỊ VÀNG) ---
preview_tiles = []            
preview_painted = set()       
preview_running = False
pending_solving_path = None   
PREVIEW_TILE_INTERVAL = 0.03  
time_since_last_preview = 0.0

# THÊM: Hằng số cho công thức tính tốc độ preview
PREVIEW_BASE_TIME = 15.0  # Thời gian base (giây) ở x1
PREVIEW_SCALE_FACTOR = 0.8  # Hệ số scale cho sqrt
PREVIEW_MIN_TIME = 12.0  # Thời gian tối thiểu
PREVIEW_MAX_TIME = 30.0  # Thời gian tối đa

# THÊM: Preview theo nhóm component
preview_groups = []           
current_preview_group = 0     
PREVIEW_GROUP_INTERVAL = 0.2  

# Surface preview tái sử dụng (tránh tạo mỗi frame)
# tạo surface sau khi TILE_SIZE đã có giá trị
preview_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
preview_surf.fill((0, 255, 0, 150))  # màu vàng bán trong suốt

# --- new: runtime preview control ---
# thực tế sẽ gán preview_tile_interval_run khi bắt đầu preview
preview_tile_interval_run = PREVIEW_TILE_INTERVAL
preview_elapsed_total = 0.0  # tổng thời gian preview đã chạy (s)

# --- VÒNG LẶP CHÍNH ---
running = True
while running:
    dt = clock.tick(FPS)
    frame += 1
    
    # === UPDATE INTRO (thêm trước game_manager.update()) ===
    if show_intro:
        intro_animation.update()
        if intro_animation.is_finished():
            show_intro = False
            reset_intro()
            sound_manager.play_button_sound()
    
    # Cập nhật game manager (CHỈ KHI KHÔNG PHẢI INTRO)
    if not show_intro:
        game_manager.update()
    
    # Precompute in-game Menu button rect so event handling (which happens next) can use it
    if game_manager.is_in_game():
        try:
            # Match the placement used in MainMenu.draw_menu_button: top-right with margins
            margin_x = 20
            margin_y = 65  # 20 + HEADER_HEIGHT - adjusted for header
            button_width = 120
            button_height = 40
            menu_button_rect = pygame.Rect(game_manager.width - margin_x - button_width, margin_y, button_width, button_height)
        except Exception:
            menu_button_rect = None
    else:
        menu_button_rect = None
    
    # === XỬ LÝ EVENTS ===
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
        # === HANDLE INTRO SKIP (thêm trước các event khác) ===
        if show_intro:
            if event.type == pygame.MOUSEBUTTONDOWN or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                if not intro_animation.transitioning:
                    intro_animation.start_transition()
                    sound_manager.play_button_sound()
            continue  # BỎ QUA tất cả event khác khi đang intro
        
        # === XỬ LÝ NÚT X ĐÓNG ỨNG DỤNG (ƯU TIÊN CAO NHẤT) ===
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if header_close_button_rect and header_close_button_rect.collidepoint(mouse_pos):
                running = False  # Đóng ứng dụng
                sound_manager.play_button_sound()
                break
        
        # Xử lý events theo trạng thái hiện tại (CHỈ KHI KHÔNG PHẢI INTRO)
        if game_manager.is_in_menu() or game_manager.is_in_spaceship_select():
            # Menu events hoặc spaceship selector events
            result = game_manager.handle_event(event)
            
            if result == "EXIT_GAME":
                running = False
                break
            elif result == "START_GAME":
                # Bắt đầu game - reset trạng thái
                state = reset_game(current_map_index, all_maps)
                apply_state(state)
                sound_manager.play_button_sound()
            elif result == "SHIP_SELECTED":
                sound_manager.play_button_sound()
                # Reload spaceship với phi thuyền mới được chọn
                reload_spaceship()
        
        elif game_manager.is_in_game():
            # === XỬ LÝ VICTORY SCREEN EVENTS ===
            if game_won:
                # Xử lý input trong victory screen
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        # Tiếp tục chơi level tiếp theo
                        current_map_index = (current_map_index + 1) % len(all_maps)
                        state = reset_game(current_map_index, all_maps)
                        apply_state(state)
                        sound_manager.play_button_sound()
                    elif event.key == pygame.K_r:
                        # Chơi lại level hiện tại
                        state = reset_game(current_map_index, all_maps)
                        apply_state(state)
                        sound_manager.play_button_sound()
                    elif event.key == pygame.K_ESCAPE:
                        # Quay về menu
                        result = game_manager.handle_event(event)
                        if result == "BACK_TO_MENU":
                            sound_manager.play_button_sound()
                            continue
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Click bất kỳ để tiếp tục level tiếp theo
                    current_map_index = (current_map_index + 1) % len(all_maps)
                    state = reset_game(current_map_index, all_maps)
                    apply_state(state)
                    sound_manager.play_button_sound()
                continue  # Bỏ qua các xử lý khác khi đang trong victory screen
            
            # Game events (chỉ khi không phải victory screen)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Quay về menu
                result = game_manager.handle_event(event)
                if result == "BACK_TO_MENU":
                    sound_manager.play_button_sound()
                    continue
            
            # === XỬ LÝ MOUSE CLICK CHO UI BUTTONS ===
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = event.pos
                handled = False  # flag to prevent clicks falling through to other UI

                # Auto-save nếu đang pending save (trừ khi click edit button)
                if edit_pending_save and not edit_rect.collidepoint(mouse_pos):
                    save_and_exit_edit_mode()

                # Map button click
                if map_rect.collidepoint(mouse_pos) and not show_history_panel:
                    current_map_index = (current_map_index + 1) % len(all_maps)
                    state = reset_game(current_map_index, all_maps)
                    apply_state(state)
                    sound_manager.play_button_sound()
                    handled = True

                # Edit button click
                elif edit_rect.collidepoint(mouse_pos) and not show_history_panel:
                    if not edit_mode:
                        # Chuyển vào edit mode
                        edit_mode = True
                        edit_pending_save = False  # Chưa có thay đổi nào
                        sound_manager.play_button_sound()
                    elif edit_pending_save:
                        # Đang ở edit mode và pending save -> nhấn SAVE
                        success = save_current_map_to_file(current_map_index, current_maze)
                        if success:
                            all_maps[map_names[current_map_index]] = copy.deepcopy(current_maze)
                            edit_pending_save = False  # Đã save, không còn pending
                            sound_manager.play_button_sound()
                    else:
                        # Đang ở edit mode nhưng đã save -> thoát edit mode
                        edit_mode = False
                        edit_pending_save = False
                        sound_manager.play_button_sound()
                    handled = True

                # Algorithm/Player button click
                elif player_rect.collidepoint(mouse_pos) and not show_history_panel:
                    show_algorithm_selector = True
                    sound_manager.play_button_sound()
                    handled = True

                # Solve button click
                elif solver_rect.collidepoint(mouse_pos) and not solving_path and not game_won and not preview_running and not is_solving_algorithm and not show_history_panel and algorithm != "Player":
                    # Bắt đầu solving trong background
                    is_solving_algorithm = True
                    solving_result_ready = False
                    solving_start_time = time.time()
                    solving_result = None
                    
                    # Tạo thread để chạy solving
                    solve_thread = threading.Thread(
                        target=solve_in_background, 
                        args=(algorithm, current_maze, player_pos, history_groups)
                    )
                    solve_thread.daemon = True  # Thread sẽ kết thúc khi main program kết thúc
                    solve_thread.start()
                    
                    sound_manager.play_button_sound()
                    handled = True

                # Restart button click
                elif restart_rect.collidepoint(mouse_pos) and not show_history_panel:
                    state = reset_game(current_map_index, all_maps)
                    apply_state(state)
                    sound_manager.play_button_sound()
                    handled = True

                # History toggle button click (open/close)
                elif history_rect.collidepoint(mouse_pos):
                    show_history_panel = not show_history_panel
                    sound_manager.play_button_sound()
                    handled = True

                # Speed decrease button
                elif speed_decrease_rect.collidepoint(mouse_pos) and not show_history_panel:
                    if current_speed_index > 0:
                        current_speed_index -= 1
                        SOLVER_MOVE_INTERVAL = BASE_SOLVER_INTERVAL // speed_multipliers[current_speed_index]
                        
                        if preview_running and len(preview_groups) > 0:
                            num_groups = len(preview_groups)
                            current_multiplier = speed_multipliers[current_speed_index]
                            
                            # Dùng hằng số global
                            base_preview_time = PREVIEW_BASE_TIME + PREVIEW_SCALE_FACTOR * math.sqrt(num_groups)
                            base_preview_time = max(PREVIEW_MIN_TIME, min(base_preview_time, PREVIEW_MAX_TIME))
                            
                            adjusted_preview_time = base_preview_time / current_multiplier
                            preview_tile_interval_run = adjusted_preview_time / num_groups
                        
                        sound_manager.play_button_sound()
                    handled = True

                # Speed increase button
                elif speed_increase_rect.collidepoint(mouse_pos) and not show_history_panel:
                    if current_speed_index < len(speed_multipliers) - 1:
                        current_speed_index += 1
                        SOLVER_MOVE_INTERVAL = BASE_SOLVER_INTERVAL // speed_multipliers[current_speed_index]
                        
                        if preview_running and len(preview_groups) > 0:
                            num_groups = len(preview_groups)
                            current_multiplier = speed_multipliers[current_speed_index]
                            
                            # Dùng hằng số global
                            base_preview_time = PREVIEW_BASE_TIME + PREVIEW_SCALE_FACTOR * math.sqrt(num_groups)
                            base_preview_time = max(PREVIEW_MIN_TIME, min(base_preview_time, PREVIEW_MAX_TIME))
                            
                            adjusted_preview_time = base_preview_time / current_multiplier
                            preview_tile_interval_run = adjusted_preview_time / num_groups
                        
                        sound_manager.play_button_sound()
                    handled = True

                # If history panel is open, handle its interactive clicks (close / clear)
                if show_history_panel and not handled:
                    panel_rect = pygame.Rect(70, 65, 1000, 580)  # 20 + HEADER_HEIGHT - Adjusted for header
                    close_rect = pygame.Rect(panel_rect.right - 40, panel_rect.top + 10, 30, 30)
            

                    # Close button click
                    if close_rect.collidepoint(mouse_pos):
                        show_history_panel = False
                        sound_manager.play_button_sound()
                        handled = True
                    # Clear history button (use same rect logic or another UI element)
                    elif history_rect.collidepoint(mouse_pos):
                        history_groups.clear()
                        sound_manager.play_button_sound()
                        handled = True

                # In-game Menu button (when in GAME state) - only if not already handled
                if not handled and game_manager.is_in_game() and menu_button_rect and menu_button_rect.collidepoint(mouse_pos) and not show_history_panel:
                    fake_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
                    result = game_manager.handle_event(fake_event)
                    if result == "BACK_TO_MENU":
                        sound_manager.play_button_sound()
                    handled = True

                # If we already handled this click, skip further processing for this event
                if handled:
                    continue

            # Handle clicks on the board when in edit mode
            # Handle mouse down to start edit/paint
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and edit_mode and not show_history_panel:
                mx, my = event.pos
                bx = mx - BOARD_X
                by = my - BOARD_Y
                if 0 <= bx < MAZE_COLS * TILE_SIZE and 0 <= by < MAZE_ROWS * TILE_SIZE:
                    col = bx // TILE_SIZE
                    row = by // TILE_SIZE
                    if 0 <= row < maze_rows and 0 <= col < maze_cols:
                        # Determine paint value based on current cell: we will set all dragged cells to this value
                        desired = WALL if current_maze[row][col] == PATH else PATH
                        edit_paint_value = desired
                        is_mouse_editing = True
                        last_edited_cell = (row, col)
                        # Apply once to this cell
                        if current_maze[row][col] != edit_paint_value:
                            current_maze[row][col] = edit_paint_value
                            painted_tiles[row][col] = False
                            sound_manager.play_button_sound()
                            save_current_map_to_file(current_map_index, current_maze)
                            edit_pending_save = True

            # Support dragging edits: while left mouse button is held, set cells to edit_paint_value
            if event.type == pygame.MOUSEMOTION and edit_mode and pygame.mouse.get_pressed()[0] and is_mouse_editing and not show_history_panel:
                mx, my = event.pos
                bx = mx - BOARD_X
                by = my - BOARD_Y
                if 0 <= bx < MAZE_COLS * TILE_SIZE and 0 <= by < MAZE_ROWS * TILE_SIZE:
                    col = bx // TILE_SIZE
                    row = by // TILE_SIZE
                    if 0 <= row < maze_rows and 0 <= col < maze_cols:
                        if (row, col) != last_edited_cell:
                            # Only change if different from desired value
                            if current_maze[row][col] != edit_paint_value:
                                current_maze[row][col] = edit_paint_value
                                painted_tiles[row][col] = False
                                sound_manager.play_button_sound()
                                save_current_map_to_file(current_map_index, current_maze)
                                edit_pending_save = True
                            last_edited_cell = (row, col)

            # End painting when mouse button is released
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and is_mouse_editing:
                is_mouse_editing = False
                edit_paint_value = None
                last_edited_cell = (-1, -1)
            
            # History panel scroll handling
            elif show_history_panel and event.type == pygame.MOUSEWHEEL:
                scroll_speed = 30
                if event.y > 0:  # Scroll up
                    history_scroll_offset = max(0, history_scroll_offset - scroll_speed)
                else:  # Scroll down
                    history_scroll_offset += scroll_speed
            
            # === ALGORITHM SELECTOR (chỉ trong game state) ===
            if show_algorithm_selector:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        show_algorithm_selector = False
                    else:
                        result = cosmic_selector.handle_key_press(event.key)
                        if result:
                            algorithm = result
                            show_algorithm_selector = False  # Đóng selector
                            # Reset cosmic selector state
                            cosmic_selector.show_heuristic_menu = False
                            cosmic_selector.selected_algorithm_for_heuristic = None
                            sound_manager.play_button_sound()
                elif event.type == pygame.MOUSEMOTION:
                    cosmic_selector.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        result = cosmic_selector.handle_mouse_click(event.pos)
                        if result:
                            algorithm = result
                            show_algorithm_selector = False  # Đóng selector
                            # Reset cosmic selector state
                            cosmic_selector.show_heuristic_menu = False
                            cosmic_selector.selected_algorithm_for_heuristic = None
                            sound_manager.play_button_sound()  # Âm thanh chọn thuật toán
    
    # === MAIN GAME LOGIC (CHỈ KHI KHÔNG PHẢI INTRO) ===
    if not show_intro:
        # === XỬ LÝ KẾT QUẢ SOLVING TRONG BACKGROUND ===
        if is_solving_algorithm and solving_result_ready:
            # Reset trạng thái solving ngay lập tức
            is_solving_algorithm = False
            solving_result_ready = False
            
            # Xử lý kết quả an toàn
            if solving_result and isinstance(solving_result, (tuple, list)) and len(solving_result) >= 2:
                try:
                    path_result, history_groups = solving_result
                except:
                    path_result = None
                    print("ERROR - Unable to unpack solving_result")
            else:
                path_result = None
                print("ERROR - solving_result is invalid")
            
            if path_result:
                explored_value = path_result.get('explored')
                
                if explored_value is not None and len(explored_value) > 0:
                    explored_dict = explored_value
                    
                    preview_groups = []
                    for step in sorted(explored_dict.keys()):
                        if explored_dict[step]:
                            group = []
                            for tile in explored_dict[step]:
                                if isinstance(tile, (list, tuple)) and len(tile) >= 2:
                                    group.append((tile[0], tile[1]))
                            if group:
                                preview_groups.append(group)
                    
                    if preview_groups:
                        preview_painted = set()
                        preview_running = True
                        current_preview_group = 0
                        preview_elapsed_total = 0.0
                        time_since_last_preview = 0.0
                        
                        solving_path_data = path_result.get("solving_path") or path_result.get("pending_solving_path")
                        if solving_path_data and len(solving_path_data) > 0:
                            pending_solving_path = solving_path_data[:]         
                        else:
                            pending_solving_path = []
           
                        solving_path = None
                        
                        # CÔNG THỨC MỚI: Sử dụng căn bậc hai cho tốc độ tự nhiên hơn
                        num_groups = len(preview_groups)
                        current_multiplier = speed_multipliers[current_speed_index]
                        
                        # Dùng hằng số global thay vì local variables
                        base_preview_time = PREVIEW_BASE_TIME + PREVIEW_SCALE_FACTOR * math.sqrt(num_groups)
                        
                        # Giới hạn trong khoảng hợp lý
                        base_preview_time = max(PREVIEW_MIN_TIME, min(base_preview_time, PREVIEW_MAX_TIME))
                        
                        # Điều chỉnh theo speed multiplier
                        adjusted_preview_time = base_preview_time / current_multiplier
                        
                        # Tính interval cho mỗi group
                        preview_tile_interval_run = adjusted_preview_time / num_groups if num_groups > 0 else 0.3

                    else:
                        solving_path_data = path_result.get("solving_path") or path_result.get("pending_solving_path")
                        if solving_path_data and len(solving_path_data) > 0:
                            solving_path = solving_path_data[:]
                        else:
                            solving_path = None
                        preview_running = False
                
                # Chỉ check pending_solving_path nếu KHÔNG có explored
                elif path_result.get("pending_solving_path"):
                    solving_path_data = path_result.get("pending_solving_path")
                    if solving_path_data and len(solving_path_data) > 0:
                        solving_path = solving_path_data[:]
                    else:
                        solving_path = None
                    preview_running = False
                
                elif path_result.get("preview_tiles"):
                    # Lấy solving path từ pending_solving_path hoặc solving_path
                    solving_path_data = path_result.get("pending_solving_path") or path_result.get("solving_path")
                    if solving_path_data and len(solving_path_data) > 0:
                        solving_path = solving_path_data[:]
                    else:
                        solving_path = None
                    preview_running = False
                
                elif path_result.get("solving_path"):
                    # Chỉ có solving_path
                    solving_path_data = path_result.get("solving_path")
                    if solving_path_data and len(solving_path_data) > 0:
                        solving_path = solving_path_data[:]
                    else:
                        solving_path = None
                    preview_running = False
                else:
                    print("ERROR - path_result has no usable data!")
                
                sound_manager.play_algorithm_start_sound()
        
        # Tăng victory frame counter nếu đang chiến thắng
        if game_won:
            victory_frame += 1
        
        # Update star particles
        update_star_particles(dt) 
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()  # Lấy trạng thái phím bấm


       
        # === SMART INPUT HANDLING ===
        # Xử lý input và thêm vào queue (luôn luôn, không cần chờ movement complete)
        if not game_won and not show_history_panel:
            current_time = pygame.time.get_ticks()
            
            # Kiểm tra xem có phím di chuyển nào được nhấn không
            movement_key_pressed = (keys[pygame.K_UP] or keys[pygame.K_w] or 
                                  keys[pygame.K_DOWN] or keys[pygame.K_s] or 
                                  keys[pygame.K_LEFT] or keys[pygame.K_a] or 
                                  keys[pygame.K_RIGHT] or keys[pygame.K_d])
            
            # Nếu đang giải thuật toán và có phím di chuyển được nhấn thì bỏ qua
            if solving_path and movement_key_pressed:
                pass  # Không xử lý input khi đang giải thuật toán
            elif not solving_path:  # Chỉ xử lý input khi không đang giải thuật toán
                # Nếu có phím di chuyển được nhấn và algorithm không phải "Player" thì chuyển về Player
                if movement_key_pressed and algorithm != "Player":
                    algorithm = "Player"
                
                # Detect new key presses and add to queue
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    add_movement_to_queue("UP", current_time)
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    add_movement_to_queue("DOWN", current_time)
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    add_movement_to_queue("LEFT", current_time)
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    add_movement_to_queue("RIGHT", current_time)
        
        # === MOVEMENT EXECUTION ===
        # Xử lý di chuyển từ queue - chỉ khi không đang di chuyển
        if not game_won and not solving_path and not is_moving_smooth:
            # Cập nhật thời gian di chuyển
            time_since_last_player_move += dt
            
            # Kiểm tra có thể thực hiện movement tiếp theo
            if time_since_last_player_move >= PLAYER_MOVE_INTERVAL:
                move_direction = get_next_movement()  # Lấy từ queue thay vì check keys
                # Di chuyển nếu có hướng từ queue
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
                    
                    # CHỈ tính move_count khi thực sự di chuyển được ít nhất 1 ô
                    if old_pos != new_pos:
                        player_target_pos = new_pos[:]
                        is_moving_smooth = True
                        movement_progress = 0.0
                        move_count += 1  # Chỉ tăng move_count khi có di chuyển thực sự
                        sound_manager.play_move_sound()  # Âm thanh di chuyển thủ công
                        
                    time_since_last_player_move = 0  # Reset cooldown
                 
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
                victory_phase3_sound_played = False  # Reset flag khi bắt đầu victory
                sound_manager.play_win_sound()  # Âm thanh chiến thắng ngắn
                sound_manager.switch_to_victory_music()  # Chuyển sang nhạc chiến thắng
                
                # Lưu thông tin chiến thắng cho cả Player và Algorithm
                try:
                    if algorithm == "Player":
                        elapsed_ms = 0
                        if level_start_time is not None:
                            elapsed_ms = (time.time() - level_start_time) * 1000
                        
                        # Update victory info
                        last_victory_info["algorithm"] = "Player"
                        last_victory_info["steps"] = move_count
                        last_victory_info["execution_time"] = elapsed_ms
                        
                        add_to_history("Player", {
                            "path": [],
                            "visited": 0,
                            "states": 0,
                            # steps use move_count
                            "steps": move_count
                        }, elapsed_ms)
                    else:
                        # Algorithm đã hoàn thành - lấy thông tin từ history gần nhất
                        current_maze_state = tuple(tuple(row) for row in current_maze)
                        if current_maze_state in history_groups:
                            latest_result = history_groups[current_maze_state]['results'][-1]
                            last_victory_info["algorithm"] = latest_result.get('algorithm', algorithm)
                            last_victory_info["steps"] = latest_result.get('steps', 0)
                            last_victory_info["execution_time"] = latest_result.get('execution_time', 0.0)
                        else:
                            # Fallback nếu không có history
                            last_victory_info["algorithm"] = algorithm
                            last_victory_info["steps"] = len(solving_path) if solving_path else 0
                            last_victory_info["execution_time"] = 0.0
                except Exception:
                    # Don't let history errors break victory flow
                    pass
            
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
                sound_manager.play_algorithm_step_sound()  # Âm thanh từng bước thuật toán
                
                # Chỉ kiểm tra win khi không còn solving_path và không đang smooth movement
                if not solving_path and not is_moving_smooth:
                    # Chỉ reset direction khi không còn smooth movement
                    current_auto_direction = None  # Reset direction khi hoàn thành
                    last_auto_direction = None     # Reset backup direction

    # --- VẼ LÊN MÀN HÌNH ---
    screen.fill(BLACK)
    
    # === DRAW INTRO OR GAME ===
    if show_intro:
        intro_animation.draw(screen)
        header_close_button_rect = None  # No header during intro
    else:
        # === VẼ HEADER BAR CHO TẤT CẢ STATES (KHÔNG PHẢI INTRO) ===
        header_height, close_button_rect = draw_modern_titlebar(screen, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, font_small, frame)
        header_close_button_rect = close_button_rect  # Lưu để xử lý events
        
        # Render theo trạng thái hiện tại
        if game_manager.is_in_menu():
            game_manager.main_menu.draw(screen)
        elif game_manager.is_in_spaceship_select():
            game_manager.draw(screen)
        else:
            # Vẽ game (trạng thái GAME)
            
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

            # --- VẼ PREVIEW VÀNG (explored) nếu có ---
            if preview_painted:
                current_time = time.time()
                try:
                    for (pr, pc) in list(preview_painted):
                        if 0 <= pr < maze_rows and 0 <= pc < maze_cols:
                            # Nếu ô đã được tô (painted_tiles), không vẽ overlay preview vàng
                            # để màu xanh của phi thuyền luôn ưu tiên hiển thị.
                            try:
                                if painted_tiles[pr][pc]:
                                    continue
                            except Exception:
                                # painted_tiles có thể chưa sẵn sàng; trong trường hợp đó vẽ như cũ
                                pass
                            
                            screen_x = BOARD_X + pc * TILE_SIZE
                            screen_y = BOARD_Y + pr * TILE_SIZE
                            
                            # Vẽ preview tile bình thường (không có highlight effects)
                            screen.blit(preview_surf, (screen_x, screen_y))
                except Exception:
                    # fallback: vẽ preview như cũ nếu có lỗi
                    for (pr, pc) in list(preview_painted):
                        if 0 <= pr < maze_rows and 0 <= pc < maze_cols:
                            screen_x = BOARD_X + pc * TILE_SIZE
                            screen_y = BOARD_Y + pr * TILE_SIZE
                            screen.blit(preview_surf, (screen_x, screen_y))

            # UI Buttons with 3D cosmic style - chỉ hiển thị khi ở trạng thái game
            draw_button(screen, font_small, map_rect, DARK_BLUE, f"MAP: {map_names[current_map_index]}", "info")
            # Edit button to the right of map button
            if not edit_mode:
                button_text = "EDIT"
                button_color = (180, 80, 80)
            elif edit_pending_save:
                button_text = "SAVE"
                button_color = (80, 180, 80)  # Green for save
            else:
                button_text = "CLOSE"
                button_color = (80, 80, 180)  # Blue for exit
            
            draw_button(screen, font_small, edit_rect, button_color, button_text, "warning")
            draw_button(screen, font_small, player_rect, DARK_BLUE, algorithm, "info") 
            
            # Solve button - disabled nếu algorithm là Player
            if algorithm == "Player":
                draw_button(screen, font_small, solver_rect, COLOR_WALL, "SOLVE", "disabled")
            else:
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
            
            # Speed display - sử dụng speed_multipliers array
            current_multiplier = speed_multipliers[current_speed_index]
            speed_text = f"x{current_multiplier}"  # Hiển thị đơn giản: x1, x5, x10, x20
            pygame.draw.rect(screen, DARK_BLUE, speed_display_rect)
            pygame.draw.rect(screen, WHITE, speed_display_rect, 2)
            text_surface = font_small.render(speed_text, True, WHITE)
            text_rect = text_surface.get_rect(center=speed_display_rect.center)
            screen.blit(text_surface, text_rect)

            draw_move_count(screen, MOVE_COUNT_X, MOVE_COUNT_Y, font_small, move_count)
            # Draw in-game Menu button and store its rect for click handling
            try:
                menu_button_rect = game_manager.main_menu.draw_menu_button(screen, label="Menu")
            except Exception:
                # If something goes wrong rendering the menu button, ensure it's None
                menu_button_rect = None
            
            # Draw history panel if visible
            if show_history_panel:
                # Panel và close button rects
                panel_rect = pygame.Rect(70, 65, 1000, 580)  # 20 + HEADER_HEIGHT - Adjusted for header
                close_rect = pygame.Rect(panel_rect.right - 40, panel_rect.top + 10, 30, 30)

                # Colors dictionary cho panel
                colors = {
                    'bg': (30, 40, 60, 220),  # Background với alpha
                    'border': (100, 150, 200),
                    'title': WHITE,
                    'white': WHITE,
                    'black': BLACK,
                    'label': (200, 200, 200),
                    'box': (60, 80, 120),
                    'wall': (100, 100, 100),
                    'path': (50, 50, 50)
                }
                
                # Fonts dictionary cho panel
                panel_fonts = {
                    'state': font_large,
                    'btn': font_small,
                    'label': font_small
                }
                
                # Vẽ panel với semi-transparent background
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # Semi-transparent black
                screen.blit(overlay, (0, 0))
                
                # Vẽ history panel
                draw_history_panel(screen, history_groups, history_scroll_offset, panel_rect, close_rect, panel_fonts, colors, None)
            
            if game_won:
                # Kiểm tra và phát âm thanh phase 3 (sau frame 180)
                if victory_frame >= 180 and not victory_phase3_sound_played:
                    sound_manager.play_victory_celebration_sound()
                    victory_phase3_sound_played = True
                    
                draw_cosmic_victory(screen, WINDOW_WIDTH, WINDOW_HEIGHT, victory_frame,
                                  last_victory_info["algorithm"], 
                                  last_victory_info["steps"],
                                  last_victory_info["execution_time"])

            # Draw algorithm selector if active
            if show_algorithm_selector:
                cosmic_selector.update()
                cosmic_selector.draw(screen)
            
            # Draw loading screen if solving
            if is_solving_algorithm:
                draw_loading_screen(screen, solving_start_time, fonts, colors)

    # --- CẬP NHẬT ANIMATION PREVIEW (CHỈ KHI TRONG GAME) ---
    if game_manager.is_in_game() and preview_running:
        elapsed_s = dt / 1000.0
        time_since_last_preview += elapsed_s
        preview_elapsed_total += elapsed_s

        # Reveal group theo interval
        if time_since_last_preview >= preview_tile_interval_run:
            time_since_last_preview = 0  # SỬA: Reset về 0 thay vì trừ
            
            # Tô cả một nhóm (step) cùng lúc
            if current_preview_group < len(preview_groups):
                current_group = preview_groups[current_preview_group]
                
                # Thêm TẤT CẢ tiles trong group này vào preview_painted CÙNG LÚC
                group_tile_positions = []
                for tile in current_group:
                    if isinstance(tile, (list, tuple)) and len(tile) >= 2:
                        tile_pos = (tile[0], tile[1])
                        group_tile_positions.append(tile_pos)
                        preview_painted.add(tile_pos)
                    elif hasattr(tile, '__getitem__') and len(tile) >= 2:
                        tile_pos = (tile[0], tile[1])
                        group_tile_positions.append(tile_pos)
                        preview_painted.add(tile_pos)
                
                current_preview_group += 1

        # Khi đã reveal hết groups, dừng preview và bắt đầu phi thuyền
        if current_preview_group >= len(preview_groups):
            preview_running = False
            if pending_solving_path:
                solving_path = pending_solving_path[:]
            pending_solving_path = None
            # Reset cho lần sau
            preview_groups = []
            current_preview_group = 0

    # Hiển thị thanh thông báo khi đang ở chế độ edit
    if edit_mode:
        try:
            player_pos_tuple = tuple(player_pos)
            
            # Chỉ cần lấy số thành phần liên thông
            num_components = find_connected_components(current_maze, player_pos_tuple)
            
            # Không cần dòng 'solvable = (num_components == 1)' nữa

        except Exception as e:
            print(f"Lỗi khi kiểm tra map: {e}") 
            num_components = -1

        # Gọi hàm render đã được cập nhật (bỏ tham số 'solvable')
        render_edit_check_panel(screen, num_components,
                                player_rect, speed_display_rect,
                                BOARD_Y, TILE_SIZE, maze_rows, WINDOW_WIDTH,
                                font_edit_panel)

    pygame.display.flip()
    
pygame.quit()