# asteroid_walls.py
import pygame
import random
import math
from config import *

class AsteroidWall:
    def __init__(self):
        self.wall_cache = {}
        self.asteroid_types = ["crystalline", "metallic", "volcanic", "normal"]
    
    def create_asteroid_wall_tile(self, tile_size, asteroid_type="normal"):
        """Tạo texture asteroid wall cho một ô"""
        if (tile_size, asteroid_type) in self.wall_cache:
            return self.wall_cache[(tile_size, asteroid_type)]
        
        surface = pygame.Surface((tile_size, tile_size))
        
        # Màu cơ bản theo loại asteroid
        if asteroid_type == "crystalline":
            base_color = (80, 120, 160)
            accent_color = (120, 160, 200)
        elif asteroid_type == "metallic":
            base_color = (100, 100, 120)
            accent_color = (140, 140, 160)
        elif asteroid_type == "volcanic":
            base_color = (120, 80, 60)
            accent_color = (160, 100, 80)
        else:  # normal
            base_color = (90, 90, 100)
            accent_color = (120, 120, 130)
        
        surface.fill(base_color)
        
        # Thêm texture và chi tiết
        for _ in range(20):
            x = random.randint(0, tile_size - 1)
            y = random.randint(0, tile_size - 1)
            size = random.randint(1, 3)
            color_variation = random.randint(-30, 30)
            
            detail_color = (
                max(0, min(255, accent_color[0] + color_variation)),
                max(0, min(255, accent_color[1] + color_variation)),
                max(0, min(255, accent_color[2] + color_variation))
            )
            
            pygame.draw.circle(surface, detail_color, (x, y), size)
        
        # Thêm viền tối
        pygame.draw.rect(surface, (40, 40, 50), (0, 0, tile_size, tile_size), 1)
        
        self.wall_cache[(tile_size, asteroid_type)] = surface
        return surface
    
    def get_wall_tile(self, row, col, tile_size):
        """Lấy tile asteroid dựa trên vị trí"""
        # Sử dụng position để chọn loại asteroid
        random.seed(row * 1000 + col)  # Seed để consistent
        asteroid_type = random.choice(self.asteroid_types)
        random.seed()  # Reset seed
        
        return self.create_asteroid_wall_tile(tile_size, asteroid_type)

# Global instance
asteroid_wall_renderer = AsteroidWall()