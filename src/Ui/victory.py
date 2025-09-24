import pygame
import random
import math
from config import *

# Vẽ hiệu ứng victory với spaceship bay qua các hành tinh
def draw_cosmic_victory(screen, width, height, frame):
    """Vẽ hiệu ứng victory với spaceship bay qua các hành tinh"""
    center = (width // 2, height // 2)
    
    # Animation phases based on frame count
    # Phase 1: 0-80 frames - Spaceship flying through planets
    # Phase 2: 80-180 frames - Spaceship stops and shows dialogue
    # Phase 3: 180+ frames - Victory display
    
    # 1. Deep Space Gradient Background
    for y in range(height):
        ratio = y / height
        r = int(5 * (1 - ratio) + 25 * ratio)
        g = int(2 * (1 - ratio) + 15 * ratio)
        b = int(15 * (1 - ratio) + 45 * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

    # 2. Background Stars Field - Like cosmic_selector with moving stars (reduced amount)
    # Create and update moving background stars like cosmic_selector
    if not hasattr(draw_cosmic_victory, 'background_stars'):
        draw_cosmic_victory.background_stars = []
        random.seed(42)
        # Initialize 80 moving background stars (reduced from 150)
        for _ in range(80):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            speed = random.uniform(0.2, 1.5)  # Moving speed like cosmic_selector
            brightness = random.randint(80, 255)
            draw_cosmic_victory.background_stars.append([x, y, size, speed, brightness])
    
    # Update moving background stars like cosmic_selector
    for star in draw_cosmic_victory.background_stars:
        star[0] -= star[3]  # Move left like cosmic_selector
        if star[0] < 0:
            star[0] = width + 10
            star[1] = random.randint(0, height)
    
    # Draw moving background stars with twinkling like cosmic_selector
    for star in draw_cosmic_victory.background_stars:
        x, y, size, speed, brightness = star
        # Add twinkling effect like cosmic_selector
        twinkle = math.sin(frame * 0.1 + x * 0.01) * 30
        actual_brightness = max(50, min(255, brightness + twinkle))
        color = (actual_brightness, actual_brightness, actual_brightness)
        
        if size == 1:
            if 0 <= int(x) < width and 0 <= int(y) < height:
                screen.set_at((int(x), int(y)), color)
        else:
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
            # Add cross for bigger stars like cosmic_selector
            if size >= 2:
                pygame.draw.line(screen, color, 
                               (int(x-size-1), int(y)), 
                               (int(x+size+1), int(y)), 1)
                pygame.draw.line(screen, color, 
                               (int(x), int(y-size-1)), 
                               (int(x), int(y+size+1)), 1)

    # 2.1. Additional Distant Twinkling Stars (reduced amount)
    random.seed(43)
    for _ in range(30):  # Reduced from 60
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.uniform(0.4, 0.8)
        twinkle = abs(math.sin(frame * 0.03 + x * 0.01 + y * 0.01))
        alpha = int(brightness * twinkle * 150)
        color = random.choice([(255,255,255), (200,220,255)])
        star_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (*color, alpha), (1, 1), 1)
        screen.blit(star_surf, (x-1, y-1))

    # 2.3. Flying Stars - Stars like in cosmic_selector style (reduced amount)
    random.seed(33)  # Different seed for flying stars
    for i in range(8):  # Reduced from 12 to 8 flying stars
        # Each star has different timing and path
        star_time = (frame + i * 35) * 0.018  # Offset timing for each star
        
        # Calculate flying star position with looping
        progress = (star_time % 5.0) / 5.0  # Loop every 5 seconds worth of frames
        
        if progress < 0.9:  # Show for 90% of the cycle
            # Stars fly from right to left across the sky
            start_x = width + 30
            end_x = -30
            fly_x = start_x + (end_x - start_x) * progress
            
            # Different heights for different stars
            heights = []
            for j in range(8):  # Changed from 12 to 8
                heights.append(height * (0.1 + (j * 0.1) % 0.8))  # Distribute across screen
            fly_y = heights[i]
            
            # Add gentle wave motion
            wave_offset = 12 * math.sin(progress * math.pi * 2.5 + i * 0.8)
            fly_y += wave_offset
            
            if -10 <= fly_x <= width + 10 and 0 <= fly_y <= height:
                # Flying star properties like cosmic_selector
                star_size = random.choice([1, 2, 3])  # Mix of sizes like cosmic_selector
                
                # Add twinkling effect like cosmic_selector
                twinkle = math.sin(frame * 0.1 + fly_x * 0.01 + i) * 30
                base_brightness = random.randint(100, 255)
                actual_brightness = max(50, min(255, base_brightness + twinkle))
                color = (actual_brightness, actual_brightness, actual_brightness)
                
                # Draw star like cosmic_selector
                if star_size == 1:
                    if 0 <= int(fly_x) < width and 0 <= int(fly_y) < height:
                        screen.set_at((int(fly_x), int(fly_y)), color)
                else:
                    pygame.draw.circle(screen, color, (int(fly_x), int(fly_y)), star_size)
                    # Add cross for bigger stars like cosmic_selector
                    if star_size >= 2:
                        pygame.draw.line(screen, color, 
                                       (int(fly_x-star_size-1), int(fly_y)), 
                                       (int(fly_x+star_size+1), int(fly_y)), 1)
                        pygame.draw.line(screen, color, 
                                       (int(fly_x), int(fly_y-star_size-1)), 
                                       (int(fly_x), int(fly_y+star_size+1)), 1)

    # 2.5. Shooting Stars - Similar to cosmic_selector style
    # Create shooting stars data if not exists (simulate cosmic_selector shooting stars)
    if not hasattr(draw_cosmic_victory, 'shooting_stars'):
        draw_cosmic_victory.shooting_stars = []
        # Initialize shooting stars
        for _ in range(4):
            x = width + random.randint(50, 200)
            y = random.randint(50, height - 50)
            speed = random.uniform(3, 6)
            length = random.randint(30, 60)
            brightness = random.randint(180, 255)
            draw_cosmic_victory.shooting_stars.append([x, y, speed, length, brightness])
    
    # Update and draw shooting stars (cosmic_selector style)
    for shooting_star in draw_cosmic_victory.shooting_stars[:]:
        shooting_star[0] -= shooting_star[2]  # Move left
        shooting_star[1] += shooting_star[2] * 0.3  # Slight downward angle
        
        # Remove and recreate shooting star if off screen
        if shooting_star[0] < -shooting_star[3]:
            draw_cosmic_victory.shooting_stars.remove(shooting_star)
            # Add new shooting star
            x = width + random.randint(50, 200)
            y = random.randint(50, height - 50)
            speed = random.uniform(3, 6)
            length = random.randint(30, 60)
            brightness = random.randint(180, 255)
            draw_cosmic_victory.shooting_stars.append([x, y, speed, length, brightness])
    
    # Draw shooting stars with trail (cosmic_selector style)
    for shooting_star in draw_cosmic_victory.shooting_stars:
        x, y, speed, length, brightness = shooting_star
        # Draw trail
        for i in range(length):
            trail_x = x + i * 2
            trail_y = y - i * 0.6
            trail_brightness = max(0, brightness - i * 4)
            if 0 <= trail_x <= width and 0 <= trail_y <= height and trail_brightness > 0:
                trail_color = (trail_brightness, trail_brightness // 2, trail_brightness // 3)
                if i < 5:  # Bright head
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (int(trail_x), int(trail_y)), 2)
                else:  # Fading trail
                    if int(trail_x) >= 0 and int(trail_x) < width and int(trail_y) >= 0 and int(trail_y) < height:
                        screen.set_at((int(trail_x), int(trail_y)), trail_color)

    if frame < 80:  # PHASE 1: SPACESHIP JOURNEY ANIMATION
        # 3. Draw planets at fixed positions for spaceship to fly through (reduced to 3 planets)
        planet_positions = [
            (width * 0.7, height * 0.3, 90, "planet1.png"),   # Top right
            (width * 0.3, height * 0.5, 100, "planet2.png"),  # Left middle  
            (width * 0.6, height * 0.7, 80, "planet3.png"),   # Right lower
        ]
        
        # Draw planets with gentle glow
        for px, py, size, planet_name in planet_positions:
            try:
                planet_img = pygame.image.load(f"./asset/image/{planet_name}")
                planet_img = pygame.transform.scale(planet_img, (size, size))
                
                # Planet glow
                glow_surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
                glow_color = (100, 150, 200, 40)
                pygame.draw.circle(glow_surf, glow_color, (size//2 + 10, size//2 + 10), size//2 + 10)
                screen.blit(glow_surf, (px - size//2 - 10, py - size//2 - 10))
                
                # Planet itself
                planet_rect = planet_img.get_rect(center=(px, py))
                screen.blit(planet_img, planet_rect)
            except:
                # Fallback: draw colored circle
                colors = [(255,100,100), (100,255,100), (100,100,255), (255,255,100), (255,100,255)]
                color = colors[len(planet_name) % len(colors)]
                pygame.draw.circle(screen, color, (int(px), int(py)), size//2)

        # 4. Spaceship flight path - curvy journey through planets
        journey_progress = frame / 80.0  # Faster journey - changed from 120.0 to 80.0
        
        if journey_progress <= 1.0:
            # Define waypoints for spaceship journey (simplified path for 3 planets)
            waypoints = [
                (-50, height * 0.5),          # Start off-screen left
                (width * 0.2, height * 0.35), # Approach first area
                (width * 0.6, height * 0.25), # Near planet1 (top right)
                (width * 0.4, height * 0.5),  # Near planet2 (left middle)
                (width * 0.55, height * 0.6), # Middle transition
                (width * 0.65, height * 0.75),# Near planet3 (right lower)
                (center[0], center[1] - 50),   # Final position above center
            ]
            
            # Calculate current position using smooth interpolation
            segment_count = len(waypoints) - 1
            segment_progress = journey_progress * segment_count
            segment_index = int(segment_progress)
            local_progress = segment_progress - segment_index
            
            if segment_index < segment_count:
                # Smooth interpolation between waypoints
                start_point = waypoints[segment_index]
                end_point = waypoints[segment_index + 1]
                
                # Ease in-out for smooth movement
                t = local_progress
                t = t * t * (3.0 - 2.0 * t)  # Smoothstep
                
                spaceship_x = start_point[0] + (end_point[0] - start_point[0]) * t
                spaceship_y = start_point[1] + (end_point[1] - start_point[1]) * t
                
                # Calculate direction based on movement
                if local_progress < 0.95:  # Don't calculate direction at very end
                    dx = end_point[0] - start_point[0]
                    dy = end_point[1] - start_point[1]
                    
                    if abs(dx) > abs(dy):
                        direction = "right" if dx > 0 else "left"
                    else:
                        direction = "down" if dy > 0 else "up"
                else:
                    direction = "up"  # Final direction pointing up
                
                # Draw spaceship trail
                trail_length = 8
                for i in range(trail_length):
                    trail_alpha = (i / trail_length) * 100
                    trail_offset = i * 8
                    trail_x = spaceship_x - (end_point[0] - start_point[0]) * 0.02 * i
                    trail_y = spaceship_y - (end_point[1] - start_point[1]) * 0.02 * i
                    
                    trail_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, (100, 200, 255, int(trail_alpha)), (6, 6), 4)
                    screen.blit(trail_surf, (trail_x - 6, trail_y - 6))
                
                # Draw spaceship (larger during journey)
                try:
                    from .spaceship import load_spaceship_image, spaceship_rotated_images as ship_imgs
                    load_spaceship_image()
                    
                    ship_img = ship_imgs.get(direction)
                    if ship_img is None:
                        ship_img = ship_imgs.get(None)
                    
                    if ship_img is not None:
                        # Scale up the spaceship - use fixed size
                        scaled_size = 60  # Fixed size instead of PLAYER_RADIUS * 6
                        ship_img = pygame.transform.scale(ship_img, (scaled_size, scaled_size))
                        ship_rect = ship_img.get_rect(center=(int(spaceship_x), int(spaceship_y)))
                        screen.blit(ship_img, ship_rect)
                        
                        # Engine glow
                    glow_surf = pygame.Surface((scaled_size + 30, scaled_size + 30), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (100, 200, 255, 60), (scaled_size//2 + 15, scaled_size//2 + 15), scaled_size//2 + 15)
                    screen.blit(glow_surf, (spaceship_x - scaled_size//2 - 15, spaceship_y - scaled_size//2 - 15))
                except:
                    # Fallback: simple triangle
                    pygame.draw.circle(screen, (100, 200, 255), (int(spaceship_x), int(spaceship_y)), 15)

        # Show progress text during journey
        if frame < 70:  # Shortened from 100 to 70 for faster journey
            try:
                journey_font = pygame.font.SysFont("Times New Roman", 36, bold=True)
            except:
                try:
                    journey_font = pygame.font.SysFont("Calibri", 36, bold=True)
                except:
                    journey_font = pygame.font.Font(None, 42)
            
            journey_texts = [
                "Exploring the galaxy...",
                "Mission accomplished!", 
            ]
            
            text_index = min(int(journey_progress * len(journey_texts)), len(journey_texts) - 1)
            journey_text = journey_font.render(journey_texts[text_index], True, (200, 220, 255))
            journey_text.set_alpha(int(200 * math.sin(frame * 0.1)))
            text_rect = journey_text.get_rect(center=(center[0], height - 60))
            screen.blit(journey_text, text_rect)

    elif frame < 180:  # PHASE 2: SPACESHIP DIALOGUE PHASE (frame 80-180)
        dialogue_frame = frame - 80  # 0-100 frame for dialogue phase
        
        # 3. Show planets (static during dialogue)
        planet_positions = [
            (width * 0.7, height * 0.3, 90, "planet1.png"),
            (width * 0.3, height * 0.5, 100, "planet2.png"),  
            (width * 0.6, height * 0.7, 80, "planet3.png"),
        ]
        
        for px, py, size, planet_name in planet_positions:
            try:
                planet_img = pygame.image.load(f"./asset/image/{planet_name}")
                planet_img = pygame.transform.scale(planet_img, (size, size))
                
                # Planet glow
                glow_surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
                glow_color = (100, 150, 200, 30)
                pygame.draw.circle(glow_surf, glow_color, (size//2 + 10, size//2 + 10), size//2 + 10)
                screen.blit(glow_surf, (px - size//2 - 10, py - size//2 - 10))
                
                planet_rect = planet_img.get_rect(center=(px, py))
                screen.blit(planet_img, planet_rect)
            except:
                colors = [(255,100,100), (100,255,100), (100,100,255)]
                color = colors[len(planet_name) % len(colors)]
                pygame.draw.circle(screen, color, (int(px), int(py)), size//2)

        # 4. Spaceship stopped at final position with dialogue
        final_ship_y = center[1] - 120
        spaceship_x = center[0]
        spaceship_y = final_ship_y + 3 * math.sin(dialogue_frame * 0.08)  # Gentle hover only
        
        try:
            from .spaceship import load_spaceship_image, spaceship_rotated_images as ship_imgs
            load_spaceship_image()
            
            # Make spaceship larger during dialogue phase
            ship_img = ship_imgs.get("up")
            if ship_img is None:
                ship_img = ship_imgs.get(None)
                
            if ship_img is not None:
                # Scale up the spaceship for dialogue phase
                larger_size = 70  # Fixed size instead of PLAYER_RADIUS * 5
                ship_img = pygame.transform.scale(ship_img, (larger_size, larger_size))
                ship_rect = ship_img.get_rect(center=(int(spaceship_x), int(spaceship_y)))
                
                # Enhanced ship glow for dialogue phase
                glow_surf = pygame.Surface((ship_rect.width + 30, ship_rect.height + 30), pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, (150, 200, 255, 80), glow_surf.get_rect())
                screen.blit(glow_surf, (ship_rect.x - 15, ship_rect.y - 15))
                
                screen.blit(ship_img, ship_rect)
            else:
                raise Exception("No spaceship image")
        except:
            # Fallback - also larger
            pygame.draw.circle(screen, (100, 200, 255), (int(spaceship_x), int(spaceship_y)), 16)  # Increased from 12 to 16

        # 5. Speech bubble with dialogue (Vietnamese - simplified if font issues)
        bubble_messages = [
            "Chinh phục thành công!",
            "Ngân hà đã an toàn!",
            "Sẵn sàng phiêu lưu mới!"
        ]
        
        # Show message based on dialogue_frame
        if dialogue_frame < 35:
            message = bubble_messages[0]
        elif dialogue_frame < 70:
            message = bubble_messages[1] 
        else:
            message = bubble_messages[2]
        
        # Speech bubble position (above spaceship)
        bubble_x = int(spaceship_x)
        bubble_y = int(spaceship_y) - 60
        
        # Create speech bubble (larger font for better visibility)
        try:
            # Try to use a font that supports Vietnamese characters better
            bubble_font = pygame.font.SysFont("Times New Roman", 22, bold=True)  # Increased from 16 to 22, made bold
        except:
            try:
                # Fallback to another common font
                bubble_font = pygame.font.SysFont("Calibri", 22, bold=True)  # Increased from 16 to 22, made bold
            except:
                # Final fallback
                bubble_font = pygame.font.Font(None, 28)  # Increased from 20 to 28
        
        text_surface = bubble_font.render(message, True, (40, 40, 80))  # Darker color for better contrast
        text_rect = text_surface.get_rect()
        
        # Bubble background (larger for bigger text)
        bubble_width = text_rect.width + 30  # Increased padding from 24 to 30
        bubble_height = text_rect.height + 24  # Increased padding from 18 to 24
        bubble_rect = pygame.Rect(bubble_x - bubble_width//2, bubble_y - bubble_height//2, 
                                bubble_width, bubble_height)
        
        # Draw bubble shadow (larger shadow for bigger bubble)
        shadow_rect = bubble_rect.move(3, 3)  # Increased shadow offset from 2,2 to 3,3
        pygame.draw.ellipse(screen, (0, 0, 0, 100), shadow_rect)  # Darker shadow
        
        # Draw bubble (brighter background for better text contrast)
        pygame.draw.ellipse(screen, (250, 250, 255), bubble_rect)  # Brighter background
        pygame.draw.ellipse(screen, (120, 120, 180), bubble_rect, 3)  # Thicker border from 2 to 3
        
        # Draw bubble tail (pointing to spaceship) - larger tail
        tail_points = [
            (bubble_x - 10, bubble_y + bubble_height//2 - 2),  # Wider tail from 8 to 10
            (bubble_x + 10, bubble_y + bubble_height//2 - 2),  # Wider tail from 8 to 10
            (bubble_x, bubble_y + bubble_height//2 + 15)       # Longer tail from 12 to 15
        ]
        pygame.draw.polygon(screen, (250, 250, 255), tail_points)  # Match bubble color
        pygame.draw.polygon(screen, (120, 120, 180), tail_points, 3)  # Thicker border
        
        # Draw text
        text_x = bubble_x - text_rect.width//2
        text_y = bubble_y - text_rect.height//2
        screen.blit(text_surface, (text_x, text_y))
        
        # Typing effect for each message
        message_start_frame = (dialogue_frame // 35) * 35  # Start of current message
        typing_frame = dialogue_frame - message_start_frame
        if typing_frame < 20:  # 20 frames to type each message
            typing_progress = typing_frame / 20.0
            chars_to_show = int(len(message) * typing_progress)
            if chars_to_show < len(message):
                # Add blinking cursor (larger for bigger font)
                cursor_alpha = int(255 * abs(math.sin(dialogue_frame * 0.3)))
                cursor_surface = bubble_font.render("|", True, (80, 80, 120))  # Use "|" instead of "_", darker color
                cursor_surface.set_alpha(cursor_alpha)
                cursor_x = text_x + bubble_font.size(message[:chars_to_show])[0]
                screen.blit(cursor_surface, (cursor_x, text_y))

    else:  # PHASE 3: VICTORY DISPLAY (after frame 180)
        victory_frame = frame - 180  # Reset frame counter for victory phase
        
        # 2.6. Enhanced Background Stars for Victory - Moderate amount for celebration
        if not hasattr(draw_cosmic_victory, 'victory_background_stars'):
            draw_cosmic_victory.victory_background_stars = []
            # Initialize moderate background stars for victory celebration (100 stars)
            random.seed(99)
            for _ in range(100):  # Reduced from 160 to 100
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(1, 3)  # Keep same sizes as phase 1&2
                speed = random.uniform(0.3, 1.8)  # Slightly faster for victory
                brightness = random.randint(120, 255)  # Bit brighter for victory
                draw_cosmic_victory.victory_background_stars.append([x, y, size, speed, brightness])
        
        # Update moving victory background stars like cosmic_selector
        for star in draw_cosmic_victory.victory_background_stars:
            star[0] -= star[3]  # Move left like cosmic_selector
            if star[0] < 0:
                star[0] = width + 10
                star[1] = random.randint(0, height)
        
        # Draw enhanced moving background stars for victory
        for star in draw_cosmic_victory.victory_background_stars:
            x, y, size, speed, brightness = star
            # Enhanced twinkling effect for victory
            twinkle = math.sin(victory_frame * 0.12 + x * 0.01) * 35  # Bit more twinkle
            actual_brightness = max(70, min(255, brightness + twinkle))
            
            # Victory star colors - mostly white with occasional golden
            if (int(x + y + victory_frame // 15)) % 6 == 0:  # Less golden stars (1/6 instead of 1/4)
                color = (actual_brightness, int(actual_brightness * 0.95), int(actual_brightness * 0.8))
            else:  # White stars
                color = (actual_brightness, actual_brightness, actual_brightness)
            
            if size == 1:
                if 0 <= int(x) < width and 0 <= int(y) < height:
                    screen.set_at((int(x), int(y)), color)
            else:
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
                # Cross for victory stars like cosmic_selector
                if size >= 2:
                    pygame.draw.line(screen, color, 
                                   (int(x-size-1), int(y)), 
                                   (int(x+size+1), int(y)), 1)
                    pygame.draw.line(screen, color, 
                                   (int(x), int(y-size-1)), 
                                   (int(x), int(y+size+1)), 1)
        
        # 2.7. Victory Shooting Stars - Enhanced cosmic_selector style for victory
        # Create victory shooting stars data if not exists
        if not hasattr(draw_cosmic_victory, 'victory_shooting_stars'):
            draw_cosmic_victory.victory_shooting_stars = []
            # Initialize more shooting stars for victory celebration
            for _ in range(6):
                x = width + random.randint(50, 200)
                y = random.randint(30, height - 30)
                speed = random.uniform(4, 8)  # Faster for victory
                length = random.randint(40, 80)  # Longer trails for victory
                brightness = random.randint(200, 255)  # Brighter for victory
                draw_cosmic_victory.victory_shooting_stars.append([x, y, speed, length, brightness])
        
        # Update and draw victory shooting stars
        for shooting_star in draw_cosmic_victory.victory_shooting_stars[:]:
            shooting_star[0] -= shooting_star[2]  # Move left
            shooting_star[1] += shooting_star[2] * 0.4  # Slightly more downward for variety
            
            # Remove and recreate shooting star if off screen
            if shooting_star[0] < -shooting_star[3]:
                draw_cosmic_victory.victory_shooting_stars.remove(shooting_star)
                # Add new victory shooting star
                x = width + random.randint(50, 200)
                y = random.randint(30, height - 30)
                speed = random.uniform(4, 8)
                length = random.randint(40, 80)
                brightness = random.randint(200, 255)
                draw_cosmic_victory.victory_shooting_stars.append([x, y, speed, length, brightness])
        
        # Draw victory shooting stars with enhanced trail
        for shooting_star in draw_cosmic_victory.victory_shooting_stars:
            x, y, speed, length, brightness = shooting_star
            # Draw trail with victory colors
            for i in range(length):
                trail_x = x + i * 2.2  # Slightly wider spacing for victory
                trail_y = y - i * 0.7
                trail_brightness = max(0, brightness - i * 3)  # Slower fade for victory
                if 0 <= trail_x <= width and 0 <= trail_y <= height and trail_brightness > 0:
                    if i < 8:  # Bigger bright head for victory
                        # Victory colors - golden/white
                        head_color = (255, 255, 200) if i < 3 else (255, 255, 255)
                        pygame.draw.circle(screen, head_color, 
                                         (int(trail_x), int(trail_y)), 2)
                    else:  # Enhanced fading trail with golden tint
                        golden_factor = min(1.0, trail_brightness / 200.0)
                        trail_color = (
                            trail_brightness, 
                            int(trail_brightness * 0.8 * golden_factor), 
                            int(trail_brightness * 0.4)
                        )
                        if int(trail_x) >= 0 and int(trail_x) < width and int(trail_y) >= 0 and int(trail_y) < height:
                            screen.set_at((int(trail_x), int(trail_y)), trail_color)
        
        # 3. Background cosmic effects (lighter than before)
        # Black hole in background
        black_hole_radius = 30 + 8 * math.sin(victory_frame * 0.05)
        pygame.draw.circle(screen, (0, 0, 0), center, int(black_hole_radius))
        
        for i in range(3):
            glow_radius = black_hole_radius + i * 10
            glow_alpha = max(15, 40 - i * 10)
            glow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (30, 20, 80, glow_alpha), center, int(glow_radius), 2)
            screen.blit(glow_surf, (0, 0))

        # Subtle energy rings
        for ring in range(2):
            ring_radius = 160 + ring * 60 + 10 * math.sin(victory_frame * 0.08 + ring)
            ring_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            alpha = max(8, 25 - ring * 8)
            color = (80 + ring * 20, 80 + ring * 20, 150, alpha)
            pygame.draw.circle(ring_surf, color, center, int(ring_radius), 1)
            screen.blit(ring_surf, (0, 0))

        # Few quantum particles
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            base_dist = random.uniform(200, 300)
            quantum_wave = 20 * math.sin(victory_frame * 0.1 + angle * 2)
            dist = base_dist + quantum_wave
            
            x = int(center[0] + math.cos(angle) * dist)
            y = int(center[1] + math.sin(angle) * dist)
            
            if 0 <= x < width and 0 <= y < height:
                quantum_alpha = int(40 * abs(math.sin(victory_frame * 0.2 + angle)))
                colors = [(120,180,255), (180,120,255), (120,255,180)]
                color = random.choice(colors)
                pygame.draw.circle(screen, (*color, quantum_alpha), (x, y), 1)

        # 4. Final spaceship position (smaller, at center top - moved higher)
        final_ship_y = center[1] - 120  # Moved up from -80 to -120
        try:
            from .spaceship import load_spaceship_image, spaceship_rotated_images as ship_imgs
            load_spaceship_image()
            
            # Victory celebration flight pattern - fly back and forth initially
            if victory_frame < 120:  # First 2 seconds - celebration flight
                # Side-to-side flight pattern
                flight_progress = victory_frame / 120.0
                side_amplitude = 80 * (1 - flight_progress)  # Decrease amplitude over time
                side_movement = side_amplitude * math.sin(victory_frame * 0.15)
                
                # Gentle up-down movement
                hover_offset = 8 * math.sin(victory_frame * 0.12)
                
                ship_x = center[0] + side_movement
                ship_y = final_ship_y + hover_offset
                
                # Direction based on movement
                if victory_frame < 100:  # Active celebration phase
                    if math.sin(victory_frame * 0.15) > 0:
                        direction = "right"
                    else:
                        direction = "left"
                else:  # Settling down phase
                    direction = "up"
            else:  # After celebration - gentle hovering
                # Gentle hovering motion only
                hover_offset = 3 * math.sin(victory_frame * 0.1)  # Slower and smaller
                ship_x = center[0]
                ship_y = final_ship_y + hover_offset
                direction = "up"
            
            ship_img = ship_imgs.get(direction)
            if ship_img is None:
                ship_img = ship_imgs.get(None)
                
            if ship_img is not None:
                # Normal size for victory display
                ship_img = pygame.transform.scale(ship_img, (40, 40))  # Fixed size
                ship_rect = ship_img.get_rect(center=(int(ship_x), int(ship_y)))
                
                # Ship glow
                glow_surf = pygame.Surface((ship_rect.width + 20, ship_rect.height + 20), pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, (150, 200, 255, 60), glow_surf.get_rect())
                screen.blit(glow_surf, (ship_rect.x - 10, ship_rect.y - 10))
                
                screen.blit(ship_img, ship_rect)
            else:
                raise Exception("No spaceship image")
        except:
            # Fallback
            ship_x = center[0]
            if victory_frame < 120:
                side_movement = 80 * (1 - victory_frame/120.0) * math.sin(victory_frame * 0.15)
                ship_x += side_movement
            hover_offset = 5 * math.sin(victory_frame * 0.1)
            pygame.draw.circle(screen, (100, 200, 255), (int(ship_x), int(final_ship_y + hover_offset)), 12)

        # 5. VICTORY TEXT - appearing after spaceship settles
        if victory_frame > 30:  # Small delay after spaceship stops
            font_large = pygame.font.SysFont("Arial", 88, bold=True)
            
            # Text animation - fade in and scale up
            text_progress = min((victory_frame - 30) / 60.0, 1.0)  # 1 second fade in
            
            # Reduced scale pulsing - much gentler
            base_scale = 0.5 + text_progress * 0.5
            pulse_scale = 0.03 * math.sin(victory_frame * 0.08)  # Reduced from 0.1 to 0.03, slower frequency
            scale_pulse = base_scale + pulse_scale
            
            victory_text = font_large.render("YOU WIN!", True, (255, 255, 200))
            cosmic_text = pygame.transform.rotozoom(victory_text, 0, scale_pulse)
            text_rect = cosmic_text.get_rect(center=(center[0], center[1] + 20))
            
            text_alpha = int(255 * text_progress)
            
            # Shadow background
            shadow_surf = pygame.Surface((text_rect.width + 80, text_rect.height + 80), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, int(120 * text_progress)), shadow_surf.get_rect())
            screen.blit(shadow_surf, (text_rect.x - 40, text_rect.y - 40))
            
            # Glow layers
            for i, (size_offset, color, alpha_mult) in enumerate([
                (60, (100, 200, 255), 0.4),
                (40, (200, 150, 255), 0.6), 
                (20, (255, 255, 255), 0.3)
            ]):
                glow = pygame.Surface((text_rect.width + size_offset, text_rect.height + size_offset), pygame.SRCALPHA)
                glow_alpha = int(255 * alpha_mult * text_progress)
                pygame.draw.ellipse(glow, (*color, glow_alpha), glow.get_rect())
                offset = size_offset // 2
                screen.blit(glow, (text_rect.x - offset, text_rect.y - offset))
            
            # Final text
            cosmic_text.set_alpha(text_alpha)
            screen.blit(cosmic_text, text_rect)

            # 6. Instruction text - appears after victory text is fully visible
            if text_progress >= 1.0:
                small_font = pygame.font.SysFont("Arial", 28, bold=False)
                restart_text = "Click anywhere to play again"
                
                instruction_alpha = int(200 + 55 * math.sin(victory_frame * 0.12))
                
                # Text background
                text_bg = pygame.Surface((width, 40), pygame.SRCALPHA)
                text_bg.fill((0, 0, 0, 80))
                screen.blit(text_bg, (0, center[1] + 120))
                
                # Instruction text
                instruction_text = small_font.render(restart_text, True, (220, 220, 255))
                instruction_text.set_alpha(instruction_alpha)
                instruction_rect = instruction_text.get_rect(center=(center[0], center[1] + 140))
                screen.blit(instruction_text, instruction_rect)