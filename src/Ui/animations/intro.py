# -*- coding: utf-8 -*-
"""
Intro Animation - 3 spaceships dodging asteroids
"""
import os
import pygame
import random
import math
from pathlib import Path

# Config - ✅ SỬA: import các constants cần thiết
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    INTRO_FADE_IN_DURATION,
    INTRO_ZOOM_DURATION,
    INTRO_TITLE_DURATION,
    INTRO_MENU_FADE_DURATION,
    ASSET_PRELOAD_TIMEOUT,
    LOADING_BAR_WIDTH,
    LOADING_BAR_HEIGHT,
    SPACESHIP_SIZE,
)

# Systems - ✅ SỬA: manager → managers
from manager.font_manager import get_font_manager

# Asset Management - ✅ SỬA: manager → managers
from manager.asset_manager import asset_loader, preload_all, get_asset_stats

class IntroAnimation:
    """Intro animation với 3 phi thuyền bay nhiều hướng né thiên thạch"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.frame = 0
        self.finished = False
        self.transition_progress = 0.0
        self.transitioning = False
        
        # Available spaceship types (IDs: 1-9)
        self.spaceship_types = [1, 2, 3]
        
        # PRE-CACHE: Tạo gradient background một lần
        self.background_surf = pygame.Surface((width, height))
        for y in range(height):
            ratio = y / height
            r = int(5 * (1 - ratio) + 25 * ratio)
            g = int(2 * (1 - ratio) + 15 * ratio)
            b = int(15 * (1 - ratio) + 45 * ratio)
            pygame.draw.line(self.background_surf, (r, g, b), (0, y), (width, y))
        
        # PRE-CACHE: Smoke, trail, glow surfaces
        self._create_effect_caches()
        
        # ===== PRELOAD ALL ASSETS =====
        preload_all()
        get_asset_stats()
        
        # Load spaceship images using asset_manager
        self.spaceship_images = {}
        for ship_id in self.spaceship_types:
            try:
                rotated_images = asset_loader.load_spaceship_rotated(
                    ship_id, 
                    cache=True
                )
                if rotated_images:
                    self.spaceship_images[ship_id] = rotated_images
                else:
                    print(f"⚠️ No images loaded for spaceship {ship_id}, creating placeholder")
                    self._create_placeholder_spaceship_for_id(ship_id)
            except Exception as e:
                print(f"❌ Error loading spaceship {ship_id}: {e}")
                self._create_placeholder_spaceship_for_id(ship_id)
        
        # Fallback if no images loaded
        if not self.spaceship_images:
            self._create_placeholder_spaceship()
        
        # Load font manager and create text surfaces
        font_manager = get_font_manager()
        self.title_surf = font_manager.render_text(
            "MAZE PAINT", 72, (200, 220, 255), 
            bold=True, glow=True
        )
        self.instruction_surf = font_manager.render_text(
            "Click anywhere to start", 28, (220, 220, 255), 
            shadow=True
        )
        
        # Initialize 3 spaceships
        self._init_spaceships()
        
        # Initialize obstacles
        self.obstacles = []
        self._create_obstacle_wave()
        
        # Background stars
        self._init_background_stars()
    
    def _create_effect_caches(self):
        """Create cached surfaces for effects"""
        # Smoke cache
        self.smoke_cache = {}
        for size in range(3, 16):
            smoke_surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            for i in range(int(size), 0, -1):
                alpha = int(200 * (i / size))
                color = (150, 150, 180, alpha)
                pygame.draw.circle(smoke_surf, color, (int(size), int(size)), i)
            self.smoke_cache[size] = smoke_surf
        
        # Trail cache
        self.trail_cache = {}
        for alpha_val in range(0, 151, 10):
            trail_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (100, 200, 255, alpha_val), (5, 5), 3)
            self.trail_cache[alpha_val] = trail_surf
        
        # Glow cache
        self.glow_cache = {}
        for intensity in [60, 120]:
            for size in [50, 60, 70]:
                glow_surf = pygame.Surface((size + 30, size + 30), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf, 
                    (100, 200, 255, intensity), 
                    (size//2 + 15, size//2 + 15), 
                    size//2 + 15
                )
                self.glow_cache[(size, intensity)] = glow_surf
    
    def _init_spaceships(self):
        """Initialize 3 spaceships with different paths"""
        self.spaceships = []
        paths = ['horizontal', 'wave', 'diagonal']
        
        for i in range(3):
            if paths[i] == 'horizontal':
                start_x = -150
                start_y = self.height * 0.3
            elif paths[i] == 'wave':
                start_x = -100
                start_y = self.height * 0.5
            else:  # diagonal
                start_x = -120
                start_y = self.height * 0.2
            
            ship = {
                'x': start_x - i * 100,
                'y': start_y,
                'start_x': start_x,
                'start_y': start_y,
                'base_speed': 2.0 + random.uniform(-0.3, 0.5),
                'current_speed': 2.0,
                'max_speed': 5.0,
                'boost_timer': 0,
                'dodge_offset': 0,
                'direction': 'right',
                'size': 50,
                'path_type': paths[i],
                'path_progress': 0,
                'spaceship_id': self.spaceship_types[i],
                'smoke_particles': []
            }
            self.spaceships.append(ship)
    
    def _init_background_stars(self):
        """Initialize background stars"""
        self.background_stars = []
        random.seed(42)
        for _ in range(60):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            speed = random.uniform(0.5, 2.0)
            brightness = random.randint(80, 255)
            self.background_stars.append([x, y, size, speed, brightness])
    
    def _get_planet_scaled(self, planet_id, size):
        """Get scaled planet image from asset_loader"""
        return asset_loader.get_planet_scaled(planet_id, size)
    
    def _create_placeholder_spaceship_for_id(self, ship_id):
        """Create placeholder spaceship for a specific ID"""
        rotated_images = {}
        
        for direction in ['up', 'down', 'left', 'right', None]:
            placeholder = pygame.Surface((50, 50), pygame.SRCALPHA)
            
            # Different triangle orientations
            if direction == 'right' or direction is None:
                points = [(40, 25), (10, 10), (10, 40)]
            elif direction == 'left':
                points = [(10, 25), (40, 10), (40, 40)]
            elif direction == 'up':
                points = [(25, 10), (10, 40), (40, 40)]
            else:  # down
                points = [(25, 40), (10, 10), (40, 10)]
            
            pygame.draw.polygon(placeholder, (100, 200, 255), points)
            pygame.draw.polygon(placeholder, (150, 220, 255), points, 2)
            rotated_images[direction] = placeholder
        
        self.spaceship_images[ship_id] = rotated_images
    
    def _create_placeholder_spaceship(self):
        """Create placeholder for all spaceships"""
        for ship_id in self.spaceship_types:
            self._create_placeholder_spaceship_for_id(ship_id)
    
    def _create_obstacle_wave(self):
        """Create initial wave of asteroids and planets"""
        # Create asteroids
        for i in range(5):
            random.seed(100 + i)
            radius_variations = [random.randint(-5, 5) for _ in range(8)]
            crater_positions = [
                (random.uniform(0, 2*math.pi), random.uniform(0.2, 0.4)) 
                for _ in range(3)
            ]
            
            obstacle = {
                'type': 'asteroid',
                'x': self.width + random.randint(100, 500) + i * 200,
                'y': random.randint(50, self.height - 50),
                'size': random.randint(30, 60),
                'speed': random.uniform(3, 5),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-3, 3),
                'radius_variations': radius_variations,
                'crater_positions': crater_positions
            }
            self.obstacles.append(obstacle)
        
        # Create planets
        for i in range(3):
            random.seed(200 + i)
            obstacle = {
                'type': 'planet',
                'x': self.width + random.randint(300, 800) + i * 400,
                'y': random.randint(100, self.height - 100),
                'size': random.randint(70, 100),
                'speed': random.uniform(1.5, 2.5),
                'planet_id': (i % 3) + 1  # ✅ SỬA: dùng planet_id thay vì planet_img
            }
            self.obstacles.append(obstacle)
    
    def _check_collision_threat(self, ship, obstacle):
        """Check if obstacle threatens ship"""
        dx = obstacle['x'] - ship['x']
        dy = abs(obstacle['y'] - ship['y'])
        
        if 100 < dx < 250 and dy < 70:
            return True, obstacle['y'] > ship['y']
        return False, False
    
    def _update_ship_path(self, ship):
        """Update ship position based on path type"""
        ship['path_progress'] += 0.02
        
        if ship['path_type'] == 'horizontal':
            ship['x'] += ship['current_speed']
            ship['direction'] = 'right'
            
        elif ship['path_type'] == 'wave':
            ship['x'] += ship['current_speed']
            wave_amplitude = 60
            ship['y'] = ship['start_y'] + math.sin(ship['path_progress'] * 3) * wave_amplitude
            
            wave_slope = math.cos(ship['path_progress'] * 3)
            if wave_slope > 0.3:
                ship['direction'] = 'down'
            elif wave_slope < -0.3:
                ship['direction'] = 'up'
            else:
                ship['direction'] = 'right'
                
        elif ship['path_type'] == 'diagonal':
            ship['x'] += ship['current_speed']
            ship['y'] = ship['start_y'] + (ship['x'] - ship['start_x']) * 0.5
            
            if ship['y'] > self.height - 80:
                ship['start_y'] = self.height - 80
                ship['start_x'] = ship['x']
                ship['direction'] = 'up'
            elif ship['y'] < 80:
                ship['start_y'] = 80
                ship['start_x'] = ship['x']
                ship['direction'] = 'down'
            else:
                ship['direction'] = 'right'
    
    def _create_smoke_particle(self, ship):
        """Create smoke particle behind ship"""
        offset_x = 0
        offset_y = 0
        
        if ship['direction'] == 'right':
            offset_x = -ship['size'] // 2
        elif ship['direction'] == 'left':
            offset_x = ship['size'] // 2
        elif ship['direction'] == 'up':
            offset_y = ship['size'] // 2
        elif ship['direction'] == 'down':
            offset_y = -ship['size'] // 2
        
        particle = {
            'x': ship['x'] + offset_x + random.uniform(-5, 5),
            'y': ship['y'] + offset_y + random.uniform(-5, 5),
            'size': random.uniform(3, 8),
            'alpha': 200,
            'life': 1.0,
            'vel_x': random.uniform(-0.5, 0.5),
            'vel_y': random.uniform(-0.5, 0.5)
        }
        ship['smoke_particles'].append(particle)
    
    def _update_smoke_particles(self, ship):
        """Update smoke particles"""
        for particle in ship['smoke_particles'][:]:
            particle['life'] -= 0.02
            particle['alpha'] = int(200 * particle['life'])
            particle['size'] *= 1.05
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            
            if particle['life'] <= 0:
                ship['smoke_particles'].remove(particle)
    
    def _draw_smoke_particles(self, screen, ship):
        """Draw smoke particles using cache"""
        for particle in ship['smoke_particles']:
            if particle['alpha'] > 0:
                cached_size = round(particle['size'])
                cached_size = max(3, min(15, cached_size))  # Clamp to cache range
                
                if cached_size in self.smoke_cache:
                    smoke_surf = self.smoke_cache[cached_size].copy()
                    smoke_surf.set_alpha(particle['alpha'])
                    screen.blit(
                        smoke_surf, 
                        (int(particle['x'] - particle['size']), 
                         int(particle['y'] - particle['size']))
                    )
    
    def _draw_space_background(self, screen):
        """Draw space background with moving stars"""
        screen.blit(self.background_surf, (0, 0))
        
        # Update star positions
        for star in self.background_stars:
            star[0] -= star[3]
            if star[0] < 0:
                star[0] = self.width + 10
                star[1] = random.randint(0, self.height)
        
        # Draw stars with twinkling
        for star in self.background_stars:
            x, y, size, speed, brightness = star
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
                
            twinkle = math.sin(self.frame * 0.1 + x * 0.01) * 30
            actual_brightness = max(50, min(255, brightness + twinkle))
            color = (actual_brightness, actual_brightness, actual_brightness)
            
            if size == 1:
                screen.set_at((int(x), int(y)), color)
            else:
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
    
    def _draw_obstacle(self, screen, obstacle):
        """Draw asteroid or planet"""
        x, y = int(obstacle['x']), int(obstacle['y'])
        size = obstacle['size']
        
        if obstacle['type'] == 'asteroid':
            self._draw_asteroid(screen, obstacle, x, y, size)
        else:
            self._draw_planet(screen, obstacle, x, y, size)
    
    def _draw_asteroid(self, screen, obstacle, x, y, size):
        """Draw asteroid with 3D effect"""
        rotation = obstacle['rotation']
        colors = [(100, 100, 100), (120, 120, 120), (80, 80, 80)]
        
        # Create polygon points
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi + math.radians(rotation)
            radius_var = size // 2 + obstacle['radius_variations'][i]
            px = x + math.cos(angle) * radius_var
            py = y + math.sin(angle) * radius_var
            points.append((px, py))
        
        # Draw shadow
        shadow_points = [(px + 3, py + 3) for px, py in points]
        pygame.draw.polygon(screen, (30, 30, 30), shadow_points)
        
        # Draw asteroid body
        pygame.draw.polygon(screen, colors[0], points)
        
        # Draw craters
        for crater_angle, crater_radius_factor in obstacle['crater_positions']:
            adjusted_angle = crater_angle + math.radians(rotation)
            crater_x = x + math.cos(adjusted_angle) * (size * crater_radius_factor)
            crater_y = y + math.sin(adjusted_angle) * (size * crater_radius_factor)
            pygame.draw.circle(
                screen, 
                (60, 60, 60), 
                (int(crater_x), int(crater_y)), 
                size // 8
            )
    
    def _draw_planet(self, screen, obstacle, x, y, size):
        """Draw planet using asset_loader"""
        planet_id = obstacle['planet_id']
        planet_img = self._get_planet_scaled(planet_id, size)
        
        if planet_img:
            # Draw glow
            glow_key = (size, 40)
            if glow_key in self.glow_cache:
                screen.blit(
                    self.glow_cache[glow_key], 
                    (x - size//2 - 10, y - size//2 - 10)
                )
            
            # Draw planet
            planet_rect = planet_img.get_rect(center=(x, y))
            screen.blit(planet_img, planet_rect)
        else:
            # Fallback: draw colored circle
            colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
            color = colors[(planet_id - 1) % len(colors)]
            pygame.draw.circle(screen, color, (x, y), size//2)
    
    def _draw_spaceship(self, screen, ship):
        """Draw spaceship using asset_loader images"""
        try:
            spaceship_id = ship['spaceship_id']
            direction_key = ship['direction']
            
            if spaceship_id in self.spaceship_images:
                rotated_images = self.spaceship_images[spaceship_id]
                ship_img = rotated_images.get(direction_key, rotated_images.get(None))
                
                if ship_img:
                    # Scale to ship size
                    ship_img = pygame.transform.scale(ship_img, (ship['size'], ship['size']))
                    ship_rect = ship_img.get_rect(center=(int(ship['x']), int(ship['y'])))
                    
                    # Draw glow
                    glow_intensity = 60 if ship['boost_timer'] <= 0 else 120
                    glow_key = (ship['size'], glow_intensity)
                    if glow_key in self.glow_cache:
                        screen.blit(
                            self.glow_cache[glow_key], 
                            (ship['x'] - ship['size']//2 - 15, 
                             ship['y'] - ship['size']//2 - 15)
                        )
                    
                    # Draw spaceship
                    screen.blit(ship_img, ship_rect)
                    
                    # Draw trail
                    self._draw_ship_trail(screen, ship)
                else:
                    raise Exception("No image for direction")
            else:
                raise Exception("Spaceship ID not found")
                
        except Exception as e:
            # Fallback: draw simple circle
            pygame.draw.circle(
                screen, 
                (100, 200, 255), 
                (int(ship['x']), int(ship['y'])), 
                ship['size']//2
            )
    
    def _draw_ship_trail(self, screen, ship):
        """Draw ship trail effect"""
        trail_length = 6 if ship['boost_timer'] <= 0 else 12
        
        for i in range(trail_length):
            trail_alpha = int((i / trail_length) * (80 if ship['boost_timer'] <= 0 else 150))
            cached_alpha = (trail_alpha // 10) * 10
            
            # Calculate trail position based on direction
            if ship['direction'] == 'right':
                trail_x = ship['x'] - i * 10
                trail_y = ship['y']
            elif ship['direction'] == 'left':
                trail_x = ship['x'] + i * 10
                trail_y = ship['y']
            elif ship['direction'] == 'up':
                trail_x = ship['x']
                trail_y = ship['y'] + i * 10
            else:  # down
                trail_x = ship['x']
                trail_y = ship['y'] - i * 10
            
            # Draw cached trail
            if cached_alpha in self.trail_cache:
                screen.blit(self.trail_cache[cached_alpha], (trail_x - 5, trail_y - 5))
    
    def update(self):
        """Update animation state"""
        if self.transitioning:
            self.transition_progress += 0.02
            if self.transition_progress >= 1.0:
                self.finished = True
            return
        
        self.frame += 1
        
        # Update spaceships
        for ship in self.spaceships:
            # Check for threats
            threat_detected = False
            for obstacle in self.obstacles:
                is_threat, _ = self._check_collision_threat(ship, obstacle)
                if is_threat:
                    threat_detected = True
                    break
            
            # Boost if threat detected
            if threat_detected and ship['boost_timer'] <= 0:
                ship['boost_timer'] = 30
                ship['current_speed'] = ship['max_speed']
            
            # Update boost and smoke
            if ship['boost_timer'] > 0:
                ship['boost_timer'] -= 1
                ship['current_speed'] = ship['max_speed']
                if self.frame % 2 == 0:
                    self._create_smoke_particle(ship)
            else:
                ship['current_speed'] = ship['base_speed']
            
            # Update path
            self._update_ship_path(ship)
            self._update_smoke_particles(ship)
            
            # Wrap around screen
            if ship['x'] > self.width + 100:
                ship['x'] = -100
                ship['path_progress'] = 0
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle['x'] -= obstacle['speed']
            
            if obstacle['type'] == 'asteroid':
                obstacle['rotation'] += obstacle['rotation_speed']
            
            if obstacle['x'] < -200:
                self.obstacles.remove(obstacle)
        
        # Spawn new obstacles
        while len(self.obstacles) < 5:
            obstacle_id = len(self.obstacles) + self.frame
            if random.random() < 0.7:
                # Spawn asteroid
                random.seed(1000 + obstacle_id)
                radius_variations = [random.randint(-5, 5) for _ in range(8)]
                crater_positions = [
                    (random.uniform(0, 2*math.pi), random.uniform(0.2, 0.4)) 
                    for _ in range(3)
                ]
                
                obstacle = {
                    'type': 'asteroid',
                    'x': self.width + random.randint(100, 300),
                    'y': random.randint(50, self.height - 50),
                    'size': random.randint(30, 60),
                    'speed': random.uniform(3, 5),
                    'rotation': random.uniform(0, 360),
                    'rotation_speed': random.uniform(-3, 3),
                    'radius_variations': radius_variations,
                    'crater_positions': crater_positions
                }
            else:
                # Spawn planet
                random.seed(2000 + obstacle_id)
                obstacle = {
                    'type': 'planet',
                    'x': self.width + random.randint(200, 400),
                    'y': random.randint(100, self.height - 100),
                    'size': random.randint(70, 100),
                    'speed': random.uniform(1.5, 2.5),
                    'planet_id': random.randint(1, 3)  # ✅ SỬA
                }
            self.obstacles.append(obstacle)
    
    def draw(self, screen):
        """Draw intro animation"""
        # Draw background
        self._draw_space_background(screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            self._draw_obstacle(screen, obstacle)
        
        # Draw smoke particles
        for ship in self.spaceships:
            self._draw_smoke_particles(screen, ship)
        
        # Draw spaceships
        for ship in self.spaceships:
            self._draw_spaceship(screen, ship)
        
        # Draw title and instruction (with fade-in)
        if self.frame > 30:
            fade_progress = min((self.frame - 30) / 60.0, 1.0)
            alpha = int(255 * fade_progress)
            
            # Draw title
            if self.title_surf:
                title_copy = self.title_surf.copy()
                title_copy.set_alpha(alpha)
                title_rect = title_copy.get_rect(center=(self.width // 2, 100))
                screen.blit(title_copy, title_rect)
            
            # Draw instruction (with pulse)
            if fade_progress >= 1.0:
                pulse_alpha = int(200 + 55 * math.sin(self.frame * 0.1))
                if self.instruction_surf:
                    inst_copy = self.instruction_surf.copy()
                    inst_copy.set_alpha(pulse_alpha)
                    inst_rect = inst_copy.get_rect(
                        center=(self.width // 2, self.height - 80)
                    )
                    screen.blit(inst_copy, inst_rect)
        
        # Draw transition fade
        if self.transitioning:
            fade_alpha = int(255 * self.transition_progress)
            fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, fade_alpha))
            screen.blit(fade_surf, (0, 0))
    
    def start_transition(self):
        """Start transition to main game"""
        self.transitioning = True
    
    def is_finished(self):
        """Check if intro is finished"""
        return self.finished


# ===== GLOBAL FUNCTIONS =====

_intro_instance = None

def get_intro_animation(width, height):
    """Get or create intro animation instance"""
    global _intro_instance
    if _intro_instance is None:
        _intro_instance = IntroAnimation(width, height)
    return _intro_instance

def reset_intro():
    """Reset intro animation"""
    global _intro_instance
    _intro_instance = None