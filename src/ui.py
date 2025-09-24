# ui.py
import random
import pygame
from config import *
import time
from spaceship import draw_spaceship_player, update_star_particles, draw_star_particles
from wall import asteroid_wall_renderer
# Load wall texture
wall_texture = None
def load_wall_texture():
    global wall_texture
    if wall_texture is None:
        try:
            wall_texture = pygame.image.load("asset/image/space_hd.png").convert()
        except:
            print("⚠️ Không thể load wall texture, sử dụng màu mặc định")
            wall_texture = None


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
max_trail_length = 5  # Số lượng vết tối đa
# ============================================================================


def render_text_with_outline(text, font, text_color, outline_color, outline_width=1):
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

def draw_button(screen, font, rect, color, text=None):
    shadow_rect = rect.move(3, 3)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=8)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    if text:
        text_surf = render_text_with_outline(text, font, WHITE, BLACK, 1)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

def draw_board(screen, maze, painted_tiles, player_pos, board_x, board_y, keys=None, logical_pos=None, auto_direction=None):
    load_wall_texture()  # Đảm bảo texture đã được load
    
    rows = len(maze)
    cols = len(maze[0])
    
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(board_x + c * TILE_SIZE, board_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if maze[r][c] == 1:  # Tường - vẽ với hệ thống thiên thạch mới
                wall_tile = asteroid_wall_renderer.get_wall_tile(r, c, TILE_SIZE)
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
            y_offset += 25

def draw_win_message(screen, font):
    window_rect = screen.get_rect()
    text = font.render("YOU WIN!", True, COLOR_FONT)
    text_rect = text.get_rect(center=window_rect.center)
    bg_rect = text_rect.inflate(40, 40)
    bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 150))
    screen.blit(bg_surface, bg_rect)
    screen.blit(text, text_rect)

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
                pygame.image.load("./asset/image/planet1.png"),
                pygame.image.load("./asset/image/planet2.png"),
                pygame.image.load("./asset/image/planet3.png"),
                pygame.image.load("./asset/image/planet4.png"),
                pygame.image.load("./asset/image/planet5.png"),
                pygame.image.load("./asset/image/planet6.png"),
                pygame.image.load("./asset/image/planet7.png")
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
    
    print(f"🌎 Tạo wave với {len(wave)} hành tinh khác nhau")
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
            planet_spawn_delay = 60  # Delay trước khi spawn hành tinh đầu tiên
            print(f"🌍 Tạo wave mới với {len(new_wave)} hành tinh")
    
    # Nếu có wave active -> spawn theo delay
    if planet_wave_active and planet_wave_queue:
        if planet_spawn_delay <= 0:
            spawn_planet()
            planet_spawn_delay = random.randint(60, 120)  # 1-2 giây delay giữa các hành tinh
            print(f"🚀 Spawn hành tinh, còn lại: {len(planet_wave_queue)}")
        else:
            planet_spawn_delay -= 1
    
    # Kết thúc wave khi hết hành tinh trong queue
    if planet_wave_active and len(planet_wave_queue) == 0:
        planet_wave_active = False
        planet_wave_cooldown = random.randint(180, 360)  # 3-6 giây cooldown sau khi spawn xong
        print(f"✅ Wave spawn xong, đợi hành tinh bay hết màn hình...")

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
