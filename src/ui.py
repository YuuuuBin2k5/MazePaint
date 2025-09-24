# ui.py
import pygame
from config import *

def draw_move_count(screen, x, y, font, count):
    text_surf = render_text_with_outline(f"Moves: {count}", font, WHITE, BLACK, 1)
    screen.blit(text_surf, (x, y))

def render_text_with_outline(text, font, text_color, outline_color, outline_width=1):
    base = font.render(text, True, text_color)
    size = base.get_size()
    surf = pygame.Surface((size[0] + 2 * outline_width, size[1] + 2 * outline_width), pygame.SRCALPHA)
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                surf.blit(outline_surf, (dx + outline_width, dy + outline_width))
    surf.blit(base, (outline_width, outline_width))
    return surf

def draw_button(screen, font, rect, color, text=None):
    shadow_rect = rect.move(3, 3)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=8)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    if text:
        text_surf = render_text_with_outline(text, font, WHITE, BLACK, 1)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

def draw_board(screen, maze, painted_tiles, player_pos, board_x, board_y):
    rows = len(maze)
    cols = len(maze[0])
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(board_x + c * TILE_SIZE, board_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if painted_tiles[r][c]:
                pygame.draw.rect(screen, DARK_BLUE, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            if maze[r][c] == 1:
                pygame.draw.rect(screen, COLOR_WALL, rect)
    center_x = board_x + player_pos[1] * TILE_SIZE + TILE_SIZE // 2
    center_y = board_y + player_pos[0] * TILE_SIZE + TILE_SIZE // 2
    pygame.draw.circle(screen, COLOR_PLAYER, (center_x, center_y), PLAYER_RADIUS)

def draw_history_box(screen, font, history_list):
    box_rect = pygame.Rect(840, 100, 240, 200)
    pygame.draw.rect(screen, DARK_BLUE, box_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=8)
    
    title_surf = font.render("Last Solve Stats", True, WHITE)
    screen.blit(title_surf, (box_rect.x + 10, box_rect.y + 10))

    if not history_list:
        no_history_surf = font.render("No history yet.", True, WHITE)
        screen.blit(no_history_surf, (box_rect.x + 10, box_rect.y + 40))
    else:
        map_name, algo, result = history_list[-1]
        y_offset = box_rect.y + 40
        if result:
            lines = [f"Map: {map_name}", f"Algo: {algo}", f"Steps: {result['steps']}", f"Visited: {result['visited']}", f"Time: {round(result['time'], 4)}s"]
        else:
            lines = [f"Map: {map_name}", f"Algo: {algo}", "No solution found."]
        for line in lines:
            info_surf = font.render(line, True, WHITE)
            screen.blit(info_surf, (box_rect.x + 10, y_offset))
            y_offset += 25

def draw_win_message(screen, font):
    window_rect = screen.get_rect()
    text = font.render("YOU WIN!", True, COLOR_FONT)
    text_rect = text.get_rect(center=window_rect.center)
    bg_rect = text_rect.inflate(40, 40)
    bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 150))
    screen.blit(bg_surface, bg_rect)
    screen.blit(text, text_rect)