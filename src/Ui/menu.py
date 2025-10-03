# -*- coding: utf-8 -*-
"""
MÔ TẢ:
- Lớp `MainMenu` quản lý và hiển thị menu chính của game Maze Paint.
- Bao gồm hiệu ứng nền động, tiêu đề, nút bấm tương tác, và hướng dẫn điều khiển.
CHỨC NĂNG:
- Khởi tạo, cập nhật, và vẽ giao diện menu chính.
- Xử lý sự kiện tương tác từ bàn phím và chuột.
PHỤ THUỘC:
- pygame, config, manager.font_manager, renderer.
"""
import pygame
import math
import random
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    HEADER_HEIGHT,
    MENU_TITLE_GLOW_SPEED,
    MENU_TITLE_GLOW_MAX,
    WHITE,
    BLACK,
    DARK_BLUE
)
from manager.font_manager import get_font_manager
from .renderer import draw_button
from manager.font_manager import font_small

class MainMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = (height + HEADER_HEIGHT) // 2  # Căn giữa menu, tính cả phần header
        
        self.frame = 0
        self.title_glow = 0
        
        self.selected_button = 0
        self.button_hover = [False, False, False]
        
        self.init_background_stars()
        self.cosmic_particles = []
        self.init_cosmic_particles()
        
        self.font_manager = get_font_manager()
    
    def init_fonts(self):
        """DEPRECATED: Hàm này không còn sử dụng, thay vào đó là font_manager."""
        pass
    
    def safe_render_text(self, text, font_size, color):
        """Render text an toàn với tiếng Việt bằng font_manager."""
        return self.font_manager.render_text(text, font_size, color)
    
    def init_background_stars(self):
        """Khởi tạo hiệu ứng các ngôi sao lấp lánh cho nền."""
        self.background_stars = []
        random.seed(12345)  # Dùng seed cố định để các ngôi sao luôn giống nhau
        for _ in range(150):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            twinkle_speed = random.uniform(0.01, 0.05)
            self.background_stars.append({
                'x': x, 'y': y, 'size': size,
                'brightness': brightness, 'base_brightness': brightness,
                'twinkle_speed': twinkle_speed, 'twinkle_phase': random.uniform(0, 6.28)
            })
    
    def init_cosmic_particles(self):
        """Khởi tạo hiệu ứng các hạt vũ trụ di chuyển."""
        random.seed(54321)
        for _ in range(30):
            self.cosmic_particles.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(-0.3, 0.3),
                'size': random.randint(1, 2),
                'color_phase': random.uniform(0, 6.28),
                'alpha': random.randint(50, 150)
            })
    
    def update(self):
        """Cập nhật trạng thái của các hiệu ứng động."""
        self.frame += 1
        
        self.title_glow = MENU_TITLE_GLOW_MAX * math.sin(self.frame * MENU_TITLE_GLOW_SPEED)
        
        # Cập nhật hiệu ứng lấp lánh của sao
        for star in self.background_stars:
            star['twinkle_phase'] += star['twinkle_speed']
            star['brightness'] = star['base_brightness'] + int(20 * math.sin(star['twinkle_phase']))
            star['brightness'] = max(50, min(255, star['brightness']))
        
        # Cập nhật vị trí các hạt vũ trụ
        for particle in self.cosmic_particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['color_phase'] += 0.02
            
            # Nếu ra khỏi màn hình thì cho xuất hiện lại ở cạnh đối diện
            if particle['x'] < 0: particle['x'] = self.width
            elif particle['x'] > self.width: particle['x'] = 0
            if particle['y'] < 0: particle['y'] = self.height
            elif particle['y'] > self.height: particle['y'] = 0
    
    def handle_event(self, event):
        """Xử lý input từ bàn phím và chuột."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_button = (self.selected_button - 1) % 3
                return "BUTTON_HOVER"
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_button = (self.selected_button + 1) % 3
                return "BUTTON_HOVER"
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected_button == 0: return "PLAY_GAME"
                elif self.selected_button == 1: return "SELECT_SPACESHIP"
                elif self.selected_button == 2: return "EXIT_GAME"
            elif event.key == pygame.K_ESCAPE:
                return "EXIT_GAME"
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            button_rects = self.get_button_rects()
            old_selected = self.selected_button
            for i, rect in enumerate(button_rects):
                self.button_hover[i] = rect.collidepoint(mouse_x, mouse_y)
                if self.button_hover[i]:
                    self.selected_button = i
            if old_selected != self.selected_button:
                return "BUTTON_HOVER"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Chuột trái
                mouse_x, mouse_y = pygame.mouse.get_pos()
                button_rects = self.get_button_rects()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if i == 0: return "PLAY_GAME"
                        elif i == 1: return "SELECT_SPACESHIP"
                        elif i == 2: return "EXIT_GAME"
        
        return None
    
    def get_button_rects(self):
        """Tính toán và trả về danh sách Rect của các nút bấm."""
        button_rects = []
        button_width = 350
        button_height = 50
        
        for i in range(3):
            y = self.center_y + i * 70 + 20
            rect = pygame.Rect(
                self.center_x - button_width // 2,
                y - button_height // 2,
                button_width,
                button_height
            )
            button_rects.append(rect)
        
        return button_rects
    
    def draw(self, screen):
        """Vẽ toàn bộ giao diện menu chính lên màn hình."""
        # 1. Nền gradient chủ đề không gian (vẽ từ dưới header)
        for y in range(HEADER_HEIGHT, self.height):
            ratio = (y - HEADER_HEIGHT) / (self.height - HEADER_HEIGHT)
            r = int(5 + ratio * 10)
            g = int(5 + ratio * 15) 
            b = int(20 + ratio * 35)
            color = (r, g, b)
            pygame.draw.line(screen, color, (0, y), (self.width, y))
        
        # 2. Các ngôi sao nền
        for star in self.background_stars:
            brightness = star['brightness']
            star_color = (brightness, brightness, min(255, brightness + 30))
            pygame.draw.circle(screen, star_color, (int(star['x']), int(star['y'])), star['size'])
        
        # 3. Các hạt vũ trụ
        for particle in self.cosmic_particles:
            color_offset = math.sin(particle['color_phase'])
            r = int(80 + 40 * color_offset)
            g = int(120 + 40 * math.sin(particle['color_phase'] + 2))
            b = int(180 + 40 * math.sin(particle['color_phase'] + 4))
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), particle['size'])
        
        # 4. Tiêu đề game với hiệu ứng phát sáng
        title_text = "MAZE PAINT"
        glow_value = max(0, min(255, int(self.title_glow + 120)))
        title_color = (glow_value, min(255, glow_value + 40), 255)
        
        title_surface = self.font_manager.render_text(title_text, 80, title_color, bold=True, shadow=True, glow=True)
        if title_surface:
            title_rect = title_surface.get_rect(center=(self.center_x, self.center_y - 120))
            screen.blit(title_surface, title_rect)
        
        # 5. Phụ đề
        subtitle_text = "Trò chơi phiêu lưu không gian"
        subtitle_color = (120, 160, 240)
        subtitle_surface = self.font_manager.render_text(subtitle_text, 20, subtitle_color, shadow=True)
        if subtitle_surface:
            subtitle_rect = subtitle_surface.get_rect(center=(self.center_x, self.center_y - 60))
            screen.blit(subtitle_surface, subtitle_rect)
        
        # 6. Các nút bấm trong menu
        button_texts = ["CHƠI NGAY", "CHỌN PHI THUYỀN", "THOÁT"]
        button_rects = self.get_button_rects()
        
        for i, (rect, text) in enumerate(zip(button_rects, button_texts)):
            is_selected = (i == self.selected_button)
            is_hovered = self.button_hover[i]
            
            if is_selected or is_hovered:
                # Nút được chọn hoặc hover
                glow_color = (60, 100, 180, 100)
                glow_surf = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color, (4, 4, rect.width, rect.height), border_radius=12)
                screen.blit(glow_surf, (rect.x - 4, rect.y - 4))
                
                button_color = (40, 70, 130, 150)
                button_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(button_surf, button_color, (0, 0, rect.width, rect.height), border_radius=8)
                screen.blit(button_surf, rect.topleft)
                
                border_color = (80, 120, 220)
                pygame.draw.rect(screen, border_color, rect, width=2, border_radius=8)
                
                text_color = (255, 255, 255)
            else:
                # Nút ở trạng thái bình thường
                button_color = (25, 45, 80, 100)
                button_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(button_surf, button_color, (0, 0, rect.width, rect.height), border_radius=8)
                screen.blit(button_surf, rect.topleft)
                
                border_color = (50, 80, 120)
                pygame.draw.rect(screen, border_color, rect, width=1, border_radius=8)
                
                text_color = (160, 180, 220)
            
            is_hover = is_selected or is_hovered
            text_surface = self.font_manager.render_text(text, 36, text_color, bold=True, outline=is_hover, glow=is_hover)
            if text_surface:
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)
        
        # 7. Hướng dẫn điều khiển
        hint_text = "↑↓ Di chuyển • ENTER/Space Chọn • ESC Thoát"
        hint_color = (100, 130, 180)
        hint_surface = self.font_manager.render_text(hint_text, 18, hint_color, shadow=True)
        if hint_surface:
            hint_rect = hint_surface.get_rect(center=(self.center_x, self.height - 25))
            screen.blit(hint_surface, hint_rect)
    
    def draw_menu_button(self, screen, label="Menu"):
        """Vẽ nút "Menu" khi đang ở trong màn hình chơi game."""
        margin_x = 20
        margin_y = 65
        button_width = 120
        button_height = 40
        button_rect = pygame.Rect(self.width - margin_x - button_width, margin_y, button_width, button_height)
        
        draw_button(screen, font_small, button_rect, DARK_BLUE, label, "info")
        
        return button_rect

    def handle_menu_button_event(self, event, button_rect):
        """Xử lý sự kiện cho nút "Menu" khi đang ở trong màn hình chơi game."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and button_rect and button_rect.collidepoint(event.pos):
            return "BACK_TO_MENU"
        return None