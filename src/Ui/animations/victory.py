# -*- coding: utf-8 -*-
import pygame
import random
import math
import colorsys
from config import *
from manager.font_manager import get_font_manager
import pygame
import math
import random
import time

# Import font manager và asset manager
from ..player.spaceship import load_spaceship_image, spaceship_rotated_images as ship_imgs
from manager.asset_manager import get_spaceship_for_player

# Vẽ hiệu ứng victory
def draw_cosmic_victory(screen, width, height, frame, algorithm_name=None, steps_count=None, execution_time=None):
    """Vẽ hiệu ứng victory với thông tin thuật toán"""
    center = (width // 2, height // 2)
    
    # 1. Deep Space Gradient Background
    for y in range(height):
        ratio = y / height
        r = int(5 * (1 - ratio) + 25 * ratio)
        g = int(2 * (1 - ratio) + 15 * ratio)
        b = int(15 * (1 - ratio) + 45 * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

    # 2. Background Stars Field
    if not hasattr(draw_cosmic_victory, 'background_stars'):
        draw_cosmic_victory.background_stars = []
        random.seed(42)
        for _ in range(80):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            speed = random.uniform(0.2, 1.5)
            brightness = random.randint(80, 255)
            draw_cosmic_victory.background_stars.append([x, y, size, speed, brightness])
    
    # Update moving background stars
    for star in draw_cosmic_victory.background_stars:
        star[0] -= star[3]
        if star[0] < 0:
            star[0] = width + 10
            star[1] = random.randint(0, height)
    
    # Draw moving background stars with twinkling
    for star in draw_cosmic_victory.background_stars:
        x, y, size, speed, brightness = star
        twinkle = math.sin(frame * 0.1 + x * 0.01) * 30
        actual_brightness = max(50, min(255, brightness + twinkle))
        color = (actual_brightness, actual_brightness, actual_brightness)
        
        if size == 1:
            if 0 <= int(x) < width and 0 <= int(y) < height:
                screen.set_at((int(x), int(y)), color)
        else:
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
            if size >= 2:
                pygame.draw.line(screen, color, 
                               (int(x-size-1), int(y)), 
                               (int(x+size+1), int(y)), 1)
                pygame.draw.line(screen, color, 
                               (int(x), int(y-size-1)), 
                               (int(x), int(y+size+1)), 1)

    # 2.1. Additional Distant Twinkling Stars
    random.seed(43)
    for _ in range(30):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.uniform(0.4, 0.8)
        twinkle = abs(math.sin(frame * 0.03 + x * 0.01 + y * 0.01))
        alpha = int(brightness * twinkle * 150)
        color = random.choice([(255,255,255), (200,220,255)])
        star_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (*color, alpha), (1, 1), 1)
        screen.blit(star_surf, (x-1, y-1))

    # 2.3. Flying Stars
    random.seed(33)
    for i in range(8):
        star_time = (frame + i * 35) * 0.018
        progress = (star_time % 5.0) / 5.0
        
        if progress < 0.9:
            start_x = width + 30
            end_x = -30
            fly_x = start_x + (end_x - start_x) * progress
            
            heights = []
            for j in range(8):
                heights.append(height * (0.1 + (j * 0.1) % 0.8))
            fly_y = heights[i]
            
            wave_offset = 12 * math.sin(progress * math.pi * 2.5 + i * 0.8)
            fly_y += wave_offset
            
            if -10 <= fly_x <= width + 10 and 0 <= fly_y <= height:
                star_size = random.choice([1, 2, 3])
                
                twinkle = math.sin(frame * 0.1 + fly_x * 0.01 + i) * 30
                base_brightness = random.randint(100, 255)
                actual_brightness = max(50, min(255, base_brightness + twinkle))
                color = (actual_brightness, actual_brightness, actual_brightness)
                
                if star_size == 1:
                    if 0 <= int(fly_x) < width and 0 <= int(fly_y) < height:
                        screen.set_at((int(fly_x), int(fly_y)), color)
                else:
                    pygame.draw.circle(screen, color, (int(fly_x), int(fly_y)), star_size)
                    if star_size >= 2:
                        pygame.draw.line(screen, color, 
                                       (int(fly_x-star_size-1), int(fly_y)), 
                                       (int(fly_x+star_size+1), int(fly_y)), 1)
                        pygame.draw.line(screen, color, 
                                       (int(fly_x), int(fly_y-star_size-1)), 
                                       (int(fly_x), int(fly_y+star_size+1)), 1)

    # 2.5. Shooting Stars
    if not hasattr(draw_cosmic_victory, 'shooting_stars'):
        draw_cosmic_victory.shooting_stars = []
        for _ in range(4):
            x = width + random.randint(50, 200)
            y = random.randint(50, height - 50)
            speed = random.uniform(3, 6)
            length = random.randint(30, 60)
            brightness = random.randint(180, 255)
            draw_cosmic_victory.shooting_stars.append([x, y, speed, length, brightness])
    
    # Update and draw shooting stars
    for shooting_star in draw_cosmic_victory.shooting_stars[:]:
        shooting_star[0] -= shooting_star[2]
        shooting_star[1] += shooting_star[2] * 0.3
        
        if shooting_star[0] < -shooting_star[3]:
            draw_cosmic_victory.shooting_stars.remove(shooting_star)
            x = width + random.randint(50, 200)
            y = random.randint(50, height - 50)
            speed = random.uniform(3, 6)
            length = random.randint(30, 60)
            brightness = random.randint(180, 255)
            draw_cosmic_victory.shooting_stars.append([x, y, speed, length, brightness])
    
    # Draw shooting stars with trail
    for shooting_star in draw_cosmic_victory.shooting_stars:
        x, y, speed, length, brightness = shooting_star
        for i in range(length):
            trail_x = x + i * 2
            trail_y = y - i * 0.6
            trail_brightness = max(0, brightness - i * 4)
            if 0 <= trail_x <= width and 0 <= trail_y <= height and trail_brightness > 0:
                trail_color = (trail_brightness, trail_brightness // 2, trail_brightness // 3)
                if i < 5:
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (int(trail_x), int(trail_y)), 2)
                else:
                    if int(trail_x) >= 0 and int(trail_x) < width and int(trail_y) >= 0 and int(trail_y) < height:
                        screen.set_at((int(trail_x), int(trail_y)), trail_color)

    # VICTORY DISPLAY - bắt đầu ngay từ frame 0
    victory_frame = frame
    
    # 2.6. Enhanced Background Stars for Victory
    if not hasattr(draw_cosmic_victory, 'victory_background_stars'):
        draw_cosmic_victory.victory_background_stars = []
        random.seed(99)
        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            speed = random.uniform(0.3, 1.8)
            brightness = random.randint(120, 255)
            draw_cosmic_victory.victory_background_stars.append([x, y, size, speed, brightness])
    
    # Update moving victory background stars
    for star in draw_cosmic_victory.victory_background_stars:
        star[0] -= star[3]
        if star[0] < 0:
            star[0] = width + 10
            star[1] = random.randint(0, height)
    
    # Draw enhanced moving background stars for victory
    for star in draw_cosmic_victory.victory_background_stars:
        x, y, size, speed, brightness = star
        twinkle = math.sin(victory_frame * 0.12 + x * 0.01) * 35
        actual_brightness = max(70, min(255, brightness + twinkle))
        
        if (int(x + y + victory_frame // 15)) % 6 == 0:
            color = (actual_brightness, int(actual_brightness * 0.95), int(actual_brightness * 0.8))
        else:
            color = (actual_brightness, actual_brightness, actual_brightness)
        
        if size == 1:
            if 0 <= int(x) < width and 0 <= int(y) < height:
                screen.set_at((int(x), int(y)), color)
        else:
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
            if size >= 2:
                pygame.draw.line(screen, color, 
                               (int(x-size-1), int(y)), 
                               (int(x+size+1), int(y)), 1)
                pygame.draw.line(screen, color, 
                               (int(x), int(y-size-1)), 
                               (int(x), int(y+size+1)), 1)
    
    # 2.7. Victory Shooting Stars
    if not hasattr(draw_cosmic_victory, 'victory_shooting_stars'):
        draw_cosmic_victory.victory_shooting_stars = []
        for _ in range(6):
            x = width + random.randint(50, 200)
            y = random.randint(30, height - 30)
            speed = random.uniform(4, 8)
            length = random.randint(40, 80)
            brightness = random.randint(200, 255)
            draw_cosmic_victory.victory_shooting_stars.append([x, y, speed, length, brightness])
    
    # Update and draw victory shooting stars
    for shooting_star in draw_cosmic_victory.victory_shooting_stars[:]:
        shooting_star[0] -= shooting_star[2]
        shooting_star[1] += shooting_star[2] * 0.4
        
        if shooting_star[0] < -shooting_star[3]:
            draw_cosmic_victory.victory_shooting_stars.remove(shooting_star)
            x = width + random.randint(50, 200)
            y = random.randint(30, height - 30)
            speed = random.uniform(4, 8)
            length = random.randint(40, 80)
            brightness = random.randint(200, 255)
            draw_cosmic_victory.victory_shooting_stars.append([x, y, speed, length, brightness])
    
    # Draw victory shooting stars with enhanced trail
    for shooting_star in draw_cosmic_victory.victory_shooting_stars:
        x, y, speed, length, brightness = shooting_star
        for i in range(length):
            trail_x = x + i * 2.2
            trail_y = y - i * 0.7
            trail_brightness = max(0, brightness - i * 3)
            if 0 <= trail_x <= width and 0 <= trail_y <= height and trail_brightness > 0:
                if i < 8:
                    head_color = (255, 255, 200) if i < 3 else (255, 255, 255)
                    pygame.draw.circle(screen, head_color, 
                                     (int(trail_x), int(trail_y)), 2)
                else:
                    golden_factor = min(1.0, trail_brightness / 200.0)
                    trail_color = (
                        trail_brightness, 
                        int(trail_brightness * 0.8 * golden_factor), 
                        int(trail_brightness * 0.4)
                    )
                    if int(trail_x) >= 0 and int(trail_x) < width and int(trail_y) >= 0 and int(trail_y) < height:
                        screen.set_at((int(trail_x), int(trail_y)), trail_color)
    
    # 3. Background cosmic effects - Cosmic Portal
    portal_radius = 35 + 12 * math.sin(victory_frame * 0.06)
    
    # Create gradient portal effect
    for layer in range(15):
        layer_radius = portal_radius * (1.0 - layer * 0.06)
        if layer_radius > 0:
            color_progress = layer / 15.0
            
            r = int(20 + (180 * color_progress))
            g = int(40 + (200 * color_progress))
            b = int(120 + (135 * color_progress))
            alpha = int(60 + (40 * (1 - color_progress)))
            
            portal_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(portal_surf, (r, g, b, alpha), center, int(layer_radius))
            screen.blit(portal_surf, (0, 0))
    
    # Rotating energy rings around portal
    for ring_idx in range(4):
        ring_radius = portal_radius + 15 + ring_idx * 12
        rotation_speed = 0.03 + ring_idx * 0.01
        ring_alpha = max(20, 60 - ring_idx * 15)
        
        angle_offset = victory_frame * rotation_speed + ring_idx * 1.57
        
        ring_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for segment in range(8):
            segment_angle = (segment * 0.785) + angle_offset
            start_x = center[0] + math.cos(segment_angle) * ring_radius
            start_y = center[1] + math.sin(segment_angle) * ring_radius
            
            color_intensity = 150 + ring_idx * 25
            ring_color = (100 + ring_idx * 20, color_intensity, 255, ring_alpha)
            
            if 0 <= start_x < width and 0 <= start_y < height:
                pygame.draw.circle(ring_surf, ring_color, (int(start_x), int(start_y)), 2)
        
        screen.blit(ring_surf, (0, 0))

    # Subtle energy rings
    for ring in range(2):
        ring_radius = 180 + ring * 80 + 15 * math.sin(victory_frame * 0.08 + ring)
        ring_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        alpha = max(12, 35 - ring * 12)
        color = (60 + ring * 30, 100 + ring * 40, 200, alpha)
        pygame.draw.circle(ring_surf, color, center, int(ring_radius), 1)
        screen.blit(ring_surf, (0, 0))

    # Enhanced quantum particles
    for particle_idx in range(25):
        orbit_radius = 80 + (particle_idx % 5) * 15
        orbit_speed = 0.02 + (particle_idx % 3) * 0.01
        angle = victory_frame * orbit_speed + particle_idx * 0.25
        
        x = center[0] + math.cos(angle) * orbit_radius
        y = center[1] + math.sin(angle) * orbit_radius
        
        drift_x = 10 * math.sin(victory_frame * 0.03 + particle_idx)
        drift_y = 8 * math.cos(victory_frame * 0.04 + particle_idx * 0.7)
        x += drift_x
        y += drift_y
        
        if 0 <= x < width and 0 <= y < height:
            quantum_alpha = int(60 + 40 * abs(math.sin(victory_frame * 0.15 + angle)))
            
            color_type = particle_idx % 4
            if color_type == 0:
                color = (120, 180, 255)
            elif color_type == 1:
                color = (180, 120, 255)
            elif color_type == 2:
                color = (120, 255, 220)
            else:
                color = (255, 180, 120)
            
            particle_size = 1 + (particle_idx % 3)
            pygame.draw.circle(screen, (*color, quantum_alpha), (int(x), int(y)), particle_size)

    # 4. Final spaceship position
    final_ship_y = center[1] - 120
    try:
        # Load spaceship directly from asset manager
        ship_imgs_loaded = get_spaceship_for_player(size=50, cache=True)
        if not ship_imgs_loaded:
            # Fallback: try loading from spaceship module
            load_spaceship_image()
            ship_imgs_loaded = ship_imgs
        
        if victory_frame < 120:
            flight_progress = victory_frame / 120.0
            side_amplitude = 80 * (1 - flight_progress)
            side_movement = side_amplitude * math.sin(victory_frame * 0.15)
            
            hover_offset = 8 * math.sin(victory_frame * 0.12)
            
            ship_x = center[0] + side_movement
            ship_y = final_ship_y + hover_offset
            
            if victory_frame < 100:
                if math.sin(victory_frame * 0.15) > 0:
                    direction = "right"
                else:
                    direction = "left"
            else:
                direction = "up"
        else:
            hover_offset = 3 * math.sin(victory_frame * 0.1)
            ship_x = center[0]
            ship_y = final_ship_y + hover_offset
            direction = "up"
        
        ship_img = ship_imgs_loaded.get(direction)
        if ship_img is None:
            ship_img = ship_imgs_loaded.get(None)
            
        if ship_img is not None:
            # Ship image đã được scale sẵn từ asset_manager
            ship_rect = ship_img.get_rect(center=(int(ship_x), int(ship_y)))
            
            glow_surf = pygame.Surface((ship_rect.width + 30, ship_rect.height + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (150, 200, 255, 100), glow_surf.get_rect())
            screen.blit(glow_surf, (ship_rect.x - 15, ship_rect.y - 15))
            
            outline_surf = pygame.Surface((ship_rect.width + 4, ship_rect.height + 4), pygame.SRCALPHA)
            outline_img = pygame.transform.scale(ship_img, (ship_rect.width + 4, ship_rect.height + 4))
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx*dx + dy*dy <= 4:
                        outline_surf.blit(outline_img, (dx+2, dy+2))
            
            outline_surf.fill((255, 255, 255, 80), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(outline_surf, (ship_rect.x - 2, ship_rect.y - 2))
            
            screen.blit(ship_img, ship_rect)
        else:
            ship_x = center[0]
            if victory_frame < 120:
                side_movement = 80 * (1 - victory_frame/120.0) * math.sin(victory_frame * 0.15)
                ship_x += side_movement
            hover_offset = 5 * math.sin(victory_frame * 0.1)
            pygame.draw.circle(screen, (100, 200, 255), (int(ship_x), int(final_ship_y + hover_offset)), 12)
    except Exception as e:
        ship_x = center[0]
        if victory_frame < 120:
            side_movement = 80 * (1 - victory_frame/120.0) * math.sin(victory_frame * 0.15)
            ship_x += side_movement
        hover_offset = 5 * math.sin(victory_frame * 0.1)
        pygame.draw.circle(screen, (100, 200, 255), (int(ship_x), int(final_ship_y + hover_offset)), 12)

    # 5. VICTORY TEXT
    if victory_frame > 30:
        text_progress = min((victory_frame - 30) / 60.0, 1.0)
        
        base_scale = 0.5 + text_progress * 0.5
        pulse_scale = 0.03 * math.sin(victory_frame * 0.08)
        scale_pulse = base_scale + pulse_scale
        
        text_alpha = int(255 * text_progress)
        
        victory_text = get_font_manager().render_text(
            "YOU WIN!",
            size=88,
            color=(255, 255, 200),
            bold=True,
            shadow=True,
            glow=True
        )
        
        cosmic_text = pygame.transform.rotozoom(victory_text, 0, scale_pulse)
        cosmic_text.set_alpha(text_alpha)
        text_rect = cosmic_text.get_rect(center=(center[0], center[1] + 20))
        screen.blit(cosmic_text, text_rect)

        # 6. Instruction text
        if text_progress >= 1.0:
            instruction_alpha = int(200 + 55 * math.sin(victory_frame * 0.12))
            
            text_bg = pygame.Surface((width, 80), pygame.SRCALPHA)
            text_bg.fill((0, 0, 0, 80))
            screen.blit(text_bg, (0, center[1] + 100))
            
            main_text = "CLICK anywhere or SPACE để tiếp tục"
            instruction_text = get_font_manager().render_text(
                main_text,
                size=24,
                color=(220, 220, 255),
                shadow=True
            )
            instruction_text.set_alpha(instruction_alpha)
            instruction_rect = instruction_text.get_rect(center=(center[0], center[1] + 120))
            screen.blit(instruction_text, instruction_rect)
            
            hint_text = "R - Chơi lại level • ESC - Về menu"
            hint_surface = get_font_manager().render_text(  
                hint_text,
                size=20,
                color=(180, 180, 220),
                shadow=True
            )
            hint_surface.set_alpha(instruction_alpha - 50)
            hint_rect = hint_surface.get_rect(center=(center[0], center[1] + 150))
            screen.blit(hint_surface, hint_rect)
            
            # 7. Algorithm Information Panel - với hiệu ứng đẹp
            if algorithm_name and steps_count is not None:
                info_alpha = int(180 + 50 * math.sin(victory_frame * 0.08))
                
                # Panel background với hiệu ứng gradient và glow (optimized)
                panel_width = 380
                panel_height = 160
                panel_x = center[0] - panel_width // 2
                panel_y = center[1] + 200
                
                # Cache gradient background (chỉ tạo 1 lần)
                if not hasattr(draw_cosmic_victory, 'cached_panel_bg'):
                    draw_cosmic_victory.cached_panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                    # Tạo gradient 1 lần
                    for y in range(panel_height):
                        gradient_ratio = y / panel_height
                        r = int(15 + 35 * gradient_ratio)
                        g = int(25 + 45 * gradient_ratio) 
                        b = int(45 + 65 * gradient_ratio)
                        alpha = int(120 + 40 * (1 - gradient_ratio))
                        pygame.draw.line(draw_cosmic_victory.cached_panel_bg, (r, g, b, alpha), (0, y), (panel_width, y))
                
                # Copy cached background
                panel_surface = draw_cosmic_victory.cached_panel_bg.copy()
                
                # Simple breathing effect (chỉ thay đổi alpha)
                breathing_alpha = int(20 * math.sin(victory_frame * 0.05))
                if breathing_alpha != 0:
                    breathing_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                    breathing_surface.fill((40, 60, 80, abs(breathing_alpha)))
                    panel_surface.blit(breathing_surface, (0, 0))
                
                # Simplified border (ít tính toán hơn)
                border_intensity = int(120 + 60 * math.sin(victory_frame * 0.12))
                border_color = (100, 200, 255)  # Static color
                
                # Chỉ 3 border layers thay vì 6
                for thickness in [3, 2, 1]:
                    glow_alpha = border_intensity // (thickness + 1)
                    border_rect = pygame.Rect(thickness, thickness, 
                                            panel_width - 2*thickness, 
                                            panel_height - 2*thickness)
                    pygame.draw.rect(panel_surface, (*border_color, glow_alpha), border_rect, 1)
                
                screen.blit(panel_surface, (panel_x, panel_y))
                
                # Simplified sparkles (ít particles hơn, đơn giản hơn)
                if not hasattr(draw_cosmic_victory, 'panel_sparkles'):
                    draw_cosmic_victory.panel_sparkles = []
                    for _ in range(8):  # Giảm từ 15 xuống 8
                        spark_x = random.randint(panel_x + 15, panel_x + panel_width - 15)
                        spark_y = random.randint(panel_y + 15, panel_y + panel_height - 15)
                        spark_life = random.randint(60, 120)
                        draw_cosmic_victory.panel_sparkles.append([spark_x, spark_y, spark_life, spark_life])
                
                # Simple sparkle update (bỏ physics phức tạp)
                for sparkle in draw_cosmic_victory.panel_sparkles[:]:
                    sparkle[2] -= 1  # Decrease life
                    
                    # Simple respawn
                    if sparkle[2] <= 0:
                        sparkle[0] = random.randint(panel_x + 15, panel_x + panel_width - 15)
                        sparkle[1] = random.randint(panel_y + 15, panel_y + panel_height - 15)
                        sparkle[2] = sparkle[3]  # Reset to max life
                    
                    # Simple sparkle render (bỏ rainbow)
                    life_ratio = sparkle[2] / sparkle[3]
                    sparkle_alpha = int(255 * life_ratio * (math.sin(victory_frame * 0.3) * 0.5 + 0.5))
                    
                    if sparkle_alpha > 0:
                        sparkle_color = (255, 255, 150)  # Static golden color
                        pygame.draw.circle(screen, sparkle_color, 
                                         (int(sparkle[0]), int(sparkle[1])), 2)
                
                # Simplified typing effect (ít tính toán hơn)
                typing_speed = 2  # Giảm speed
                text_reveal_frame = max(0, victory_frame - 60)
                
                # Cache text để tránh render lại mỗi frame
                if not hasattr(draw_cosmic_victory, 'cached_texts'):
                    draw_cosmic_victory.cached_texts = {}
                    draw_cosmic_victory.last_reveal_frame = -1
                
                # Chỉ update khi reveal frame thay đổi đáng kể
                if text_reveal_frame // 5 != draw_cosmic_victory.last_reveal_frame // 5:
                    draw_cosmic_victory.last_reveal_frame = text_reveal_frame
                    
                    # Algorithm name
                    algorithm_display = "Manual Play" if algorithm_name == "Player" else algorithm_name
                    full_algorithm_text = f"Algorithm: {algorithm_display}"
                    revealed_chars = min(len(full_algorithm_text), text_reveal_frame * typing_speed // 10)
                    draw_cosmic_victory.cached_texts['algorithm'] = full_algorithm_text[:revealed_chars]
                    
                    # Steps count
                    full_steps_text = f"Steps: {steps_count}"
                    revealed_chars = min(len(full_steps_text), max(0, text_reveal_frame - 20) * typing_speed // 10)
                    draw_cosmic_victory.cached_texts['steps'] = full_steps_text[:revealed_chars]
                    
                    # Execution time
                    if execution_time is not None:
                        time_display = f"{execution_time:.1f} ms" if execution_time > 0 else "N/A"
                        full_time_text = f"Time: {time_display}"
                        revealed_chars = min(len(full_time_text), max(0, text_reveal_frame - 40) * typing_speed // 10)
                        draw_cosmic_victory.cached_texts['time'] = full_time_text[:revealed_chars]
                
                # Draw cached texts
                if 'algorithm' in draw_cosmic_victory.cached_texts and draw_cosmic_victory.cached_texts['algorithm']:
                    title_y = panel_y + 30
                    algorithm_text = get_font_manager().render_text(
                        draw_cosmic_victory.cached_texts['algorithm'],
                        size=26, color=(255, 230, 120), bold=True, shadow=True
                    )
                    algorithm_text.set_alpha(info_alpha)
                    float_offset = 2 * math.sin(victory_frame * 0.06)
                    algorithm_rect = algorithm_text.get_rect(center=(center[0], title_y + float_offset))
                    screen.blit(algorithm_text, algorithm_rect)
                
                if 'steps' in draw_cosmic_victory.cached_texts and draw_cosmic_victory.cached_texts['steps']:
                    steps_y = panel_y + 70
                    steps_text = get_font_manager().render_text(
                        draw_cosmic_victory.cached_texts['steps'],
                        size=24, color=(150, 255, 200), bold=True, shadow=True
                    )
                    steps_text.set_alpha(info_alpha)
                    float_offset = 2 * math.sin(victory_frame * 0.06 + 1)
                    steps_rect = steps_text.get_rect(center=(center[0], steps_y + float_offset))
                    screen.blit(steps_text, steps_rect)
                
                if execution_time is not None and 'time' in draw_cosmic_victory.cached_texts and draw_cosmic_victory.cached_texts['time']:
                    time_y = panel_y + 110
                    time_text = get_font_manager().render_text(
                        draw_cosmic_victory.cached_texts['time'],
                        size=24, color=(255, 180, 255), bold=True, shadow=True
                    )
                    time_text.set_alpha(info_alpha)
                    float_offset = 2 * math.sin(victory_frame * 0.06 + 2)
                    time_rect = time_text.get_rect(center=(center[0], time_y + float_offset))
                    screen.blit(time_text, time_rect)
                
                # Simple cursor (bỏ logic phức tạp)
                if text_reveal_frame < 100:  # Hiện cursor trong 100 frame đầu
                    cursor_alpha = int(255 * (math.sin(victory_frame * 0.3) * 0.5 + 0.5))
                    cursor_surface = get_font_manager().render_text(
                        "|", size=24, color=(255, 255, 255), bold=True
                    )
                    cursor_surface.set_alpha(cursor_alpha)
                    cursor_x = center[0] + 100
                    cursor_y = panel_y + 110
                    screen.blit(cursor_surface, (cursor_x, cursor_y))