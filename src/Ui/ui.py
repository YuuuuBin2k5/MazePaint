# ui.py
import math
import random
import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import *
import time
from .spaceship import *
from .wall import asteroid_wall_3d_renderer
from .victory import draw_cosmic_victory
 
# Background elements - Các thành phần nền

def get_movement_direction(keys):
    """Xác định hướng di chuyển từ phím bấm"""
    if not keys:
        return None
    
    # Kiểm tra phím WASD hoặc arrow keys
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        return "up"
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        return "down"
    elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
        return "left"
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        return "right"
    
    return None
stars_far = [[random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)] for _ in range(50)]
stars_mid = [[random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)] for _ in range(40)]
stars_near = [[random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)] for _ in range(30)]

# Hành tinh
planet_imgs = []
planets = []

# Planet wave system - Hệ thống sóng hành tinh có trật tự
planet_wave_queue = []  # Hàng đợi các hành tinh sẽ spawn
planet_wave_active = False  # Có đang trong wave không
planet_spawn_delay = 0  # Delay giữa các hành tinh trong wave
planet_wave_cooldown = 0  # Thời gian nghỉ giữa các wave

# Trail system - Hệ thống vết di chuyển
player_trail = []  # Lưu các vị trí gần đây của player
max_trail_length = MAX_TRAIL_LENGTH  # Sử dụng từ config
# ============================================================================


def render_text_with_outline(text, font, text_color, outline_color, outline_width=TEXT_OUTLINE_WIDTH):
    base = font.render(text, True, text_color)
    size = base.get_size()
    surf = pygame.Surface((size[0] + 2 * outline_width, size[1] + 2 * outline_width), pygame.SRCALPHA)
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                surf.blit(outline_surf, (dx + outline_width, dy + outline_width))
    surf.blit(base, (outline_width, outline_width))
    return surf

def draw_button(screen, font, rect, color, text=None, button_style="default"):
    """
    Draw 3D style button with different styles for space theme
    button_style options: "default", "primary", "success", "info", "warning"
    """
    if button_style == "primary":
        # Main action buttons (SOLVE, etc.) - Blue cosmic theme
        base_color = (70, 130, 200)
        highlight_color = (100, 160, 230)
        shadow_color = (40, 80, 140)
        border_color = (120, 180, 255)
    elif button_style == "success":
        # Success/positive buttons (RESTART) - Green cosmic theme  
        base_color = (80, 160, 120)
        highlight_color = (110, 190, 150)
        shadow_color = (50, 110, 80)
        border_color = (140, 220, 180)
    elif button_style == "info":
        # Info buttons (MAP, HISTORY) - Cyan cosmic theme
        base_color = (60, 140, 160)
        highlight_color = (90, 170, 190)
        shadow_color = (30, 100, 120)
        border_color = (120, 200, 220)
    elif button_style == "warning":
        # Speed control buttons - Orange cosmic theme
        base_color = (180, 120, 60)
        highlight_color = (210, 150, 90)
        shadow_color = (130, 80, 30)
        border_color = (240, 180, 120)
    else:
        # Default - use provided color
        base_color = color
        highlight_color = tuple(min(255, c + 40) for c in color)
        shadow_color = tuple(max(0, c - 40) for c in color)
        border_color = tuple(min(255, c + 60) for c in color)
    
    # 3D button layers
    # 1. Deep shadow (bottom layer)
    deep_shadow_rect = rect.move(4, 4)
    pygame.draw.rect(screen, (0, 0, 0, BUTTON_SHADOW_ALPHA), deep_shadow_rect, border_radius=BUTTON_BORDER_RADIUS)
    
    # 2. Main shadow
    shadow_rect = rect.move(2, 2)  
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=8)
    
    # 3. Main button body
    pygame.draw.rect(screen, base_color, rect, border_radius=8)
    
    # 4. Top highlight (gives 3D effect)
    highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
    highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(highlight_surf, (*highlight_color, 120), (0, 0, highlight_rect.width, highlight_rect.height), border_radius=8)
    screen.blit(highlight_surf, highlight_rect)
    
    # 5. Border glow
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)
    
    # 6. Inner subtle highlight line
    inner_rect = pygame.Rect(rect.x + 2, rect.y + 1, rect.width - 4, 1)
    pygame.draw.rect(screen, border_color, inner_rect)
    
    # 7. Text with enhanced styling
    if text:
        text_surf = render_text_with_outline(text, font, WHITE, (20, 20, 40), 1)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

