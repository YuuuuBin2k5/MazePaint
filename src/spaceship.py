# spaceship.py - Simple spaceship with rotation
import pygame
import math
import random
from config import *

# Load spaceship image once at module level
spaceship_image = None
spaceship_rotated_images = {}
last_direction = None  # Lưu hướng cuối cùng

def load_spaceship_image():
    """Load và cache ảnh spaceship"""
    global spaceship_image, spaceship_rotated_images
    
    if spaceship_image is None:
        try:
            # Try loading from spaceship.png first
            spaceship_image = pygame.image.load("asset/image/spaceship/ship_7.svg")
            print("✅ Loaded spaceship.png")
        except:
            try:
                # Create simple spaceship if no image found
                spaceship_image = create_simple_spaceship()
                print("✅ Created simple spaceship")
            except Exception as e:
                print(f"❌ Error creating spaceship: {e}")
                spaceship_image = create_fallback_spaceship()
        
        # Scale to appropriate size
        size = PLAYER_RADIUS * 4
        spaceship_image = pygame.transform.scale(spaceship_image, (size, size))
        
        # Pre-rotate images for each direction to avoid runtime rotation
        spaceship_rotated_images = {
            "up": pygame.transform.rotate(spaceship_image, -90),      # Default up
            "right": pygame.transform.rotate(spaceship_image, 0), # Rotate 90° clockwise 
            "down": pygame.transform.rotate(spaceship_image, 90),  # Rotate 180°
            "left": pygame.transform.rotate(spaceship_image, 180),   # Rotate 90° counter-clockwise
            None: spaceship_image  # Default orientation
        }
        
        print("✅ Loaded simple spaceship with rotations")

def create_simple_spaceship():
    """Tạo spaceship đơn giản nếu không có ảnh"""
    size = PLAYER_RADIUS * 4
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Vẽ tam giác spaceship đơn giản
    center_x, center_y = size // 2, size // 2
    points = [
        (center_x, center_y - size//3),      # Đỉnh trên
        (center_x - size//4, center_y + size//4),  # Góc trái
        (center_x + size//4, center_y + size//4)   # Góc phải
    ]
    pygame.draw.polygon(surface, (200, 200, 255), points)
    pygame.draw.polygon(surface, (255, 255, 255), points, 2)
    
    return surface

def create_fallback_spaceship():
    """Tạo spaceship fallback đơn giản nhất"""
    size = PLAYER_RADIUS * 4
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
    return surface

class StarParticle:
    """Class đơn giản cho hiệu ứng vì sao"""
    def __init__(self, x, y, direction=None):
        self.x = x + random.uniform(-5, 5)
        self.y = y + random.uniform(-5, 5)
        
        # Tốc độ particles ngược hướng di chuyển
        base_speed = random.uniform(15, 25)
        if direction == "up":
            self.vx = random.uniform(-5, 5)
            self.vy = base_speed
        elif direction == "down":
            self.vx = random.uniform(-5, 5)
            self.vy = -base_speed
        elif direction == "left":
            self.vx = base_speed
            self.vy = random.uniform(-5, 5)
        elif direction == "right":
            self.vx = -base_speed
            self.vy = random.uniform(-5, 5)
        else:
            self.vx = random.uniform(-10, 10)
            self.vy = random.uniform(-10, 10)
        
        self.life = random.uniform(1.0, 2.0)
        self.max_life = self.life
        self.size = random.uniform(3, 6)
        self.color = (255, 255, 255)  # Trắng đơn giản
    
    def update(self, dt):
        """Cập nhật vị trí và tuổi thọ của vì sao"""
        dt_sec = dt / 1000.0
        self.x += self.vx * dt_sec
        self.y += self.vy * dt_sec
        self.life -= dt_sec
        self.vx *= 0.98
        self.vy *= 0.98
        return self.life > 0
    
    def draw(self, screen):
        """Vẽ vì sao đơn giản"""
        if self.life <= 0:
            return
            
        alpha = int(255 * (self.life / self.max_life))
        if alpha < 10:
            return
            
        # Vẽ vì sao bằng 2 đường thẳng chéo nhau
        center_x, center_y = int(self.x), int(self.y)
        size = int(self.size)
        
        pygame.draw.line(screen, self.color, 
                        (center_x - size, center_y), 
                        (center_x + size, center_y), 2)
        pygame.draw.line(screen, self.color, 
                        (center_x, center_y - size), 
                        (center_x, center_y + size), 2)

# Global particles list
star_particles = []

def add_star_particles(x, y, direction, count=3):
    """Thêm các particles vì sao"""
    global star_particles
    for _ in range(count):
        star_particles.append(StarParticle(x, y, direction))

def update_star_particles(dt):
    """Cập nhật tất cả particles"""
    global star_particles
    star_particles = [p for p in star_particles if p.update(dt)]

def draw_star_particles(screen):
    """Vẽ tất cả particles"""
    for particle in star_particles:
        particle.draw(screen)

def draw_spaceship_player(screen, x, y, direction=None):
    """Vẽ spaceship đơn giản với rotation"""
    global last_direction
    
    # Load image if needed
    load_spaceship_image()
    
    # Cập nhật last_direction nếu có direction mới
    if direction is not None:
        last_direction = direction
    
    # Sử dụng direction hiện tại hoặc last_direction nếu không có direction
    current_direction = direction if direction is not None else last_direction
    
    # Get appropriate rotated image
    image = spaceship_rotated_images.get(current_direction, spaceship_rotated_images[None])
    
    # Center the image
    rect = image.get_rect()
    rect.center = (x, y)
    
    # Draw spaceship
    screen.blit(image, rect)
    
    # Add star particles if moving (chỉ khi có direction mới, không phải last_direction)
    if direction and random.random() < 0.3:  # 30% chance to spawn particles
        add_star_particles(x, y, direction, count=2)

def draw_rotated_spaceship(screen, x, y, direction="up"):
    """Alias for compatibility"""
    draw_spaceship_player(screen, x, y, direction)

# Compatibility functions for existing code
class SpaceshipAnimator:
    """Compatibility class - simplified"""
    def __init__(self):
        self.loaded = True
    
    def set_animation(self, anim_name):
        pass
    
    def update_animation(self, dt=0):
        pass
    
    def get_current_frame(self):
        load_spaceship_image()
        return spaceship_image

    def update(self, is_moving=False):
        pass
    
    def update_particles(self, x, y, direction=None, is_moving=False):
        pass
    
    def draw_particles(self, screen):
        pass

# Create global animator for compatibility
spaceship_animator = SpaceshipAnimator()

def draw_static_spaceship(screen, center_x, center_y):
    """Draw static spaceship"""
    draw_spaceship_player(screen, center_x, center_y)

def draw_animated_spaceship(screen, center_x, center_y):
    """Draw spaceship - same as static for simplicity"""
    draw_spaceship_player(screen, center_x, center_y)


# Easing functions for smooth movement
def ease_in_out_quart(t):
    """Easing function mạnh hơn: chậm hơn ở đầu/cuối, nhanh hơn ở giữa"""
    if t < 0.5:
        return 8 * t * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 4) / 2

def ease_in_out_sine(t):
    """Easing function mượt mà: dùng sine wave"""
    import math
    return -(math.cos(math.pi * t) - 1) / 2
