# -*- coding: utf-8 -*-
"""
Centralized asset loader for spaceships and planets
"""
import os
import pygame
import random
from pathlib import Path
from config import get_selected_spaceship

class AssetLoader:
    """Load và cache assets (spaceship, planet) một cách tập trung"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.project_root = self._get_project_root()
        
        # Cache dictionaries
        self.spaceship_cache = {}
        self.planet_cache = {}
    
    def _get_project_root(self):
        """Tính đường dẫn project root từ file hiện tại"""
        current_file = os.path.abspath(__file__)  # MazePaint/src/Ui/asset_loader.py
        ui_dir = os.path.dirname(current_file)    # MazePaint/src/Ui
        src_dir = os.path.dirname(ui_dir)         # MazePaint/src
        project_root = os.path.dirname(src_dir)   # MazePaint
        return project_root
    
    def get_spaceship_path(self, ship_id):
        """
        Lấy đường dẫn đầy đủ của spaceship
        Args:
            ship_id: int (1-9) hoặc string ("spaceship1.png", "ship_1.svg")
        Returns:
            Path object hoặc None nếu không tìm thấy
        """
        # Xử lý input linh hoạt
        if isinstance(ship_id, int):
            filename = f"spaceship{ship_id}.png"
        else:
            filename = ship_id
        
        spaceship_dir = os.path.join(self.project_root, "asset", "image", "spaceship")
        spaceship_path = os.path.join(spaceship_dir, filename)
        
        if os.path.exists(spaceship_path):
            return spaceship_path
        
        # Try alternative naming: ship_X.svg
        if isinstance(ship_id, int):
            alt_filename = f"ship_{ship_id}.svg"
            alt_path = os.path.join(spaceship_dir, alt_filename)
            if os.path.exists(alt_path):
                return alt_path

        return None
    
    def get_planet_path(self, planet_id):
        """
        Lấy đường dẫn đầy đủ của planet
        Args:
            planet_id: int (1-3) hoặc string ("planet1.png")
        Returns:
            Path object hoặc None nếu không tìm thấy
        """
        if isinstance(planet_id, int):
            filename = f"planet{planet_id}.png"
        else:
            filename = planet_id
        
        planet_dir = os.path.join(self.project_root, "asset", "image", "planet")
        planet_path = os.path.join(planet_dir, filename)
        
        if os.path.exists(planet_path):
            return planet_path
        
        # Fallback: try without subfolder
        fallback_path = os.path.join(self.project_root, "asset", "image", filename)
        if os.path.exists(fallback_path):
            return fallback_path

        return None
    
    def load_spaceship(self, ship_id, cache=True):
        """
        Load spaceship image
        Args:
            ship_id: int hoặc string
            cache: bool - có cache không
        Returns:
            pygame.Surface hoặc None
        """
        cache_key = f"spaceship_{ship_id}"
        
        # Check cache first
        if cache and cache_key in self.spaceship_cache:
            return self.spaceship_cache[cache_key]
        
        # Load from file
        path = self.get_spaceship_path(ship_id)
        if path is None:
            return None
        
        try:
            image = pygame.image.load(path).convert_alpha()
            if cache:
                self.spaceship_cache[cache_key] = image
            return image
        except Exception as e:
            print(f"❌ Error loading spaceship {ship_id}: {e}")
            return None
    
    def load_planet(self, planet_id, cache=True):
        """
        Load planet image
        Args:
            planet_id: int hoặc string
            cache: bool - có cache không
        Returns:
            pygame.Surface hoặc None
        """
        cache_key = f"planet_{planet_id}"
        
        # Check cache first
        if cache and cache_key in self.planet_cache:
            return self.planet_cache[cache_key]
        
        # Load from file
        path = self.get_planet_path(planet_id)
        if path is None:
            return None
        
        try:
            image = pygame.image.load(path).convert_alpha()
            if cache:
                self.planet_cache[cache_key] = image
            return image
        except Exception as e:
            print(f"❌ Error loading planet {planet_id}: {e}")
            return None
    
    def load_spaceship_rotated(self, ship_id, cache=True):
        """
        Load spaceship và tạo 4 hướng xoay
        Returns:
            dict {'up': surf, 'down': surf, 'left': surf, 'right': surf, None: surf}
        """
        cache_key = f"spaceship_rotated_{ship_id}"
        
        # Check cache
        if cache and cache_key in self.spaceship_cache:
            return self.spaceship_cache[cache_key]
        
        # Load base image
        base_image = self.load_spaceship(ship_id, cache=False)
        if base_image is None:
            return None
        
        # Create rotated versions
        rotated_images = {
            'right': base_image,
            'down': pygame.transform.rotate(base_image, -90),
            'left': pygame.transform.rotate(base_image, 180),
            'up': pygame.transform.rotate(base_image, 90),
            None: base_image
        }
        
        if cache:
            self.spaceship_cache[cache_key] = rotated_images
        
        return rotated_images
    
    def get_planet_scaled(self, planet_id, size, cache=True):
        """
        Lấy planet đã scale
        Args:
            planet_id: int hoặc string
            size: int - kích thước muốn
            cache: bool
        Returns:
            pygame.Surface hoặc None
        """
        cache_key = f"planet_{planet_id}_size_{size}"
        
        # Check cache
        if cache and cache_key in self.planet_cache:
            return self.planet_cache[cache_key]
        
        # Load base image
        base_image = self.load_planet(planet_id, cache=False)
        if base_image is None:
            return None
        
        # Scale
        scaled_image = pygame.transform.smoothscale(base_image, (size, size))
        
        if cache:
            self.planet_cache[cache_key] = scaled_image
        
        return scaled_image
    
    def clear_cache(self):
        """Clear toàn bộ cache"""
        self.spaceship_cache.clear()
        self.planet_cache.clear()
   
    
    def preload_common_assets(self):
        """Preload các asset thường dùng"""
        
        # Preload all spaceships
        for i in range(1, 4):
            self.load_spaceship_rotated(i)
        
        # Preload all planets with common sizes
        for i in range(1, 4):
            for size in [70, 80, 90, 100]:
                self.get_planet_scaled(i, size)
        


# Singleton instance
asset_loader = AssetLoader()

# ===== HELPER FUNCTIONS CHO CONVENIENCE =====

def get_spaceship_for_player(size=40, cache=True):
    """
    Lấy spaceship hiện tại của player theo SELECTED_SPACESHIP
    Trả về dict với các hướng đã scale
    """
    
    ship_id = get_selected_spaceship() + 1  # 0-8 -> 1-9
    rotated = asset_loader.load_spaceship_rotated(ship_id, cache=cache)
    
    if not rotated:
        return None
    
    # Scale all directions
    scaled_rotated = {}
    for direction, img in rotated.items():
        scaled_rotated[direction] = pygame.transform.scale(img, (size, size))
    
    return scaled_rotated


def get_random_planet(min_size=70, max_size=100, cache=True):
    """
    Lấy random planet với size ngẫu nhiên
    Tiện cho tạo obstacles
    """
    planet_id = random.randint(1, 3)
    size = random.randint(min_size, max_size)
    return asset_loader.get_planet_scaled(planet_id, size, cache=cache)


def preload_all():
    """Preload TẤT CẢ assets cần thiết cho game"""
    
    # Preload tất cả spaceships (1-9)
    for ship_id in range(1, 10):
        asset_loader.load_spaceship_rotated(ship_id)
    
    # Preload tất cả planets với common sizes
    for planet_id in range(1, 4):
        for size in [70, 75, 80, 85, 90, 95, 100]:
            asset_loader.get_planet_scaled(planet_id, size)

def get_asset_stats():
    """In thống kê về assets đã cache"""
    spaceship_count = sum(1 for key in asset_loader.spaceship_cache.keys() 
                         if 'spaceship' in str(key))
    planet_count = len(asset_loader.planet_cache)
    
    return {
        'spaceships': spaceship_count,
        'planets': planet_count,
        'total': spaceship_count + planet_count
    }