def draw_button_pressed(screen, font, rect, color, text=None, button_style="default"):
    """
    Draw 3D style button in pressed state (when clicked)
    """
    if button_style == "primary":
        base_color = (50, 100, 160)
        shadow_color = (30, 60, 110)
    elif button_style == "success":
        base_color = (60, 130, 90)
        shadow_color = (40, 90, 60)
    elif button_style == "info":
        base_color = (40, 110, 130)
        shadow_color = (20, 80, 100)
    elif button_style == "warning":
        base_color = (150, 90, 40)
        shadow_color = (110, 60, 20)
    else:
        base_color = tuple(max(0, c - 30) for c in color)
        shadow_color = tuple(max(0, c - 50) for c in color)
    
    # Pressed effect - no shadow, darker colors, slightly offset
    pressed_rect = rect.move(1, 1)
    
    # 1. Main button body (darker)
    pygame.draw.rect(screen, base_color, pressed_rect, border_radius=8)
    
    # 2. Inner shadow (inverted effect)
    inner_shadow = pygame.Rect(pressed_rect.x + 1, pressed_rect.y + 1, pressed_rect.width - 2, pressed_rect.height - 2)
    pygame.draw.rect(screen, shadow_color, inner_shadow, 1, border_radius=6)
    
    # 3. Text (slightly offset for pressed effect)
    if text:
        text_surf = render_text_with_outline(text, font, (220, 220, 220), (10, 10, 30), 1)
        text_rect = text_surf.get_rect(center=(pressed_rect.centerx, pressed_rect.centery + 1))
        screen.blit(text_surf, text_rect)

