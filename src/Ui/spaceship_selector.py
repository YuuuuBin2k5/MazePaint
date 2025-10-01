# -*- coding: utf-8 -*-
"""Menu chọn phi thuyền.

Di chuyển các imports an toàn lên đầu module; giữ lazy import chỉ khi cần.
"""
import pygame
import math
import os
import random
from config import *
from font_manager import get_font_manager
from config import SELECTED_SPACESHIP, set_selected_spaceship

class SpaceshipSelector:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        
        # Animation
        self.frame = 0
        
        # Spaceship data
        self.spaceships = []
        self.selected_ship = 0
        self.load_spaceships()
        
        # Grid layout - điều chỉnh lại cho phi thuyền nhỏ hơn
        self.ships_per_row = 3
        self.ship_spacing = 130  # Giảm lại khoảng cách do phi thuyền nhỏ hơn
        self.ship_size = 60      # Giảm kích thước vùng hiển thị
        
        # Background effects
        self.init_background()
        
        # Font manager cho tiếng Việt
        self.font_manager = get_font_manager()
    
    def init_fonts(self):
        """Khởi tạo fonts với hỗ trợ tiếng Việt - DEPRECATED"""
        # Giữ lại để tương thích, sử dụng font_manager thay thế
        pass
    
    def safe_render_text(self, text, font_size, color):
        """Render text an toàn với tiếng Việt - sử dụng font_manager"""
        return self.font_manager.render_text(text, font_size, color)
    
    def load_spaceships(self):
        """Tải tất cả phi thuyền từ thư mục"""
        spaceship_path = "./asset/image/spaceship/"
        
        # Thông tin mô tả cho từng phi thuyền
        ship_descriptions = {
            "ship_1.svg": "Explorer - Phi thuyền thám hiểm cơ bản",
            "ship_2.svg": "Fighter - Phi thuyền chiến đấu nhanh",
            "ship_3.svg": "Cruiser - Phi thuyền tuần tra mạnh mẽ",
            "ship_4.svg": "Destroyer - Phi thuyền hủy diệt hạng nặng",
            "ship_5.svg": "Interceptor - Phi thuyền đánh chặn tốc độ cao",
            "ship_6.svg": "Bomber - Phi thuyền ném bom tầm xa",
            "ship_7.svg": "Scout - Phi thuyền trinh sát nhẹ",
            "ship_8.svg": "Carrier - Phi thuyền chở máy bay",
            "ship_9.svg": "Dreadnought - Phi thuyền chiến hạm siêu nặng"
        }
        
        if os.path.exists(spaceship_path):
            svg_files = [f for f in os.listdir(spaceship_path) if f.endswith('.svg')]
            svg_files.sort()  # Sắp xếp theo tên
            
            for i, filename in enumerate(svg_files, 1):
                filepath = os.path.join(spaceship_path, filename)
                try:
                    # Thử load SVG, nếu không được thì tạo placeholder
                    ship_image = self.load_or_create_spaceship(filepath, i)
                    self.spaceships.append({
                        'image': ship_image,
                        'name': f"Phi thuyền {i}",
                        'description': ship_descriptions.get(filename, "Phi thuyền bí ẩn"),
                        'filename': filename,
                        'id': i - 1  # Convert to 0-based (0-8) để match với SELECTED_SPACESHIP
                    })
                except Exception as e:
                    print(f"Could not load {filename}: {e}")
                    # Tạo placeholder nếu không load được
                    ship_image = self.create_spaceship_placeholder(i)
                    self.spaceships.append({
                        'image': ship_image,
                        'name': f"Phi thuyền {i}",
                        'description': f"Phi thuyền số {i}",
                        'filename': filename,
                        'id': i - 1  # Convert to 0-based để match với SELECTED_SPACESHIP
                    })
        
        # Tạo phi thuyền mặc định nếu không tải được gì
        if not self.spaceships:
            for i in range(9):
                ship_image = self.create_spaceship_placeholder(i + 1)
                self.spaceships.append({
                    'image': ship_image,
                    'name': f"Phi thuyền {i + 1}",
                    'description': f"Phi thuyền số {i + 1}",
                    'filename': f"ship_{i + 1}.svg",
                    'id': i  # 0-based ID (0-8) để match với SELECTED_SPACESHIP
                })
    
    def load_or_create_spaceship(self, filepath, ship_id):
        """Load SVG hoặc tạo placeholder đẹp - thử load SVG thật trước"""
        try:
            # Thử load SVG bằng pygame (giống như trong spaceship.py)
            image = pygame.image.load(filepath)
            # Scale xuống kích thước phù hợp cho selector
            scaled_image = pygame.transform.scale(image, (50, 50))
            return scaled_image
        except Exception as e:
            print(f"Could not load {filepath}: {e}, using placeholder")
            # Tạo placeholder nếu không load được SVG
            return self.create_spaceship_placeholder(ship_id)
    
    def create_spaceship_placeholder(self, ship_id):
        """Tạo hình phi thuyền placeholder đẹp hơn với kích thước cố định nhỏ"""
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)  # Giảm kích thước xuống để phù hợp
        
        # Màu sắc theo ID
        colors = [
            (100, 150, 255), (255, 100, 100), (100, 255, 100),
            (255, 255, 100), (255, 100, 255), (100, 255, 255),
            (255, 150, 100), (150, 100, 255), (200, 200, 200)
        ]
        
        # Vẽ phi thuyền với nhiều chi tiết hơn - scale nhỏ lại cho 50x50
        color = colors[(ship_id - 1) % len(colors)]
        
        # Body chính - scale nhỏ lại
        body_points = self.get_spaceship_shape(ship_id)
        pygame.draw.polygon(surface, color, body_points)
        
        # Engine glow - scale nhỏ lại
        engine_color = tuple(min(255, c + 60) for c in color)
        pygame.draw.circle(surface, engine_color, (25, 40), 4)  # Giảm kích thước cho 50x50
        pygame.draw.circle(surface, (255, 255, 255), (25, 40), 2)  # Giảm kích thước cho 50x50
        
        # Thêm chi tiết theo từng loại phi thuyền
        self.add_ship_details(surface, ship_id, color)
        
        return surface
    
    def get_spaceship_shape(self, ship_id):
        """Lấy hình dạng phi thuyền - điều chỉnh kích thước cho canvas 50x50"""
        # Tất cả shapes được scale để vừa trong canvas 50x50
        shapes = [
            # Ship 1: Triangle basic
            [(25, 8), (35, 35), (25, 28), (15, 35)],
            # Ship 2: Arrow fighter  
            [(25, 5), (40, 32), (25, 25), (10, 32)],
            # Ship 3: Diamond cruiser
            [(25, 6), (38, 25), (25, 44), (12, 25)],
            # Ship 4: Heavy destroyer
            [(25, 10), (33, 40), (25, 35), (17, 40)],
            # Ship 5: Sleek interceptor
            [(25, 4), (42, 28), (25, 22), (8, 28)],
            # Ship 6: Bomber
            [(25, 12), (32, 38), (25, 33), (18, 38)],
            # Ship 7: Scout
            [(25, 7), (36, 30), (25, 26), (14, 30)],
            # Ship 8: Carrier
            [(25, 15), (30, 40), (25, 37), (20, 40)],
            # Ship 9: Dreadnought
            [(25, 18), (28, 42), (25, 39), (22, 42)]
        ]
        return shapes[(ship_id - 1) % len(shapes)]
    
    def add_ship_details(self, surface, ship_id, color):
        """Thêm chi tiết cho từng loại phi thuyền - điều chỉnh cho canvas 50x50"""
        wing_color = tuple(c // 2 for c in color)
        detail_color = tuple(min(255, c + 80) for c in color)
        
        # Wings - điều chỉnh vị trí để phù hợp với canvas 50x50
        if ship_id % 3 == 1:
            pygame.draw.polygon(surface, wing_color, [(10, 20), (18, 25), (15, 30)])
            pygame.draw.polygon(surface, wing_color, [(40, 20), (32, 25), (35, 30)])
        
        if ship_id % 2 == 0:  # Các phi thuyền chẵn
            pygame.draw.circle(surface, detail_color, (25, 18), 2)  # Giảm kích thước cho 50x50
            pygame.draw.circle(surface, (200, 200, 255), (25, 18), 1)
        
        # Thêm số ID nhỏ ở góc
        font = pygame.font.Font(None, 14)  # Giảm font size
        id_text = font.render(str(ship_id), True, (255, 255, 255))
        surface.blit(id_text, (2, 2))
        
        # Thêm antenna cho một số phi thuyền
        if ship_id in [3, 6, 9]:
            pygame.draw.line(surface, detail_color, (25, 5), (25, 2), 1)  # Điều chỉnh vị trí cho 50x50
            pygame.draw.circle(surface, (255, 200, 100), (25, 2), 1)
    
    def get_ship_color(self, ship_id):
        """Lấy màu cho phi thuyền"""
        colors = [
            (100, 150, 255), (255, 100, 100), (100, 255, 100),
            (255, 255, 100), (255, 100, 255), (100, 255, 255),
            (255, 150, 100), (150, 100, 255), (200, 200, 200)
        ]
        return colors[(ship_id - 1) % len(colors)]
    
    def init_background(self):
        """Khởi tạo background"""
        # random đã được import ở module-level
        self.background_stars = []
        random.seed(67890)
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 2)
            brightness = random.randint(80, 200)
            self.background_stars.append({
                'x': x, 'y': y, 'size': size, 'brightness': brightness
            })
    
    def update(self):
        """Cập nhật animation"""
        self.frame += 1
    
    def handle_event(self, event):
        """Xử lý input events"""
        # Không cần global declaration nữa vì dùng setter function
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if self.selected_ship > 0:
                    self.selected_ship -= 1
                    return "SHIP_CHANGED"
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if self.selected_ship < len(self.spaceships) - 1:
                    self.selected_ship += 1
                    return "SHIP_CHANGED"
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                if self.selected_ship >= self.ships_per_row:
                    self.selected_ship -= self.ships_per_row
                    return "SHIP_CHANGED"
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if self.selected_ship < len(self.spaceships) - self.ships_per_row:
                    self.selected_ship += self.ships_per_row
                    return "SHIP_CHANGED"
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Chọn phi thuyền
                ship_id = self.spaceships[self.selected_ship]['id']
                set_selected_spaceship(ship_id)
                return "SHIP_SELECTED"
            elif event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
        
        # Kiểm tra click vào phi thuyền
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Check back button
                back_rect = pygame.Rect(20, 20, 100, 30)
                if back_rect.collidepoint(mouse_x, mouse_y):
                    return "BACK_TO_MENU"
                
                # Check spaceship grid
                grid_rects = self.get_ship_grid_rects()
                for i, rect in enumerate(grid_rects):
                    if rect.collidepoint(mouse_x, mouse_y) and i < len(self.spaceships):
                        if i == self.selected_ship:
                            # Double click to select
                            ship_id = self.spaceships[i]['id']
                            set_selected_spaceship(ship_id)
                            return "SHIP_SELECTED"
                        else:
                            self.selected_ship = i
                            return "SHIP_CHANGED"
        
        elif event.type == pygame.MOUSEMOTION:
            # Hover effect
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_rects = self.get_ship_grid_rects()
            for i, rect in enumerate(grid_rects):
                if rect.collidepoint(mouse_x, mouse_y) and i < len(self.spaceships):
                    if i != self.selected_ship:
                        self.selected_ship = i
                        return "SHIP_CHANGED"
        
        return None
    
    def get_ship_grid_rects(self):
        """Lấy rectangles của grid phi thuyền"""
        rects = []
        start_x = self.center_x - (self.ships_per_row * self.ship_spacing) // 2 + self.ship_spacing // 2
        start_y = self.center_y - 60  # Vị trí khởi đầu
        
        for i in range(len(self.spaceships)):
            row = i // self.ships_per_row
            col = i % self.ships_per_row
            x = start_x + col * self.ship_spacing - self.ship_size // 2
            y = start_y + row * 100 - self.ship_size // 2  # Giảm khoảng cách dọc
            rects.append(pygame.Rect(x, y, self.ship_size, self.ship_size))
        
        return rects
    
    def draw(self, screen):
        """Vẽ spaceship selector"""
        # 1. Background gradient
        for y in range(self.height):
            ratio = y / self.height
            r = int(8 + ratio * 12)
            g = int(8 + ratio * 18) 
            b = int(25 + ratio * 30)
            color = (r, g, b)
            pygame.draw.line(screen, color, (0, y), (self.width, y))
        
        # 2. Background stars
        for star in self.background_stars:
            brightness = star['brightness']
            color = (brightness, brightness, min(255, brightness + 20))
            pygame.draw.circle(screen, color, 
                             (star['x'], star['y']), star['size'])
        
        # 3. Title với hiệu ứng đẹp
        title_text = "CHỌN PHI THUYỀN"
        title_color = (120, 160, 240)
        title_surface = self.font_manager.render_text(title_text, 60, title_color, 
                                                     bold=True, shadow=True, glow=True)
        if title_surface:
            title_rect = title_surface.get_rect(center=(self.center_x, 60))
            screen.blit(title_surface, title_rect)
        
        # 4. Back button với hiệu ứng
        back_rect = pygame.Rect(20, 20, 100, 30)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = back_rect.collidepoint(mouse_pos)
        
        if is_hover:
            pygame.draw.rect(screen, (60, 90, 140), back_rect, border_radius=5)
            pygame.draw.rect(screen, (120, 160, 220), back_rect, width=2, border_radius=5)
            back_text = self.font_manager.render_text("← QUAY LẠI", 18, (255, 255, 255), bold=True, glow=True)
        else:
            pygame.draw.rect(screen, (40, 60, 100), back_rect, border_radius=5)
            pygame.draw.rect(screen, (80, 120, 180), back_rect, width=2, border_radius=5)
            back_text = self.font_manager.render_text("← QUAY LẠI", 18, (180, 200, 240), shadow=True)
        
        if back_text:
            back_text_rect = back_text.get_rect(center=back_rect.center)
            screen.blit(back_text, back_text_rect)
        
        # 5. Draw spaceship grid
        grid_rects = self.get_ship_grid_rects()
        
        for i, (rect, ship) in enumerate(zip(grid_rects, self.spaceships)):
            # Selection highlight
            if i == self.selected_ship:
                # Glow effect
                glow_rect = pygame.Rect(rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10)
                pygame.draw.rect(screen, (80, 120, 200, 100), glow_rect, border_radius=10)
                pygame.draw.rect(screen, (120, 160, 255), rect, width=3, border_radius=8)
            else:
                pygame.draw.rect(screen, (50, 70, 120), rect, width=1, border_radius=8)
            
            # Ship image
            ship_rect = ship['image'].get_rect(center=rect.center)
            screen.blit(ship['image'], ship_rect)
            
            # Ship name với hiệu ứng đẹp
            is_selected = (i == self.selected_ship)
            name_color = (220, 240, 255) if is_selected else (180, 200, 240)
            name_text = self.font_manager.render_text(ship['name'], 14, name_color, 
                                                     bold=is_selected, shadow=True)
            if name_text:
                name_rect = name_text.get_rect(center=(rect.centerx, rect.bottom + 15))
                screen.blit(name_text, name_rect)
        
        # 6. Selected ship info với hiệu ứng đẹp
        if self.spaceships:
            selected_ship = self.spaceships[self.selected_ship]
            info_x = 50
            info_y = self.height - 120
            
            # Ship info background
            info_rect = pygame.Rect(info_x - 10, info_y - 10, 400, 100)
            pygame.draw.rect(screen, (20, 30, 50, 180), info_rect, border_radius=8)
            pygame.draw.rect(screen, (60, 90, 140), info_rect, width=2, border_radius=8)
            
            # Ship name với hiệu ứng đẹp
            name_surface = self.font_manager.render_text(selected_ship['name'], 24, (220, 240, 255), 
                                                        bold=True, glow=True)
            if name_surface:
                screen.blit(name_surface, (info_x, info_y))
            
            # Description với hiệu ứng
            desc_surface = self.font_manager.render_text(selected_ship['description'], 18, (160, 180, 220), shadow=True)
            if desc_surface:
                screen.blit(desc_surface, (info_x, info_y + 30))
            
            # Controls với hiệu ứng
            controls_text = "ENTER để chọn • ESC quay lại"
            controls_surface = self.font_manager.render_text(controls_text, 16, (120, 140, 180), shadow=True)
            if controls_surface:
                screen.blit(controls_surface, (info_x, info_y + 55))
        
        # 7. Controls hint với hiệu ứng đẹp
        hint_text = "← → ↑ ↓ Di chuyển • ENTER Chọn • ESC Quay lại"
        hint_color = (100, 120, 160)
        hint_surface = self.font_manager.render_text(hint_text, 16, hint_color, shadow=True)
        if hint_surface:
            hint_rect = hint_surface.get_rect(center=(self.center_x, self.height - 20))
            screen.blit(hint_surface, hint_rect)
