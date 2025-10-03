# -*- coding: utf-8 -*-
"""
Wall Rendering Component - Asteroid 3D walls
"""
import pygame
import random
import math

from config import (
    ASTEROID_TYPES,
    ASTEROID_TEXTURE_DENSITY,
    ASTEROID_HIGHLIGHT_OFFSET,
)

class AsteroidWall3D:
    """3D Asteroid wall renderer với nhiều loại asteroid"""
    
    def __init__(self):
        self.wall_cache = {}
        self.asteroid_types = ASTEROID_TYPES  # ✅ DÙNG TỪ CONFIG
    
    def create_asteroid_wall_tile(self, tile_size, asteroid_type="normal"):
        """Tạo texture asteroid wall 3D cho một ô"""
        if (tile_size, asteroid_type) in self.wall_cache:
            return self.wall_cache[(tile_size, asteroid_type)]
        
        surface = pygame.Surface((tile_size, tile_size))
        
        # Màu cơ bản theo loại asteroid
        if asteroid_type == "crystalline":
            base_color = (80, 120, 160)
        elif asteroid_type == "metallic":
            base_color = (110, 110, 130)
        elif asteroid_type == "volcanic":
            base_color = (130, 85, 65)
        else:  # normal
            base_color = (95, 95, 105)

        # Gradient sáng-trung tâm, tối-viền (tạo khối 3D)
        for y in range(tile_size):
            for x in range(tile_size):
                dist_x = abs(x - tile_size/2) / (tile_size/2)
                dist_y = abs(y - tile_size/2) / (tile_size/2)
                factor = (dist_x + dist_y) / 2
                brightness = max(1.0, 1 - factor*1.0)
                r = int(base_color[0] * brightness)
                g = int(base_color[1] * brightness)
                b = int(base_color[2] * brightness)
                surface.set_at((x, y), (r, g, b))
        
        # Thêm texture asteroid (bụi + đá nhỏ) - ✅ DÙNG CONFIG
        for _ in range(ASTEROID_TEXTURE_DENSITY):
            x = random.randint(2, tile_size - 3)
            y = random.randint(2, tile_size - 3)
            size = random.randint(1, 3)
            noise = random.randint(-25, 25)
            color = (
                max(0, min(255, base_color[0] + noise)),
                max(0, min(255, base_color[1] + noise)),
                max(0, min(255, base_color[2] + noise))
            )
            pygame.draw.circle(surface, color, (x, y), size)

        # Viền highlight (trên + trái) - ✅ DÙNG CONFIG
        highlight = (
            min(255, base_color[0] + ASTEROID_HIGHLIGHT_OFFSET),
            min(255, base_color[1] + ASTEROID_HIGHLIGHT_OFFSET),
            min(255, base_color[2] + ASTEROID_HIGHLIGHT_OFFSET)
        )
        pygame.draw.line(surface, highlight, (0, 0), (tile_size - 1, 0))     # top
        pygame.draw.line(surface, highlight, (0, 0), (0, tile_size - 1))     # left

        # Viền shadow (dưới + phải) - ✅ DÙNG CONFIG
        shadow = (
            max(0, base_color[0] - ASTEROID_HIGHLIGHT_OFFSET),
            max(0, base_color[1] - ASTEROID_HIGHLIGHT_OFFSET),
            max(0, base_color[2] - ASTEROID_HIGHLIGHT_OFFSET)
        )
        pygame.draw.line(surface, shadow, (tile_size - 1, 0), (tile_size - 1, tile_size - 1))  # right
        pygame.draw.line(surface, shadow, (0, tile_size - 1), (tile_size - 1, tile_size - 1))  # bottom
        
        self.wall_cache[(tile_size, asteroid_type)] = surface
        return surface
    
    def get_wall_tile(self, row, col, tile_size):
        """Lấy tile asteroid 3D dựa trên vị trí"""
        random.seed(row * 1000 + col)  # Seed để consistent
        asteroid_type = random.choice(self.asteroid_types)
        random.seed()  # Reset seed
        
        return self.create_asteroid_wall_tile(tile_size, asteroid_type)

# Global instance
asteroid_wall_3d_renderer = AsteroidWall3D()