def draw_board(screen, maze, painted_tiles, player_pos, board_x, board_y, keys=None, logical_pos=None, auto_direction=None):
    rows = len(maze)
    cols = len(maze[0])
    
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(board_x + c * TILE_SIZE, board_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if maze[r][c] == 1:  # Tường - vẽ với hệ thống thiên thạch mới
                wall_tile = asteroid_wall_3d_renderer.get_wall_tile(r, c, TILE_SIZE)
                screen.blit(wall_tile, (rect.x, rect.y))
                    
            else:  # Ô có thể di chuyển
                if painted_tiles[r][c]:
                    # Ô đã đi qua - hiệu ứng "completed path"
                    # Vẽ lớp mờ với màu xanh dương đậm
                    overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    overlay.fill(PATH_OVERLAY)  # Sử dụng màu từ config
                    screen.blit(overlay, rect)
                    
                    # Thêm viền sáng để thể hiện "đã hoàn thành"
                    pygame.draw.rect(screen, PATH_GLOW, rect, 2)
                    
                    # Hiệu ứng sparkle nhỏ ở giữa
                    center_x = rect.centerx
                    center_y = rect.centery
                    pygame.draw.circle(screen, (150, 220, 255), (center_x, center_y), 3)
                else:
                    # Ô chưa đi qua - background mờ đen
                    overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    overlay.fill(UNVISITED_OVERLAY)  # Sử dụng màu từ config
                    screen.blit(overlay, rect)
                    
                    # Viền mờ để phân biệt với tường
                    pygame.draw.rect(screen, (50, 50, 100), rect, 1)
    
    # Vẽ hiệu ứng completion cho các ô đã đi
    add_completion_effect(screen, board_x, board_y, painted_tiles)
    
    # Cập nhật và vẽ trail của player (sử dụng logical position)
    trail_pos = logical_pos if logical_pos else [int(player_pos[0]), int(player_pos[1])]
    update_player_trail(trail_pos, board_x, board_y)
    draw_player_trail(screen)
    
    # Vẽ người chơi - spaceship với animation (hỗ trợ smooth movement)
    center_x = board_x + player_pos[1] * TILE_SIZE + TILE_SIZE // 2
    center_y = board_y + player_pos[0] * TILE_SIZE + TILE_SIZE // 2
    
    # Xác định hướng di chuyển từ phím bấm hoặc auto solve
    direction = None
    # Kiểm tra xem có phím nào được bấm không (thay vì chỉ kiểm tra keys tồn tại)
    manual_direction = None
    if keys:
        manual_direction = get_movement_direction(keys)
    
    if manual_direction:
        direction = manual_direction
    elif auto_direction:
        # Chuyển đổi từ direction của game logic (CHỮ HOA) sang direction của spaceship (chữ thường)
        direction_mapping = {
            "UP": "up",
            "DOWN": "down", 
            "LEFT": "left",
            "RIGHT": "right"
        }
        direction = direction_mapping.get(auto_direction, None)
    
    # Vẽ spaceship với rotation theo hướng di chuyển
    draw_spaceship_player(screen, center_x, center_y, direction)

def draw_history_box(screen, font, history_list):
    box_rect = pygame.Rect(840, 100, 240, 200)
    pygame.draw.rect(screen, DARK_BLUE, box_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=8)
    
    title_surf = font.render("Last Solve Stats", True, WHITE)
    screen.blit(title_surf, (box_rect.x + 10, box_rect.y + 10))

    if not history_list:
        no_history_surf = font.render("No history yet.", True, WHITE)
        screen.blit(no_history_surf, (box_rect.x + 10, box_rect.y + 40))
    else:
        map_name, algo, result = history_list[-1]
        y_offset = box_rect.y + 40
        if result:
            lines = [f"Map: {map_name}", f"Algo: {algo}", f"Steps: {result['steps']}", f"Visited: {result['visited']}", f"Time: {round(result['time'], 4)}s"]
        else:
            lines = [f"Map: {map_name}", f"Algo: {algo}", "No solution found."]
        for line in lines:
            info_surf = font.render(line, True, WHITE)
            screen.blit(info_surf, (box_rect.x + 10, y_offset))
            y_offset += HISTORY_Y_OFFSET

def draw_move_count(screen, x, y, font, count):
    text_surf = render_text_with_outline(f"Moves: {count}", font, WHITE, BLACK, 1)
    screen.blit(text_surf, (x, y))

def draw_text_outline(screen, text, pos, text_color, outline_color, outline_width, center=False, font=None):
    """Helper function để vẽ text với outline"""
    if font is None:
        font = pygame.font.Font(None, 24)
    
    # Tạo text surface
    text_surf = font.render(text, True, text_color)
    
    # Tạo outline surface
    outline_surf = font.render(text, True, outline_color)
    
    # Tính vị trí
    if center:
        x, y = pos
        text_rect = text_surf.get_rect(center=(x, y))
        pos = (text_rect.x, text_rect.y)
    
    # Vẽ outline bằng cách vẽ text ở các vị trí lân cận
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                screen.blit(outline_surf, (pos[0] + dx, pos[1] + dy))
    
    # Vẽ text chính
    screen.blit(text_surf, pos)

def draw_text(screen, text, pos, color, center=False, font=None):
    """Helper function để vẽ text đơn giản"""
    if font is None:
        font = pygame.font.Font(None, 24)
    
    text_surf = font.render(text, True, color)
    
    if center:
        x, y = pos
        text_rect = text_surf.get_rect(center=(x, y))
        screen.blit(text_surf, text_rect)
    else:
        screen.blit(text_surf, pos)

def flat_to_matrix(flat_list, rows, cols):
    """Chuyển đổi list phẳng thành matrix 2D"""
    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            idx = i * cols + j
            if idx < len(flat_list):
                row.append(flat_list[idx])
            else:
                row.append(0)
        matrix.append(row)
    return matrix

def draw_matrix(screen, matrix, x, y, cell_width, cell_height, fonts, colors, tiles):
    """Vẽ matrix mini maze với tường giống game thật"""
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            rect = pygame.Rect(x + j * cell_width, y + i * cell_height, cell_width, cell_height)
            if cell == 1:  # Wall - sử dụng texture giống game
                # Tạo wall tile với kích thước mini
                wall_tile = asteroid_wall_3d_renderer.get_wall_tile(i, j, max(cell_width, cell_height))
                # Scale về kích thước mini nếu cần
                if cell_width != max(cell_width, cell_height) or cell_height != max(cell_width, cell_height):
                    wall_tile = pygame.transform.scale(wall_tile, (cell_width, cell_height))
                screen.blit(wall_tile, (rect.x, rect.y))
            else:  # Path - màu xanh giống game thật
                # Vẽ nền xanh giống như trong game chính
                pygame.draw.rect(screen, COLOR_BACKGROUND, rect)  # Nền xanh đậm
                # Thêm viền để tạo hiệu ứng lưới
                if cell_width > 2 and cell_height > 2:
                    pygame.draw.rect(screen, (40, 60, 80), rect, 1)  # Viền xanh nhạt hơn

def draw_history_panel(screen, history_groups, scroll_offset, panel_rect, close_rect, fonts, colors, tiles):
    """Vẽ panel lịch sử theo nhóm, with ms time and layout.

    `history_groups` expected to be an ordered dict or dict mapping
    state_tuple -> {'rows':R, 'cols':C, 'results':[{'algorithm':..,'steps':..,'visited_count':..,'generated_count':..,'execution_time':..}, ...]}
    """
    # 1. Vẽ các thành phần chung của panel
    pygame.draw.rect(screen, colors['bg'], panel_rect, border_radius=15)
    pygame.draw.rect(screen, colors['border'], panel_rect, 3, border_radius=15)
    draw_text_outline(screen, "Solve History", (panel_rect.centerx, panel_rect.top + 40),
                      colors['title'], colors['black'], 2, center=True, font=fonts['state'])
    pygame.draw.rect(screen, (200, 50, 50), close_rect, border_radius=5)
    draw_text(screen, "X", close_rect.center, colors['white'], center=True, font=fonts['btn'])

    # 2. Tạo vùng cắt và vẽ tiêu đề cho bảng
    header_y = panel_rect.y + 85
    content_y_start = header_y + 35
    content_rect = pygame.Rect(panel_rect.x + 20, content_y_start, panel_rect.width - 40, panel_rect.bottom - content_y_start - 20)

    # Định nghĩa vị trí X cho từng cột
    table_x_start = panel_rect.x + 160
    col_x = {
        "algo": table_x_start + 70,
        "steps": table_x_start + 200,
        "visited": table_x_start + 280,
        "generated": table_x_start + 380,
        "time": table_x_start + 500,
    }

    # Vẽ dòng tiêu đề của bảng
    draw_text_outline(screen, "Algorithm", (col_x["algo"], header_y), colors['white'], colors['black'], 1, font=fonts['btn'])
    draw_text_outline(screen, "Steps", (col_x["steps"], header_y), colors['white'], colors['black'], 1, font=fonts['btn'])
    draw_text_outline(screen, "Visited", (col_x["visited"], header_y), colors['white'], colors['black'], 1, font=fonts['btn'])
    draw_text_outline(screen, "Generated", (col_x["generated"], header_y), colors['white'], colors['black'], 1, font=fonts['btn'])
    draw_text_outline(screen, "Time (ms)", (col_x["time"], header_y), colors['white'], colors['black'], 1, font=fonts['btn'])

    # Vẽ đường kẻ ngang dưới tiêu đề
    pygame.draw.line(screen, colors['border'], (panel_rect.x + 20, header_y + 25), (panel_rect.right - 20, header_y + 25), 2)

    # 3. Vẽ nội dung các hàng
    screen.set_clip(content_rect)

    if not history_groups:
        draw_text_outline(screen, "No history yet.", panel_rect.center, colors['white'], colors['black'], 1, center=True, font=fonts['label'])
    else:
        y_cursor = content_rect.top - scroll_offset

        group_padding, row_height, header_height = 40, 35, 110

        # iterate in insertion order if dict-like, else iterate items
        for state_tuple, group_data in history_groups.items():
            group_height = header_height + (len(group_data['results']) * row_height) + group_padding

            if y_cursor + group_height > content_rect.top and y_cursor < content_rect.bottom:
                # Vẽ puzzle mini đại diện cho nhóm
                rows, cols = group_data.get('rows', MAZE_ROWS), group_data.get('cols', MAZE_COLS)
                maze_structure = group_data.get('maze', [])  # Lấy maze structure
                puzzle_w, puzzle_h = 100, 100
                puzzle_x, puzzle_y = content_rect.left + 10, y_cursor + 5

                frame_rect = pygame.Rect(puzzle_x, puzzle_y, puzzle_w, puzzle_h)
                padding = 2
                grid_w, grid_h = puzzle_w - padding*2, puzzle_h - padding*2
                cell_width, cell_height = max(8, grid_w // cols), max(8, grid_h // rows)
                
                # Không vẽ nền mini map nữa - để mini map hiển thị trực tiếp trên nền panel
                
                # Sử dụng maze structure thay vì state tuple
                if maze_structure:
                    draw_matrix(screen, maze_structure, puzzle_x + padding, puzzle_y + padding, cell_width, cell_height, fonts, colors, tiles)
                    
                    # Tính kích thước thực tế của mini map dựa trên matrix đã vẽ
                    actual_rows = len(maze_structure)
                    actual_cols = len(maze_structure[0]) if maze_structure else 0
                    actual_map_width = actual_cols * cell_width
                    actual_map_height = actual_rows * cell_height
                    
                    # Vẽ khung bao lên trên mini map (không bo tròn)
                    map_rect = pygame.Rect(puzzle_x + padding, puzzle_y + padding, 
                                         actual_map_width, actual_map_height)
                    pygame.draw.rect(screen, (120, 150, 200), map_rect, 2)  # Viền xanh sáng, độ dày 2

                # Vẽ bảng kết quả cho nhóm
                for i, result in enumerate(group_data['results']):
                    # Căn chỉnh vị trí Y của hàng đầu tiên ngang với puzzle mini
                    row_y = puzzle_y + (i * row_height)

                    draw_text_outline(screen, result.get('algorithm', result.get('method', 'N/A')), (col_x["algo"], row_y), colors['white'], colors['black'], 1, font=fonts['btn'])
                    draw_text_outline(screen, str(result.get('steps', result.get('steps', 0))), (col_x["steps"], row_y), colors['white'], colors['black'], 1, font=fonts['btn'])
                    draw_text_outline(screen, str(result.get('visited_count', result.get('visited', 'N/A'))), (col_x["visited"], row_y), colors['white'], colors['black'], 1, font=fonts['btn'])
                    draw_text_outline(screen, str(result.get('generated_count', result.get('states', 'N/A'))), (col_x["generated"], row_y), colors['white'], colors['black'], 1, font=fonts['btn'])

                    # Chuyển đổi giây sang mili giây (* 1000) và làm tròn
                    exec_time = result.get('execution_time', result.get('time', 0.0))
                    time_ms = exec_time * 1000
                    draw_text_outline(screen, f"{time_ms:.1f}", (col_x["time"], row_y), colors['white'], colors['black'], 1, font=fonts['btn'])

            y_cursor += group_height

    screen.set_clip(None)

#===========================================================================
# PLANET IMAGES - Ảnh hành tinh
def init_planet_images():
    """
    Khởi tạo ảnh hành tinh cho background effect.
    """
    global planet_imgs
    if not planet_imgs:  # Chỉ load 1 lần
        try:
            planet_imgs = [
                pygame.image.load("asset/image/planet1.png"),
                pygame.image.load("asset/image/planet2.png"),
                pygame.image.load("asset/image/planet3.png"),
                pygame.image.load("asset/image/planet4.png"),
                pygame.image.load("asset/image/planet5.png"),
                pygame.image.load("asset/image/planet6.png"),
                pygame.image.load("asset/image/planet7.png")
            ]
        except Exception as e:
            print(f"⚠️ Lỗi khi load ảnh hành tinh: {e}")

# ============================================================================
# BACKGROUND EFFECTS - Hiệu ứng nền
# ============================================================================

def draw_stars(screen):
    """
    Vẽ hiệu ứng sao bay 3 lớp với tốc độ khác nhau để tạo độ sâu.
    
    - Lớp xa (stars_far): Sao nhỏ, chậm, màu xanh nhạt
    - Lớp trung (stars_mid): Sao trung bình, tốc độ vừa  
    - Lớp gần (stars_near): Sao lớn, nhanh, màu trắng sáng
    
    Args:
        screen (pygame.Surface): Surface màn hình chính
    """
    # Lớp sao xa - chuyển động chậm
    for star in stars_far:
        pygame.draw.circle(screen, (200, 200, 255), (int(star[0]), int(star[1])), 1)
        star[0] -= 0.3
        if star[0] < 0:
            star[0] = WINDOW_WIDTH
            star[1] = random.randint(0, WINDOW_HEIGHT)
    
    # Lớp sao trung bình        
    for star in stars_mid:
        pygame.draw.circle(screen, (230, 230, 255), (int(star[0]), int(star[1])), 2)
        star[0] -= 0.6
        if star[0] < 0:
            star[0] = WINDOW_WIDTH
            star[1] = random.randint(0, WINDOW_HEIGHT)
    
    # Lớp sao gần - chuyển động nhanh        
    for star in stars_near:
        pygame.draw.circle(screen, (255, 255, 255), (int(star[0]), int(star[1])), 3)
        star[0] -= 1
        if star[0] < 0:
            star[0] = WINDOW_WIDTH
            star[1] = random.randint(0, WINDOW_HEIGHT)

def create_planet_wave():
    """
    Tạo một wave (sóng) hành tinh có trật tự.
    
    Mỗi wave bao gồm 2-4 hành tinh với:
    - Kích thước và loại đa dạng
    - Vị trí Y được sắp xếp để tránh chồng lấp
    - Tốc độ tương đối đồng đều để bay cùng nhau
    
    Returns:
        list: Danh sách các planet data [img, size, y, speed]
    """
    init_planet_images()
    
    if not planet_imgs:
        return []
    
    wave = []
    # Giới hạn wave_size không vượt quá số lượng hình ảnh hành tinh có sẵn
    max_planets = len(planet_imgs)
    wave_size = random.randint(3, min(max_planets, 5))  # 3-5 hành tinh, có thể đến 5 vì có 7 ảnh
    base_speed = random.uniform(0.8, 1.2)  # Tốc độ cơ bản cho wave
    
    # Tạo danh sách hành tinh có sẵn và trộn ngẫu nhiên để tránh trùng lặp
    available_planets = planet_imgs.copy()  # Copy để không ảnh hưởng list gốc
    random.shuffle(available_planets)  # Trộn ngẫu nhiên
    
    # Chia màn hình thành các khu vực an toàn
    safe_areas = []
    margin_top = 80
    margin_bottom = 80
    usable_height = WINDOW_HEIGHT - margin_top - margin_bottom
    
    if wave_size <= 1:
        safe_areas = [WINDOW_HEIGHT // 2]  # Giữa màn hình
    else:
        area_height = usable_height // wave_size
        for i in range(wave_size):
            center_y = margin_top + area_height // 2 + i * area_height
            safe_areas.append(center_y)
    
    # Trộn ngẫu nhiên thứ tự các vùng
    random.shuffle(safe_areas)
    
    for i in range(wave_size):
        # Chọn hành tinh KHÔNG trùng lặp từ danh sách đã trộn
        img = available_planets[i]  # Lấy theo thứ tự, đảm bảo không trùng
        
        # Kích thước hợp lý
        size = random.randint(70, 100)  # Nhỏ hơn để tránh chồng lấp
        scaled_img = pygame.transform.smoothscale(img, (size, size))
        
        # Vị trí Y từ safe area với offset nhỏ
        base_y = safe_areas[i]
        offset_range = min(30, area_height // 3) if wave_size > 1 else 50
        y_offset = random.randint(-offset_range, offset_range)
        y = base_y + y_offset
        
        # Đảm bảo trong bounds màn hình
        y = max(margin_top, min(y, WINDOW_HEIGHT - margin_bottom - size))
        
        # Tốc độ đồng đều với biến thiên nhẹ
        speed = base_speed + random.uniform(-0.1, 0.1)
        speed = max(0.6, min(speed, 1.5))  # Giới hạn tốc độ
        
        wave.append([scaled_img, size, y, speed])
    
    return wave

def spawn_planet():
    """
    Spawn một hành tinh từ wave queue.
    Chỉ được gọi khi có hành tinh trong hàng đợi.
    """
    global planet_wave_queue
    
    if planet_wave_queue:
        planet_data = planet_wave_queue.pop(0)
        img, size, y, speed = planet_data
        planets.append([WINDOW_WIDTH, y, img, speed])

def update_planet_system():
    """
    Cập nhật hệ thống spawn hành tinh có trật tự.
    
    Logic:
    1. Kiểm tra xem có hành tinh nào còn trên màn hình không
    2. Chỉ tạo wave mới khi không có hành tinh nào và hết cooldown
    3. Spawn hành tinh theo delay trong wave
    """
    global planet_wave_queue, planet_wave_active, planet_spawn_delay, planet_wave_cooldown
    
    # Giảm cooldown
    if planet_wave_cooldown > 0:
        planet_wave_cooldown -= 1
        return
    
    # Kiểm tra xem còn hành tinh nào trên màn hình không
    planets_on_screen = len(planets) > 0
    
    # CHỈ tạo wave mới khi:
    # 1. Không có wave đang active
    # 2. Không còn hành tinh nào trong queue  
    # 3. Không còn hành tinh nào trên màn hình
    # 4. Đã hết cooldown
    if (not planet_wave_active and 
        len(planet_wave_queue) == 0 and 
        not planets_on_screen and 
        planet_wave_cooldown <= 0):
        
        new_wave = create_planet_wave()
        if new_wave:
            planet_wave_queue = new_wave
            planet_wave_active = True
            planet_spawn_delay = PLANET_SPAWN_DELAY  # Delay trước khi spawn hành tinh đầu tiên
    
    
    # Nếu có wave active -> spawn theo delay
    if planet_wave_active and planet_wave_queue:
        if planet_spawn_delay <= 0:
            spawn_planet()
            planet_spawn_delay = random.randint(60, 120)  # 1-2 giây delay giữa các hành tinh
        else:
            planet_spawn_delay -= 1
    
    # Kết thúc wave khi hết hành tinh trong queue
    if planet_wave_active and len(planet_wave_queue) == 0:
        planet_wave_active = False
        planet_wave_cooldown = random.randint(180, 360)  # 3-6 giây cooldown sau khi spawn xong

def draw_planets(screen):
    """
    Vẽ tất cả hành tinh và cập nhật vị trí của chúng.
    
    Args:
        screen (pygame.Surface): Surface màn hình chính
    """
    for planet in planets[:]:  # Copy list để tránh lỗi khi xóa phần tử
        screen.blit(planet[2], (int(planet[0]), int(planet[1])))
        planet[0] -= planet[3]  # Di chuyển sang trái
        
        # Xóa hành tinh khi ra khỏi màn hình
        if planet[0] < -200:
            planets.remove(planet)

def update_player_trail(player_pos, board_x, board_y):
    """
    Cập nhật vết di chuyển của player.
    
    Args:
        player_pos (list): Vị trí hiện tại của player [row, col]
        board_x, board_y (int): Tọa độ board trên màn hình
    """
    global player_trail
    
    # Tính tọa độ pixel của player
    pixel_pos = [
        board_x + player_pos[1] * TILE_SIZE + TILE_SIZE // 2,
        board_y + player_pos[0] * TILE_SIZE + TILE_SIZE // 2
    ]
    
    # Thêm vị trí mới vào trail
    player_trail.append({
        'pos': pixel_pos,
        'alpha': 255,  # Độ trong suốt ban đầu
        'size': PLAYER_RADIUS
    })
    
    # Giới hạn độ dài trail
    if len(player_trail) > max_trail_length:
        player_trail.pop(0)
    
    # Cập nhật alpha và size của các trail cũ
    for i, trail in enumerate(player_trail[:-1]):  # Không cập nhật trail cuối (mới nhất)
        trail['alpha'] = max(0, trail['alpha'] - 50)  # Giảm độ sáng
        trail['size'] = max(2, trail['size'] - 2)     # Giảm kích thước

def draw_player_trail(screen):
    """
    Vẽ vết di chuyển của player.
    
    Args:
        screen (pygame.Surface): Surface màn hình chính
    """
    for trail in player_trail[:-1]:  # Không vẽ trail cuối (đó là vị trí hiện tại)
        if trail['alpha'] > 0:
            # Tạo surface trong suốt cho trail
            trail_surf = pygame.Surface((trail['size'] * 2, trail['size'] * 2), pygame.SRCALPHA)
            trail_color = (*COLOR_PLAYER[:3], trail['alpha'] // 3)  # Màu player với alpha giảm
            pygame.draw.circle(trail_surf, trail_color, (trail['size'], trail['size']), trail['size'])
            
            # Vẽ trail lên màn hình
            screen.blit(trail_surf, (trail['pos'][0] - trail['size'], trail['pos'][1] - trail['size']))

def add_completion_effect(screen, board_x, board_y, painted_tiles):
    """
    Thêm hiệu ứng khi hoàn thành một ô.
    
    Args:
        screen (pygame.Surface): Surface màn hình
        board_x, board_y (int): Tọa độ board
        painted_tiles (list): Ma trận các ô đã đi
    """
    
    # Tìm các ô vừa được hoàn thành (có thể mở rộng logic này)
    rows, cols = len(painted_tiles), len(painted_tiles[0])
    current_time = time.time()
    
    for r in range(rows):
        for c in range(cols):
            if painted_tiles[r][c]:
                rect = pygame.Rect(board_x + c * TILE_SIZE, board_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # Hiệu ứng pulse nhẹ cho các ô đã hoàn thành
                pulse_intensity = int(50 + 30 * abs(pygame.math.Vector2(current_time * 3).length() % 2 - 1))
                pulse_color = (100, 150 + pulse_intensity, 255, 80)
                
                pulse_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                pulse_surf.fill(pulse_color)
                screen.blit(pulse_surf, rect)

def render_text_outline(target_surf, text, font, pos, fg,
                        outline_col=(6, 16, 26), outline_width=2, blend_add=False):
    """
    Vẽ text với outline đơn giản và hiệu ứng additive tùy chọn.
    - target_surf: pygame.Surface để blit lên
    - text: chuỗi
    - font: pygame.font.Font
    - pos: (x, y) tọa độ top-left của text
    - fg: màu chính (tuple)
    - outline_col: màu viền
    - outline_width: bán kính viền (số pixel offsets)
    - blend_add: nếu True, main text sẽ blit bằng BLEND_ADD (nhẹ neon)
    """
    x, y = pos
    # Outline surface (render once)
    outline_s = font.render(text, True, outline_col)
    # Blit outline at offsets
    for ox in range(-outline_width, outline_width + 1):
        for oy in range(-outline_width, outline_width + 1):
            if ox == 0 and oy == 0:
                continue
            target_surf.blit(outline_s, (x + ox, y + oy))
    # Main text
    main_s = font.render(text, True, fg)
    if blend_add:
        # slightly reduce alpha so additive doesn't blow out
        main_s.set_alpha(220)
        target_surf.blit(main_s, (x, y), special_flags=pygame.BLEND_ADD)
    else:
        target_surf.blit(main_s, (x, y))

def render_edit_check_panel(screen, solvable, comps, player_pos,
                            player_rect, speed_display_rect,
                            board_y, tile_size, maze_rows, window_width,
                            font_vn, font_mono):
    """
    Vẽ panel 'Kiểm tra map: PASS/FAIL' theo phong cách 3D máy móc.
    Không thay đổi state, chỉ render.
    """
    # Layout ngang bằng nút Player nếu có
    base_btn_w = player_rect.width if player_rect else 360
    bar_w = int(base_btn_w)
    bar_h = 72
    gap = 12

    ref_cx = speed_display_rect.centerx if speed_display_rect else window_width // 2
    bar_x = int(ref_cx - bar_w // 2)
    bar_x = max(12, min(bar_x, window_width - bar_w - 12))
    bar_y = (speed_display_rect.bottom + gap) if speed_display_rect else 20

    board_bottom = board_y + maze_rows * tile_size
    if bar_y + bar_h > board_bottom - 8:
        bar_y = max(8, board_bottom - bar_h - 8)

    # Shadow nền
    shadow = pygame.Surface((bar_w + 10, bar_h + 10), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 180), shadow.get_rect(), border_radius=14)
    screen.blit(shadow, (bar_x + 6, bar_y + 6))

    # Extruded layers -> cảm giác 3D sâu
    for d in range(5, 0, -1):
        layer = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        shade = 6 + d * 8
        layer.fill((shade, shade + 6, shade + 14, 255))
        pygame.draw.rect(layer, (shade + 34, shade + 56, shade + 74, 18),
                         layer.get_rect(), 1, border_radius=12)
        screen.blit(layer, (bar_x, bar_y + d))

    # Top face (metallic + deep-blue neon)
    top = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
    top_rect = top.get_rect()
    for y in range(bar_h):
        t = y / max(1, bar_h - 1)
        r = int(4 * (1 - t) + 8 * t)
        g = int(10 * (1 - t) + 80 * t)
        b = int(20 * (1 - t) + 120 * t)
        pygame.draw.line(top, (r, g, b, 240), (0, y), (bar_w, y))
    # specular strip (muted)
    spec_h = bar_h // 3
    spec = pygame.Surface((bar_w - 20, spec_h), pygame.SRCALPHA)
    for i in range(spec_h):
        a = int(120 * (1 - i / max(1, spec_h - 1)) ** 2)
        pygame.draw.line(spec, (40, 120, 160, a), (0, i), (spec.get_width(), i))
    top.blit(spec, (10, 6), special_flags=pygame.BLEND_PREMULTIPLIED)

    pygame.draw.rect(top, (80, 160, 190, 40), top_rect, 1, border_radius=12)
    pygame.draw.rect(top, (6, 18, 34, 120), top_rect.inflate(-6, -6), 1, border_radius=10)

    screen.blit(top, (bar_x, bar_y))

    # Neon outer glow (subtle)
    glow = pygame.Surface((bar_w + 28, bar_h + 28), pygame.SRCALPHA)
    for i, a in enumerate((26, 14, 8)):
        c = (12, 100, 170, a)
        pygame.draw.rect(glow, c, pygame.Rect(8 - i, 8 - i, bar_w + 2 * i + 12, bar_h + 2 * i + 12),
                         border_radius=14 - i)
    screen.blit(glow, (bar_x - 12, bar_y - 12), special_flags=pygame.BLEND_ADD)

    # Indicator: vòng tròn 3D, segmented + inner core
    ring_size = 35
    ring_x = bar_x + 26 - 20
    ring_y = bar_y + (bar_h - ring_size) // 2
    ring_surf = pygame.Surface((ring_size, ring_size), pygame.SRCALPHA)
    cx, cy = ring_size // 2, ring_size // 2
    outer_r = ring_size // 2 - 2
    inner_r = outer_r - 10

    pygame.draw.circle(ring_surf, (18, 44, 60), (cx, cy), outer_r + 2)
    pygame.draw.circle(ring_surf, (28, 86, 110), (cx, cy), outer_r, 6)

    seg_count = 10
    for i in range(seg_count):
        angle = i * (360 / seg_count)
        v = pygame.math.Vector2(1, 0).rotate(angle)
        tx = cx + int(v.x * (outer_r - 6))
        ty = cy + int(v.y * (outer_r - 6))
        color = (18, 140, 190) if solvable else (180, 70, 70)
        pygame.draw.circle(ring_surf, color, (tx, ty), 3)

    core_surf = pygame.Surface((inner_r * 2, inner_r * 2), pygame.SRCALPHA)
    for i in range(inner_r, 0, -1):
        a = int(120 * (1 - i / inner_r))
        col = (22, 150, 130) if solvable else (190, 80, 80)
        pygame.draw.circle(core_surf, (*col, a), (inner_r, inner_r), i)
    pygame.draw.circle(core_surf, (6, 18, 24, 200), (inner_r, inner_r), max(2, inner_r // 3))

    ring_surf.blit(core_surf, (cx - inner_r, cy - inner_r), special_flags=pygame.BLEND_PREMULTIPLIED)
    pygame.draw.circle(ring_surf, (8, 28, 40, 180), (cx, cy), inner_r - 1, 1)
    screen.blit(ring_surf, (ring_x, ring_y), special_flags=pygame.BLEND_ADD)

    # Text: nổi bật, bevel + neon glow (không dùng trắng nguyên)
    status_text = "Kiểm tra map: PASS" if solvable else "Kiểm tra map: FAIL"
    # main color: tăng tương phản, không dùng trắng nguyên
    main_col = (40, 230, 190) if solvable else (230, 120, 120)
    outline_col = (6, 14, 22)
    txt_x = ring_x + ring_size
    txt_y = bar_y + (bar_h - font_vn.get_height()) // 2

    # Render outlined text để tối ưu readability
    render_text_outline(screen, status_text, font_vn, (txt_x, txt_y), main_col,
                        outline_col=outline_col, outline_width=2, blend_add=False)
    # nhẹ nhàng thêm một lớp neon mờ (không làm mờ chữ)
    try:
        neon = font_vn.render(status_text, True, (18, 110, 170))
        neon.set_alpha(28)
        screen.blit(neon, (txt_x + 1, txt_y + 1), special_flags=pygame.BLEND_ADD)
    except Exception:
        pass
