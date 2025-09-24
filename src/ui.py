# ui.py
import math
import random
import pygame
from config import *
import time
from spaceship import draw_spaceship_player, update_star_particles, draw_star_particles
from wall import asteroid_wall_3d_renderer


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
            y_offset += 25

def draw_cosmic_victory(screen, width, height, frame):
    """Vẽ hiệu ứng victory với spaceship bay qua các hành tinh"""
    center = (width // 2, height // 2)
    
    # Animation phases based on frame count
    # Phase 1: 0-80 frames - Spaceship flying through planets
    # Phase 2: 80-180 frames - Spaceship stops and shows dialogue
    # Phase 3: 180+ frames - Victory display
    
    # 1. Deep Space Gradient Background
    for y in range(height):
        ratio = y / height
        r = int(5 * (1 - ratio) + 25 * ratio)
        g = int(2 * (1 - ratio) + 15 * ratio)
        b = int(15 * (1 - ratio) + 45 * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

    # 2. Distant Stars
    random.seed(42)
    for _ in range(60):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.uniform(0.4, 0.8)
        twinkle = abs(math.sin(frame * 0.03 + x * 0.01 + y * 0.01))
        alpha = int(brightness * twinkle * 150)
        color = random.choice([(255,255,255), (200,220,255)])
        star_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (*color, alpha), (1, 1), 1)
        screen.blit(star_surf, (x-1, y-1))

    if frame < 80:  # PHASE 1: SPACESHIP JOURNEY ANIMATION
        # 3. Draw planets at fixed positions for spaceship to fly through (reduced to 3 planets)
        planet_positions = [
            (width * 0.7, height * 0.3, 90, "planet1.png"),   # Top right
            (width * 0.3, height * 0.5, 100, "planet2.png"),  # Left middle  
            (width * 0.6, height * 0.7, 80, "planet3.png"),   # Right lower
        ]
        
        # Draw planets with gentle glow
        for px, py, size, planet_name in planet_positions:
            try:
                planet_img = pygame.image.load(f"./asset/image/{planet_name}")
                planet_img = pygame.transform.scale(planet_img, (size, size))
                
                # Planet glow
                glow_surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
                glow_color = (100, 150, 200, 40)
                pygame.draw.circle(glow_surf, glow_color, (size//2 + 10, size//2 + 10), size//2 + 10)
                screen.blit(glow_surf, (px - size//2 - 10, py - size//2 - 10))
                
                # Planet itself
                planet_rect = planet_img.get_rect(center=(px, py))
                screen.blit(planet_img, planet_rect)
            except:
                # Fallback: draw colored circle
                colors = [(255,100,100), (100,255,100), (100,100,255), (255,255,100), (255,100,255)]
                color = colors[len(planet_name) % len(colors)]
                pygame.draw.circle(screen, color, (int(px), int(py)), size//2)

        # 4. Spaceship flight path - curvy journey through planets
        journey_progress = frame / 80.0  # Faster journey - changed from 120.0 to 80.0
        
        if journey_progress <= 1.0:
            # Define waypoints for spaceship journey (simplified path for 3 planets)
            waypoints = [
                (-50, height * 0.5),          # Start off-screen left
                (width * 0.2, height * 0.35), # Approach first area
                (width * 0.6, height * 0.25), # Near planet1 (top right)
                (width * 0.4, height * 0.5),  # Near planet2 (left middle)
                (width * 0.55, height * 0.6), # Middle transition
                (width * 0.65, height * 0.75),# Near planet3 (right lower)
                (center[0], center[1] - 50),   # Final position above center
            ]
            
            # Calculate current position using smooth interpolation
            segment_count = len(waypoints) - 1
            segment_progress = journey_progress * segment_count
            segment_index = int(segment_progress)
            local_progress = segment_progress - segment_index
            
            if segment_index < segment_count:
                # Smooth interpolation between waypoints
                start_point = waypoints[segment_index]
                end_point = waypoints[segment_index + 1]
                
                # Ease in-out for smooth movement
                t = local_progress
                t = t * t * (3.0 - 2.0 * t)  # Smoothstep
                
                spaceship_x = start_point[0] + (end_point[0] - start_point[0]) * t
                spaceship_y = start_point[1] + (end_point[1] - start_point[1]) * t
                
                # Calculate direction based on movement
                if local_progress < 0.95:  # Don't calculate direction at very end
                    dx = end_point[0] - start_point[0]
                    dy = end_point[1] - start_point[1]
                    
                    if abs(dx) > abs(dy):
                        direction = "right" if dx > 0 else "left"
                    else:
                        direction = "down" if dy > 0 else "up"
                else:
                    direction = "up"  # Final direction pointing up
                
                # Draw spaceship trail
                trail_length = 8
                for i in range(trail_length):
                    trail_alpha = (i / trail_length) * 100
                    trail_offset = i * 8
                    trail_x = spaceship_x - (end_point[0] - start_point[0]) * 0.02 * i
                    trail_y = spaceship_y - (end_point[1] - start_point[1]) * 0.02 * i
                    
                    trail_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, (100, 200, 255, int(trail_alpha)), (6, 6), 4)
                    screen.blit(trail_surf, (trail_x - 6, trail_y - 6))
                
                # Draw spaceship (larger during journey)
                from spaceship import draw_spaceship_player
                spaceship_scale = 1.5  # Larger during journey
                # We'll draw it manually since we need custom size
                try:
                    from spaceship import load_spaceship_image, spaceship_rotated_images
                    load_spaceship_image()
                    
                    ship_img = spaceship_rotated_images.get(direction, spaceship_rotated_images[None])
                    # Scale up the spaceship
                    scaled_size = int(PLAYER_RADIUS * 6)  # Bigger than normal
                    ship_img = pygame.transform.scale(ship_img, (scaled_size, scaled_size))
                    ship_rect = ship_img.get_rect(center=(spaceship_x, spaceship_y))
                    screen.blit(ship_img, ship_rect)
                    
                    # Engine glow
                    glow_surf = pygame.Surface((scaled_size + 30, scaled_size + 30), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (100, 200, 255, 60), (scaled_size//2 + 15, scaled_size//2 + 15), scaled_size//2 + 15)
                    screen.blit(glow_surf, (spaceship_x - scaled_size//2 - 15, spaceship_y - scaled_size//2 - 15))
                except:
                    # Fallback: simple triangle
                    pygame.draw.circle(screen, (100, 200, 255), (int(spaceship_x), int(spaceship_y)), 15)

        # Show progress text during journey
        if frame < 70:  # Shortened from 100 to 70 for faster journey
            try:
                journey_font = pygame.font.SysFont("Times New Roman", 36, bold=True)
            except:
                try:
                    journey_font = pygame.font.SysFont("Calibri", 36, bold=True)
                except:
                    journey_font = pygame.font.Font(None, 42)
            
            journey_texts = [
                "Exploring the galaxy...",
                "Mission accomplished!", 
            ]
            
            text_index = min(int(journey_progress * len(journey_texts)), len(journey_texts) - 1)
            journey_text = journey_font.render(journey_texts[text_index], True, (200, 220, 255))
            journey_text.set_alpha(int(200 * math.sin(frame * 0.1)))
            text_rect = journey_text.get_rect(center=(center[0], height - 60))
            screen.blit(journey_text, text_rect)

    elif frame < 180:  # PHASE 2: SPACESHIP DIALOGUE PHASE (frame 80-180)
        dialogue_frame = frame - 80  # 0-100 frame for dialogue phase
        
        # 3. Show planets (static during dialogue)
        planet_positions = [
            (width * 0.7, height * 0.3, 90, "planet1.png"),
            (width * 0.3, height * 0.5, 100, "planet2.png"),  
            (width * 0.6, height * 0.7, 80, "planet3.png"),
        ]
        
        for px, py, size, planet_name in planet_positions:
            try:
                planet_img = pygame.image.load(f"./asset/image/{planet_name}")
                planet_img = pygame.transform.scale(planet_img, (size, size))
                
                # Planet glow
                glow_surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
                glow_color = (100, 150, 200, 30)
                pygame.draw.circle(glow_surf, glow_color, (size//2 + 10, size//2 + 10), size//2 + 10)
                screen.blit(glow_surf, (px - size//2 - 10, py - size//2 - 10))
                
                planet_rect = planet_img.get_rect(center=(px, py))
                screen.blit(planet_img, planet_rect)
            except:
                colors = [(255,100,100), (100,255,100), (100,100,255)]
                color = colors[len(planet_name) % len(colors)]
                pygame.draw.circle(screen, color, (int(px), int(py)), size//2)

        # 4. Spaceship stopped at final position with dialogue
        final_ship_y = center[1] - 120
        spaceship_x = center[0]
        spaceship_y = final_ship_y + 3 * math.sin(dialogue_frame * 0.08)  # Gentle hover only
        
        try:
            from spaceship import load_spaceship_image, spaceship_rotated_images
            load_spaceship_image()
            
            # Make spaceship larger during dialogue phase
            ship_img = spaceship_rotated_images.get("up", spaceship_rotated_images[None])
            # Scale up the spaceship for dialogue phase
            larger_size = int(PLAYER_RADIUS * 5)  # Bigger than normal (was PLAYER_RADIUS * 4)
            ship_img = pygame.transform.scale(ship_img, (larger_size, larger_size))
            ship_rect = ship_img.get_rect(center=(spaceship_x, spaceship_y))
            
            # Enhanced ship glow for dialogue phase
            glow_surf = pygame.Surface((ship_rect.width + 30, ship_rect.height + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (150, 200, 255, 80), glow_surf.get_rect())
            screen.blit(glow_surf, (ship_rect.x - 15, ship_rect.y - 15))
            
            screen.blit(ship_img, ship_rect)
        except:
            # Fallback - also larger
            pygame.draw.circle(screen, (100, 200, 255), (int(spaceship_x), int(spaceship_y)), 16)  # Increased from 12 to 16

        # 5. Speech bubble with dialogue (Vietnamese - simplified if font issues)
        bubble_messages = [
            "Chinh phục thành công!",
            "Ngân hà đã an toàn!",
            "Sẵn sàng phiêu lưu mới!"
        ]
        
        # Show message based on dialogue_frame
        if dialogue_frame < 35:
            message = bubble_messages[0]
        elif dialogue_frame < 70:
            message = bubble_messages[1] 
        else:
            message = bubble_messages[2]
        
        # Speech bubble position (above spaceship)
        bubble_x = int(spaceship_x)
        bubble_y = int(spaceship_y) - 60
        
        # Create speech bubble (larger for Vietnamese text)
        try:
            # Try to use a font that supports Vietnamese characters better
            bubble_font = pygame.font.SysFont("Times New Roman", 16, bold=False)
        except:
            try:
                # Fallback to another common font
                bubble_font = pygame.font.SysFont("Calibri", 16, bold=False)
            except:
                # Final fallback
                bubble_font = pygame.font.Font(None, 20)  # Default pygame font
        
        text_surface = bubble_font.render(message, True, (50, 50, 100))
        text_rect = text_surface.get_rect()
        
        # Bubble background (wider for Vietnamese)
        bubble_width = text_rect.width + 24  # Extra width for Vietnamese text
        bubble_height = text_rect.height + 18
        bubble_rect = pygame.Rect(bubble_x - bubble_width//2, bubble_y - bubble_height//2, 
                                bubble_width, bubble_height)
        
        # Draw bubble shadow
        shadow_rect = bubble_rect.move(2, 2)
        pygame.draw.ellipse(screen, (0, 0, 0, 80), shadow_rect)
        
        # Draw bubble
        pygame.draw.ellipse(screen, (240, 240, 255), bubble_rect)
        pygame.draw.ellipse(screen, (150, 150, 200), bubble_rect, 2)
        
        # Draw bubble tail (pointing to spaceship)
        tail_points = [
            (bubble_x - 8, bubble_y + bubble_height//2 - 2),
            (bubble_x + 8, bubble_y + bubble_height//2 - 2),
            (bubble_x, bubble_y + bubble_height//2 + 12)
        ]
        pygame.draw.polygon(screen, (240, 240, 255), tail_points)
        pygame.draw.polygon(screen, (150, 150, 200), tail_points, 2)
        
        # Draw text
        text_x = bubble_x - text_rect.width//2
        text_y = bubble_y - text_rect.height//2
        screen.blit(text_surface, (text_x, text_y))
        
        # Typing effect for each message
        message_start_frame = (dialogue_frame // 35) * 35  # Start of current message
        typing_frame = dialogue_frame - message_start_frame
        if typing_frame < 20:  # 20 frames to type each message
            typing_progress = typing_frame / 20.0
            chars_to_show = int(len(message) * typing_progress)
            if chars_to_show < len(message):
                # Add blinking cursor
                cursor_alpha = int(255 * abs(math.sin(dialogue_frame * 0.3)))
                cursor_surface = bubble_font.render("_", True, (100, 100, 150))
                cursor_surface.set_alpha(cursor_alpha)
                cursor_x = text_x + bubble_font.size(message[:chars_to_show])[0]
                screen.blit(cursor_surface, (cursor_x, text_y))

    else:  # PHASE 3: VICTORY DISPLAY (after frame 180)
        victory_frame = frame - 180  # Reset frame counter for victory phase
        
        # 3. Background cosmic effects (lighter than before)
        # Black hole in background
        black_hole_radius = 30 + 8 * math.sin(victory_frame * 0.05)
        pygame.draw.circle(screen, (0, 0, 0), center, int(black_hole_radius))
        
        for i in range(3):
            glow_radius = black_hole_radius + i * 10
            glow_alpha = max(15, 40 - i * 10)
            glow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (30, 20, 80, glow_alpha), center, int(glow_radius), 2)
            screen.blit(glow_surf, (0, 0))

        # Subtle energy rings
        for ring in range(2):
            ring_radius = 160 + ring * 60 + 10 * math.sin(victory_frame * 0.08 + ring)
            ring_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            alpha = max(8, 25 - ring * 8)
            color = (80 + ring * 20, 80 + ring * 20, 150, alpha)
            pygame.draw.circle(ring_surf, color, center, int(ring_radius), 1)
            screen.blit(ring_surf, (0, 0))

        # Few quantum particles
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            base_dist = random.uniform(200, 300)
            quantum_wave = 20 * math.sin(victory_frame * 0.1 + angle * 2)
            dist = base_dist + quantum_wave
            
            x = int(center[0] + math.cos(angle) * dist)
            y = int(center[1] + math.sin(angle) * dist)
            
            if 0 <= x < width and 0 <= y < height:
                quantum_alpha = int(40 * abs(math.sin(victory_frame * 0.2 + angle)))
                colors = [(120,180,255), (180,120,255), (120,255,180)]
                color = random.choice(colors)
                pygame.draw.circle(screen, (*color, quantum_alpha), (x, y), 1)

        # 4. Final spaceship position (smaller, at center top - moved higher)
        final_ship_y = center[1] - 120  # Moved up from -80 to -120
        try:
            from spaceship import load_spaceship_image, spaceship_rotated_images
            load_spaceship_image()
            
            # Victory celebration flight pattern - fly back and forth initially
            if victory_frame < 120:  # First 2 seconds - celebration flight
                # Side-to-side flight pattern
                flight_progress = victory_frame / 120.0
                side_amplitude = 80 * (1 - flight_progress)  # Decrease amplitude over time
                side_movement = side_amplitude * math.sin(victory_frame * 0.15)
                
                # Gentle up-down movement
                hover_offset = 8 * math.sin(victory_frame * 0.12)
                
                ship_x = center[0] + side_movement
                ship_y = final_ship_y + hover_offset
                
                # Direction based on movement
                if victory_frame < 100:  # Active celebration phase
                    if math.sin(victory_frame * 0.15) > 0:
                        direction = "right"
                    else:
                        direction = "left"
                else:  # Settling down phase
                    direction = "up"
            else:  # After celebration - gentle hovering
                # Gentle hovering motion only
                hover_offset = 3 * math.sin(victory_frame * 0.1)  # Slower and smaller
                ship_x = center[0]
                ship_y = final_ship_y + hover_offset
                direction = "up"
            
            ship_img = spaceship_rotated_images.get(direction, spaceship_rotated_images[None])
            # Normal size for victory display
            ship_rect = ship_img.get_rect(center=(ship_x, ship_y))
            
            # Ship glow
            glow_surf = pygame.Surface((ship_rect.width + 20, ship_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (150, 200, 255, 60), glow_surf.get_rect())
            screen.blit(glow_surf, (ship_rect.x - 10, ship_rect.y - 10))
            
            screen.blit(ship_img, ship_rect)
        except:
            # Fallback
            ship_x = center[0]
            if victory_frame < 120:
                side_movement = 80 * (1 - victory_frame/120.0) * math.sin(victory_frame * 0.15)
                ship_x += side_movement
            hover_offset = 5 * math.sin(victory_frame * 0.1)
            pygame.draw.circle(screen, (100, 200, 255), (int(ship_x), int(final_ship_y + hover_offset)), 12)

        # 5. VICTORY TEXT - appearing after spaceship settles
        if victory_frame > 30:  # Small delay after spaceship stops
            font_large = pygame.font.SysFont("Arial", 88, bold=True)
            
            # Text animation - fade in and scale up
            text_progress = min((victory_frame - 30) / 60.0, 1.0)  # 1 second fade in
            
            # Reduced scale pulsing - much gentler
            base_scale = 0.5 + text_progress * 0.5
            pulse_scale = 0.03 * math.sin(victory_frame * 0.08)  # Reduced from 0.1 to 0.03, slower frequency
            scale_pulse = base_scale + pulse_scale
            
            victory_text = font_large.render("VICTORY!", True, (255, 255, 200))
            cosmic_text = pygame.transform.rotozoom(victory_text, 0, scale_pulse)
            text_rect = cosmic_text.get_rect(center=(center[0], center[1] + 20))
            
            text_alpha = int(255 * text_progress)
            
            # Shadow background
            shadow_surf = pygame.Surface((text_rect.width + 80, text_rect.height + 80), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, int(120 * text_progress)), shadow_surf.get_rect())
            screen.blit(shadow_surf, (text_rect.x - 40, text_rect.y - 40))
            
            # Glow layers
            for i, (size_offset, color, alpha_mult) in enumerate([
                (60, (100, 200, 255), 0.4),
                (40, (200, 150, 255), 0.6), 
                (20, (255, 255, 255), 0.3)
            ]):
                glow = pygame.Surface((text_rect.width + size_offset, text_rect.height + size_offset), pygame.SRCALPHA)
                glow_alpha = int(255 * alpha_mult * text_progress)
                pygame.draw.ellipse(glow, (*color, glow_alpha), glow.get_rect())
                offset = size_offset // 2
                screen.blit(glow, (text_rect.x - offset, text_rect.y - offset))
            
            # Final text
            cosmic_text.set_alpha(text_alpha)
            screen.blit(cosmic_text, text_rect)

            # 6. Instruction text - appears after victory text is fully visible
            if text_progress >= 1.0:
                small_font = pygame.font.SysFont("Arial", 28, bold=False)
                restart_text = "Click anywhere or press RESTART button to play again"
                
                instruction_alpha = int(200 + 55 * math.sin(victory_frame * 0.12))
                
                # Text background
                text_bg = pygame.Surface((width, 40), pygame.SRCALPHA)
                text_bg.fill((0, 0, 0, 80))
                screen.blit(text_bg, (0, center[1] + 120))
                
                # Instruction text
                instruction_text = small_font.render(restart_text, True, (220, 220, 255))
                instruction_text.set_alpha(instruction_alpha)
                instruction_rect = instruction_text.get_rect(center=(center[0], center[1] + 140))
                screen.blit(instruction_text, instruction_rect)

def draw_move_count(screen, x, y, font, count):
    text_surf = render_text_with_outline(f"Moves: {count}", font, WHITE, BLACK, 1)
    screen.blit(text_surf, (x, y))

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
