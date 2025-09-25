# cosmic_selector.py - Cosmic Algorithm Selector with 3D space theme
import pygame
import math
import random
from config import *

class CosmicAlgorithmSelector:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Use cosmic-style fonts that match the game theme
        try:
            # Try futuristic/tech fonts first, then fall back to Vietnamese support
            font_names = [
                "Consolas",        # Monospace tech look - great for sci-fi
                "Courier New",     # Classic computer terminal font
                "Lucida Console",  # Clean terminal style
                "Monaco",          # Clean monospace
                "DejaVu Sans Mono", # Open source monospace
                "Liberation Mono",  # Another good monospace
                "Segoe UI",        # Modern with Vietnamese support
                "Tahoma",          # Good Vietnamese support
                "Arial"            # Last resort
            ]
            font_found = False
            
            for font_name in font_names:
                try:
                    test_font = pygame.font.SysFont(font_name, 24, bold=True)
                    # Test Vietnamese rendering
                    test_surf = test_font.render("Tiếng Việt", True, (255, 255, 255))
                    if test_surf.get_width() > 0:  # Font works
                        # Use larger, bolder fonts for cosmic effect
                        self.font_title = pygame.font.SysFont(font_name, 48, bold=True)
                        self.font_algo = pygame.font.SysFont(font_name, 32, bold=True) 
                        self.font_desc = pygame.font.SysFont(font_name, 22)
                        print(f"🚀 Using cosmic font: {font_name}")
                        font_found = True
                        break
                except:
                    continue
                    
            # Final fallback with enhanced cosmic sizes
            if not font_found:
                print("⚠️ Using fallback fonts with cosmic enhancement")
                self.font_title = pygame.font.Font(None, 48)
                self.font_algo = pygame.font.Font(None, 32)
                self.font_desc = pygame.font.Font(None, 22)
                
        except Exception as e:
            print(f"Font error: {e}")
            self.font_title = pygame.font.Font(None, 42)
            self.font_algo = pygame.font.Font(None, 28)
            self.font_desc = pygame.font.Font(None, 20)
        
        # Algorithm data with cosmic descriptions in Vietnamese
        self.algorithms = [
            {
                "name": "Player",
                "title": "Player",
                "desc": "Điều khiển tàu vũ trụ bằng tay",
                "color": (100, 200, 255),
                "glow": (150, 220, 255)
            },
            {
                "name": "BFS",
                "title": "Breadth-First Search",
                "desc": "Khám phá đồng đều tất cả hướng",
                "color": (255, 150, 100),
                "glow": (255, 200, 150)
            },
            {
                "name": "DFS",
                "title": "Depth-First Search",
                "desc": "Lao sâu vào một đường duy nhất",
                "color": (150, 255, 150),
                "glow": (200, 255, 200)
            },
            {
                "name": "UCS",
                "title": "Uniform Cost Search",
                "desc": "Tìm đường đi ít tốn kém nhất",
                "color": (255, 255, 100),
                "glow": (255, 255, 180)
            },
            {
                "name": "Greedy",
                "title": "Greedy Best-First",
                "desc": "Lao thẳng về phía đích",
                "color": (255, 100, 255),
                "glow": (255, 180, 255)
            },
            {
                "name": "Astar",
                "title": "A* Algorithm",
                "desc": "Hệ thống tìm đường tối ưu",
                "color": (255, 200, 100),
                "glow": (255, 230, 150)
            }
        ]
        
        # Animation state
        self.frame = 0
        self.selected_index = 0
        self.hover_index = -1
        self.stars = []
        self.init_stars()
        
        # Layout
        self.panel_width = 600
        self.panel_height = 500
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        self.button_height = 60
        self.button_margin = 10
        self.buttons_start_y = self.panel_y + 100
        
    def safe_render_text(self, font, text, color):
        """Safely render Vietnamese text with fallback"""
        try:
            return font.render(text, True, color)
        except UnicodeError:
            # Remove Vietnamese characters and use ASCII fallback
            ascii_text = text.encode('ascii', 'ignore').decode('ascii')
            if ascii_text.strip():
                return font.render(ascii_text, True, color)
            else:
                return font.render("Text", True, color)
        except Exception as e:
            print(f"Text render error: {e}")
            return font.render("Error", True, color)
    
    def init_stars(self):
        """Initialize enhanced star field with shooting stars"""
        # Regular stars
        for _ in range(150):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(1, 3)
            speed = random.uniform(0.2, 1.5)
            brightness = random.randint(80, 255)
            self.stars.append([x, y, size, speed, brightness])
            
        # Add shooting stars data
        self.shooting_stars = []
        for _ in range(3):
            self.add_shooting_star()
    
    def add_shooting_star(self):
        """Add a new shooting star"""
        x = self.screen_width + random.randint(50, 200)
        y = random.randint(50, self.screen_height - 50)
        speed = random.uniform(3, 6)
        length = random.randint(30, 60)
        brightness = random.randint(180, 255)
        self.shooting_stars.append([x, y, speed, length, brightness])
    
    def update_stars(self):
        """Update enhanced star field animation"""
        # Update regular stars
        for star in self.stars:
            star[0] -= star[3]  # Move left
            if star[0] < 0:
                star[0] = self.screen_width + 10
                star[1] = random.randint(0, self.screen_height)
                
        # Update shooting stars
        for shooting_star in self.shooting_stars[:]:
            shooting_star[0] -= shooting_star[2]
            shooting_star[1] += shooting_star[2] * 0.3  # Slight downward angle
            
            if shooting_star[0] < -shooting_star[3]:
                self.shooting_stars.remove(shooting_star)
                self.add_shooting_star()
    
    def draw_stars(self, screen):
        """Draw enhanced animated star field with shooting stars"""
        # Draw regular twinkling stars
        for star in self.stars:
            x, y, size, speed, brightness = star
            # Add twinkling effect
            twinkle = math.sin(self.frame * 0.1 + x * 0.01) * 30
            actual_brightness = max(50, min(255, brightness + twinkle))
            color = (actual_brightness, actual_brightness, actual_brightness)
            
            if size == 1:
                screen.set_at((int(x), int(y)), color)
            else:
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
                # Add small cross for bigger stars
                if size >= 2:
                    pygame.draw.line(screen, color, 
                                   (int(x-size-1), int(y)), 
                                   (int(x+size+1), int(y)), 1)
                    pygame.draw.line(screen, color, 
                                   (int(x), int(y-size-1)), 
                                   (int(x), int(y+size+1)), 1)
        
        # Draw shooting stars
        for shooting_star in self.shooting_stars:
            x, y, speed, length, brightness = shooting_star
            # Draw trail
            for i in range(length):
                trail_x = x + i * 2
                trail_y = y - i * 0.6
                trail_brightness = max(0, brightness - i * 4)
                if trail_brightness > 0:
                    trail_color = (trail_brightness, trail_brightness // 2, trail_brightness // 3)
                    if i < 5:  # Bright head
                        pygame.draw.circle(screen, (255, 255, 255), 
                                         (int(trail_x), int(trail_y)), 2)
                    else:  # Fading trail
                        screen.set_at((int(trail_x), int(trail_y)), trail_color)
    
    def draw_3d_panel(self, screen):
        """Draw 3D cosmic panel background"""
        # Main panel with gradient
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        
        # Create gradient background
        for y in range(self.panel_height):
            ratio = y / self.panel_height
            r = max(0, min(255, int(10 * (1 - ratio) + 30 * ratio)))
            g = max(0, min(255, int(15 * (1 - ratio) + 40 * ratio)))
            b = max(0, min(255, int(30 * (1 - ratio) + 60 * ratio)))
            color = (r, g, b)
            line_rect = pygame.Rect(self.panel_x, self.panel_y + y, self.panel_width, 1)
            pygame.draw.rect(screen, color, line_rect)
        
        # 3D border effects
        # Highlight (top-left)
        pygame.draw.line(screen, (80, 100, 140), 
                        (self.panel_x, self.panel_y), 
                        (self.panel_x + self.panel_width, self.panel_y), 3)
        pygame.draw.line(screen, (80, 100, 140), 
                        (self.panel_x, self.panel_y), 
                        (self.panel_x, self.panel_y + self.panel_height), 3)
        
        # Shadow (bottom-right)
        pygame.draw.line(screen, (5, 10, 20), 
                        (self.panel_x + self.panel_width, self.panel_y + 3), 
                        (self.panel_x + self.panel_width, self.panel_y + self.panel_height), 3)
        pygame.draw.line(screen, (5, 10, 20), 
                        (self.panel_x + 3, self.panel_y + self.panel_height), 
                        (self.panel_x + self.panel_width, self.panel_y + self.panel_height), 3)
    
    def draw_cosmic_title(self, screen):
        """Draw animated cosmic title with enhanced effects"""
        title_text = "VŨ TRỤ NAVIGATOR"
        
        # Multiple animated effects
        time_offset = self.frame * 0.08
        glow_intensity = int(80 + 50 * math.sin(time_offset))
        pulse_scale = 1.0 + 0.1 * math.sin(time_offset * 2)
        
        # Create holographic color shift
        holo_r = int(200 + 55 * math.sin(time_offset))
        holo_g = int(220 + 35 * math.sin(time_offset + 2))
        holo_b = int(255)
        
        # Draw multiple glow layers for depth
        title_surf = self.safe_render_text(self.font_title, title_text, (holo_r, holo_g, holo_b))
        title_rect = title_surf.get_rect(centerx=self.panel_x + self.panel_width // 2, 
                                        y=self.panel_y + 15)
        
        # Outer glow (cyan-blue)
        for offset in range(5, 0, -1):
            glow_alpha = glow_intensity - offset * 15
            if glow_alpha > 0:
                glow_color = (0, glow_alpha // 3, glow_alpha)
                glow_surf = self.safe_render_text(self.font_title, title_text, glow_color)
                for dx in range(-offset, offset + 1):
                    for dy in range(-offset, offset + 1):
                        if dx != 0 or dy != 0:
                            glow_rect = glow_surf.get_rect(centerx=title_rect.centerx + dx, 
                                                          y=title_rect.y + dy)
                            screen.blit(glow_surf, glow_rect)
        
        # Inner glow (white-blue)
        for offset in range(2, 0, -1):
            inner_glow = (glow_intensity, glow_intensity, 255)
            inner_surf = self.safe_render_text(self.font_title, title_text, inner_glow)
            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    if dx != 0 or dy != 0:
                        inner_rect = inner_surf.get_rect(centerx=title_rect.centerx + dx, 
                                                        y=title_rect.y + dy)
                        screen.blit(inner_surf, inner_rect)
        
        # Main title with holographic effect
        screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_text = "Chọn Phương Thức Điều Hướng"
        subtitle_surf = self.safe_render_text(self.font_desc, subtitle_text, (150, 200, 255))
        subtitle_rect = subtitle_surf.get_rect(centerx=self.panel_x + self.panel_width // 2, 
                                             y=title_rect.bottom + 8)
        screen.blit(subtitle_surf, subtitle_rect)
    
    def draw_algorithm_button(self, screen, algo_data, index, button_rect):
        """Draw 3D cosmic algorithm button"""
        is_selected = (index == self.selected_index)
        is_hovered = (index == self.hover_index)
        
        # Button 3D effect
        if is_selected:
            # Selected state - bright and elevated
            base_color = algo_data["glow"]
            border_highlight = tuple(min(255, max(0, int(c + 50))) for c in base_color)
            border_shadow = tuple(max(0, int(c - 50)) for c in base_color)
        elif is_hovered:
            # Hovered state - medium brightness
            base_color = tuple(min(255, max(0, int(c * 1.2))) for c in algo_data["color"])
            border_highlight = tuple(min(255, max(0, int(c + 30))) for c in base_color)
            border_shadow = tuple(max(0, int(c - 30)) for c in base_color)
        else:
            # Normal state
            base_color = algo_data["color"]
            border_highlight = tuple(min(255, max(0, int(c + 20))) for c in base_color)
            border_shadow = tuple(max(0, int(c - 40)) for c in base_color)
        
        # Main button background with gradient
        for y in range(button_rect.height):
            ratio = y / button_rect.height
            r = max(0, min(255, int(base_color[0] * (0.3 + 0.7 * (1 - ratio)))))
            g = max(0, min(255, int(base_color[1] * (0.3 + 0.7 * (1 - ratio)))))
            b = max(0, min(255, int(base_color[2] * (0.3 + 0.7 * (1 - ratio)))))
            color = (r, g, b)
            line_rect = pygame.Rect(button_rect.x, button_rect.y + y, button_rect.width, 1)
            pygame.draw.rect(screen, color, line_rect)
        
        # 3D borders
        # Top and left highlights
        pygame.draw.line(screen, border_highlight,
                        (button_rect.left, button_rect.top),
                        (button_rect.right, button_rect.top), 2)
        pygame.draw.line(screen, border_highlight,
                        (button_rect.left, button_rect.top),
                        (button_rect.left, button_rect.bottom), 2)
        
        # Bottom and right shadows
        pygame.draw.line(screen, border_shadow,
                        (button_rect.left + 2, button_rect.bottom),
                        (button_rect.right, button_rect.bottom), 2)
        pygame.draw.line(screen, border_shadow,
                        (button_rect.right, button_rect.top + 2),
                        (button_rect.right, button_rect.bottom), 2)
        
        # Algorithm title with enhanced glow effect
        title_color = (255, 255, 255) if not is_hovered else (255, 255, 100)
        if is_hovered:
            # Add glow to hovered title
            for offset in range(2, 0, -1):
                glow_title = self.safe_render_text(self.font_algo, algo_data["title"], 
                                                 (100, 150, 255))
                for dx in range(-offset, offset + 1):
                    for dy in range(-offset, offset + 1):
                        if dx != 0 or dy != 0:
                            glow_rect = pygame.Rect(button_rect.x + 20 + dx, 
                                                   button_rect.y + 8 + dy, 0, 0)
                            screen.blit(glow_title, glow_rect)
        
        title_surf = self.safe_render_text(self.font_algo, algo_data["title"], title_color)
        title_rect = title_surf.get_rect(x=button_rect.x + 20, y=button_rect.y + 8)
        screen.blit(title_surf, title_rect)
        
        # Algorithm description with cosmic styling
        desc_color = (200, 200, 200) if not is_hovered else (150, 200, 255)
        desc_text = algo_data["desc"]  # Add cosmic brackets
        desc_surf = self.safe_render_text(self.font_desc, desc_text, desc_color)
        desc_rect = desc_surf.get_rect(x=button_rect.x + 20, y=button_rect.y + 35)
        screen.blit(desc_surf, desc_rect)
        
        # Selection indicator with enhanced animation
        if is_selected:
            # Multi-layered animated selection glow
            time_offset = self.frame * 0.15
            pulse_size = int(10 + 6 * math.sin(time_offset))
            inner_pulse = int(6 + 3 * math.sin(time_offset + 1))
            
            # Outer energy ring
            glow_color = algo_data["glow"]
            pygame.draw.circle(screen, glow_color, 
                             (button_rect.x + 10, button_rect.centery), 
                             pulse_size)
            
            # Middle energy ring
            mid_color = tuple(min(255, c + 50) for c in glow_color)
            pygame.draw.circle(screen, mid_color, 
                             (button_rect.x + 10, button_rect.centery), 
                             inner_pulse)
            
            # Core
            pygame.draw.circle(screen, (255, 255, 255), 
                             (button_rect.x + 10, button_rect.centery), 
                             3)
            
            # Add energy particles around selection
            for i in range(3):
                angle = time_offset * 2 + i * (2 * math.pi / 3)
                particle_x = button_rect.x + 10 + int(15 * math.cos(angle))
                particle_y = button_rect.centery + int(15 * math.sin(angle))
                particle_size = int(2 + math.sin(time_offset + i) * 1)
                pygame.draw.circle(screen, glow_color, 
                                 (particle_x, particle_y), particle_size)
    
    def get_button_rect(self, index):
        """Get button rectangle for given index"""
        y = self.buttons_start_y + index * (self.button_height + self.button_margin)
        return pygame.Rect(self.panel_x + 20, y, self.panel_width - 40, self.button_height)
    
    def handle_mouse_motion(self, mouse_pos):
        """Handle mouse motion for hover effects"""
        self.hover_index = -1
        for i in range(len(self.algorithms)):
            button_rect = self.get_button_rect(i)
            if button_rect.collidepoint(mouse_pos):
                self.hover_index = i
                break
    
    def handle_mouse_click(self, mouse_pos):
        """Handle mouse click for selection"""
        for i in range(len(self.algorithms)):
            button_rect = self.get_button_rect(i)
            if button_rect.collidepoint(mouse_pos):
                self.selected_index = i
                return self.algorithms[i]["name"]
        return None
    
    def handle_key_press(self, key):
        """Handle keyboard navigation"""
        if key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == pygame.K_DOWN:
            self.selected_index = min(len(self.algorithms) - 1, self.selected_index + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            return self.algorithms[self.selected_index]["name"]
        return None
    
    def update(self):
        """Update animation frame"""
        self.frame += 1
        self.update_stars()
    
    def draw(self, screen):
        """Draw the complete cosmic selector"""
        # Clear with space background
        screen.fill((5, 10, 20))
        
        # Draw star field
        self.draw_stars(screen)
        
        # Draw main panel
        self.draw_3d_panel(screen)
        self.draw_cosmic_title(screen)
        
        # Draw algorithm buttons
        for i, algo_data in enumerate(self.algorithms):
            button_rect = self.get_button_rect(i)
            self.draw_algorithm_button(screen, algo_data, i, button_rect)
        
        # Draw instructions
        instruction_text = "↑↓ Di chuyển | ENTER Chọn | ESC Hủy"
        instruction_surf = self.font_desc.render(instruction_text, True, (150, 150, 150))
        instruction_rect = instruction_surf.get_rect(centerx=self.screen_width // 2,
                                                   y=self.panel_y + self.panel_height + 20)
        screen.blit(instruction_surf, instruction_rect)

def cosmic_algorithm_selector(screen, clock):
    """
    Show cosmic algorithm selector and return selected algorithm.
    Returns algorithm name or None if cancelled.
    """
    selector = CosmicAlgorithmSelector(WINDOW_WIDTH, WINDOW_HEIGHT)
    running = True
    selected_algorithm = None
    
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                else:
                    result = selector.handle_key_press(event.key)
                    if result:
                        return result
            elif event.type == pygame.MOUSEMOTION:
                selector.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    result = selector.handle_mouse_click(event.pos)
                    if result:
                        return result
        
        selector.update()
        selector.draw(screen)
        pygame.display.flip()
    
    return None