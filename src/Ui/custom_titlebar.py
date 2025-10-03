import pygame
import math
from manager.font_manager import get_font_manager

def create_gradient_surface(width, height, color1, color2, vertical=False):
    """Tạo surface với gradient đẹp"""
    surface = pygame.Surface((width, height))
    
    if vertical:
        for y in range(height):
            ratio = y / height
            color = [
                int(color1[i] * (1 - ratio) + color2[i] * ratio)
                for i in range(3)
            ]
            pygame.draw.line(surface, color, (0, y), (width, y))
    else:
        for x in range(width):
            ratio = x / width
            color = [
                int(color1[i] * (1 - ratio) + color2[i] * ratio)
                for i in range(3)
            ]
            pygame.draw.line(surface, color, (x, 0), (x, height))
    
    return surface

def draw_custom_titlebar(screen, width, height, title, font, frame=0):
    """Vẽ custom title bar đẹp với hiệu ứng"""
    
    # Tạo gradient background cho title bar
    title_height = 35
    
    # Gradient colors (dark blue to light blue)
    color1 = (15, 25, 45)    # Dark navy
    color2 = (45, 80, 120)   # Light blue
    color3 = (25, 40, 70)    # Mid blue
    
    # Tạo gradient surface
    gradient_surf = create_gradient_surface(width, title_height, color1, color2)
    
    # Thêm hiệu ứng glow
    glow_surf = pygame.Surface((width, title_height), pygame.SRCALPHA)
    
    # Animated glow effect
    glow_alpha = int(50 + 30 * math.sin(frame * 0.02))
    glow_color = (100, 150, 255, glow_alpha)
    
    # Draw glow bars
    pygame.draw.rect(glow_surf, glow_color, (0, 0, width, 2))
    pygame.draw.rect(glow_surf, glow_color, (0, title_height-2, width, 2))
    
    # Draw gradient
    screen.blit(gradient_surf, (0, 0))
    screen.blit(glow_surf, (0, 0))
    
    # Draw title text với hiệu ứng
    text_color = (220, 240, 255)
    shadow_color = (10, 20, 40)
    
    # Render text
    text_surf = font.render(title, True, text_color)
    shadow_surf = font.render(title, True, shadow_color)
    
    # Center text
    text_x = (width - text_surf.get_width()) // 2
    text_y = (title_height - text_surf.get_height()) // 2
    
    # Draw shadow
    screen.blit(shadow_surf, (text_x + 1, text_y + 1))
    # Draw main text
    screen.blit(text_surf, (text_x, text_y))
    
    # Draw decorative elements
    # Left decoration
    pygame.draw.circle(screen, (100, 150, 255), (20, title_height//2), 4)
    pygame.draw.circle(screen, (150, 200, 255), (20, title_height//2), 2)
    
    # Right decoration
    pygame.draw.circle(screen, (100, 150, 255), (width-20, title_height//2), 4)
    pygame.draw.circle(screen, (150, 200, 255), (width-20, title_height//2), 2)
    
    return title_height

def draw_modern_titlebar(screen, width, height, title, font, frame=0):
    """Vẽ title bar hiện đại với neon effect, decorative graphics và text trái"""
    
    title_height = 45  # Height cho title bar
    font_manager = get_font_manager()
    
    # Background với gradient space theme đẹp hơn
    bg_color1 = (5, 10, 25)      # Đậm hơn
    bg_color2 = (15, 30, 60)     # Xanh space đẹp
    bg_color3 = (25, 45, 80)     # Highlight
    
    # Tạo gradient 3 màu phức tạp hơn
    gradient_surf = pygame.Surface((width, title_height))
    for y in range(title_height):
        if y < title_height // 2:
            ratio = y / (title_height // 2)
            color = [
                int(bg_color1[i] * (1 - ratio) + bg_color2[i] * ratio)
                for i in range(3)
            ]
        else:
            ratio = (y - title_height // 2) / (title_height // 2)
            color = [
                int(bg_color2[i] * (1 - ratio) + bg_color3[i] * ratio)
                for i in range(3)
            ]
        pygame.draw.line(gradient_surf, color, (0, y), (width, y))
    
    screen.blit(gradient_surf, (0, 0))
    
    # Animated neon border với nhiều màu
    neon_alpha = int(80 + 40 * math.sin(frame * 0.04))
    neon_color_cyan = (0, 255, 255, neon_alpha)
    neon_color_purple = (255, 0, 255, neon_alpha // 2)
    
    # Top neon lines - 2 màu
    for i in range(2):
        alpha_cyan = neon_alpha - i * 40
        alpha_purple = (neon_alpha // 2) - i * 20
        if alpha_cyan > 0:
            neon_surf = pygame.Surface((width, 1), pygame.SRCALPHA)
            neon_surf.fill((0, 255, 255, alpha_cyan))
            screen.blit(neon_surf, (0, i))
        if alpha_purple > 0:
            neon_surf2 = pygame.Surface((width, 1), pygame.SRCALPHA)
            neon_surf2.fill((255, 0, 255, alpha_purple))
            screen.blit(neon_surf2, (0, i + 1))
    
    # Bottom neon lines
    for i in range(2):
        alpha_cyan = neon_alpha - i * 40
        if alpha_cyan > 0:
            neon_surf = pygame.Surface((width, 1), pygame.SRCALPHA)
            neon_surf.fill((0, 255, 255, alpha_cyan))
            screen.blit(neon_surf, (0, title_height - 1 - i))
    
    # Vẽ decorative elements - circuit pattern bên trái
    circuit_color = (100, 200, 255, 150)
    circuit_start_x = 15
    circuit_y = title_height // 2
    
    # Circuit lines (animated)
    pulse = int(50 + 30 * math.sin(frame * 0.1))
    circuit_surf = pygame.Surface((60, title_height), pygame.SRCALPHA)
    
    # Horizontal main line
    pygame.draw.line(circuit_surf, (*circuit_color[:3], pulse), (5, circuit_y - 8), (55, circuit_y - 8), 2)
    # Vertical connectors
    pygame.draw.line(circuit_surf, (*circuit_color[:3], pulse + 20), (10, circuit_y - 12), (10, circuit_y - 4), 2)
    pygame.draw.line(circuit_surf, (*circuit_color[:3], pulse + 30), (25, circuit_y - 12), (25, circuit_y - 4), 2)
    pygame.draw.line(circuit_surf, (*circuit_color[:3], pulse + 10), (40, circuit_y - 12), (40, circuit_y - 4), 2)
    
    # Circuit nodes (pulsing)
    node_size = 2 + int(math.sin(frame * 0.08) * 1)
    pygame.draw.circle(circuit_surf, (0, 255, 255, pulse + 50), (10, circuit_y - 8), node_size)
    pygame.draw.circle(circuit_surf, (255, 100, 255, pulse + 30), (25, circuit_y - 8), node_size)
    pygame.draw.circle(circuit_surf, (100, 255, 100, pulse + 40), (40, circuit_y - 8), node_size)
    
    screen.blit(circuit_surf, (circuit_start_x, 0))
    
    # Nút X đóng ở góc phải
    close_button_size = 30
    close_margin = 8
    close_x = width - close_button_size - close_margin
    close_y = (title_height - close_button_size) // 2
    
    # Background nút X với hiệu ứng hover
    close_bg_alpha = int(120 + 30 * math.sin(frame * 0.05))
    close_bg_color = (80, 20, 20, close_bg_alpha)
    close_border_color = (255, 100, 100)
    
    # Vẽ background nút X
    close_surf = pygame.Surface((close_button_size, close_button_size), pygame.SRCALPHA)
    pygame.draw.rect(close_surf, close_bg_color, (0, 0, close_button_size, close_button_size))
    pygame.draw.rect(close_surf, close_border_color, (0, 0, close_button_size, close_button_size), 2)
    screen.blit(close_surf, (close_x, close_y))
    
    # Vẽ X
    x_color = (255, 150, 150)
    x_margin = 8
    pygame.draw.line(screen, x_color, 
                    (close_x + x_margin, close_y + x_margin), 
                    (close_x + close_button_size - x_margin, close_y + close_button_size - x_margin), 3)
    pygame.draw.line(screen, x_color, 
                    (close_x + x_margin, close_y + close_button_size - x_margin), 
                    (close_x + close_button_size - x_margin, close_y + x_margin), 3)
    
    # Vẽ decorative hexagon pattern bên phải nút X
    hex_x = close_x - 80
    hex_y = title_height // 2
    hex_size = 8
    hex_color = (150, 200, 255, 100)
    
    # Draw hexagon
    hex_points = []
    for i in range(6):
        angle = i * 60 * math.pi / 180
        x = hex_x + hex_size * math.cos(angle + frame * 0.02)
        y = hex_y + hex_size * math.sin(angle + frame * 0.02)
        hex_points.append((x, y))
    
    if len(hex_points) >= 3:
        pygame.draw.polygon(screen, hex_color[:3], hex_points, 2)
    
    # Title text căn trái với font manager hỗ trợ tiếng Việt
    title_font_size = 16  # Tăng font size để rõ hơn
    
    # Render text với màu sắc tương phản cao
    text_color = (255, 255, 255)  # Màu trắng tinh khiết để rõ nét
    glow_color = (120, 180, 255)  # Màu glow nhẹ hơn
    
    try:
        # Sử dụng font manager để render tiếng Việt
        title_surf = font_manager.render_text(title, title_font_size, text_color)
    except:
        # Fallback to default font nếu font manager lỗi
        fallback_font = pygame.font.Font(None, title_font_size)
        title_surf = fallback_font.render(title, True, text_color)
    
    # Tính toán vị trí text (căn trái với margin, tránh circuit pattern)
    text_margin = 85  # Đủ khoảng cách để tránh circuit pattern
    text_x = text_margin
    text_y = (title_height - title_surf.get_height()) // 2
    
    # Kiểm tra text có bị che bởi decorative elements không
    max_text_width = hex_x - text_x - 20  # Để lại khoảng cách 20px trước hexagon
    if title_surf.get_width() > max_text_width:
        # Cắt text nếu quá dài
        title_words = title.split()
        truncated_title = ""
        for word in title_words:
            test_title = truncated_title + word + " "
            try:
                test_surf = font_manager.render_text(test_title, title_font_size, text_color)
            except:
                test_surf = fallback_font.render(test_title, True, text_color)
            
            if test_surf.get_width() <= max_text_width - 30:  # -30 for "..."
                truncated_title = test_title
            else:
                break
        
        if len(truncated_title.strip()) > 0:
            title = truncated_title.strip() + "..."
        else:
            # Fallback: cắt theo ký tự
            while title_surf.get_width() > max_text_width and len(title) > 10:
                title = title[:-4] + "..."
                try:
                    title_surf = font_manager.render_text(title, title_font_size, text_color)
                except:
                    title_surf = fallback_font.render(title, True, text_color)
        
        # Re-render truncated title
        try:
            title_surf = font_manager.render_text(title, title_font_size, text_color)
        except:
            title_surf = fallback_font.render(title, True, text_color)
    
    # Vẽ text outline để tăng độ rõ nét (vẽ text đen ở xung quanh trước)
    outline_color = (0, 0, 0)  # Màu đen cho outline
    outline_offset = 1
    
    # Vẽ outline ở 8 hướng
    for dx in [-outline_offset, 0, outline_offset]:
        for dy in [-outline_offset, 0, outline_offset]:
            if dx != 0 or dy != 0:  # Không vẽ ở center
                try:
                    outline_surf = font_manager.render_text(title, title_font_size, outline_color)
                except:
                    outline_surf = fallback_font.render(title, True, outline_color)
                screen.blit(outline_surf, (text_x + dx, text_y + dy))
    
    # Vẽ subtle glow effect (chỉ 1 layer nhẹ)
    glow_alpha = 30
    try:
        glow_surf = font_manager.render_text(title, title_font_size, (*glow_color[:3], glow_alpha))
    except:
        fallback_font = pygame.font.Font(None, title_font_size)
        glow_surf = fallback_font.render(title, True, glow_color)
        # Tạo alpha surface cho glow effect nhẹ
        glow_alpha_surf = pygame.Surface(glow_surf.get_size(), pygame.SRCALPHA)
        glow_alpha_surf.fill((*glow_color, glow_alpha))
        glow_alpha_surf.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        glow_surf = glow_alpha_surf
    
    # Vẽ glow nhẹ chỉ ở 4 hướng chính
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        screen.blit(glow_surf, (text_x + dx, text_y + dy))
    
    # Vẽ main text (trắng, rõ nét)
    screen.blit(title_surf, (text_x, text_y))
    
    # Return both height and close button rect for click detection
    close_button_rect = pygame.Rect(close_x, close_y, close_button_size, close_button_size)
    return title_height, close_button_rect