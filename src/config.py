# -*- coding: utf-8 -*-
"""
Game Configuration
Tất cả constants và settings của game
"""

import pygame

# ============================================================================
# WINDOW SETTINGS
# ============================================================================
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 680
WINDOW_TITLE = "MAZE PAINT - | Created by: Đào Nguyễn Nhật Anh [23110073] & Nguyễn Đoàn Trường Vĩ [23110173]"
ICON_PATH = "./asset/image/icon.png"
FPS = 60

# ============================================================================
# LAYOUT SETTINGS - HEADER SYSTEM
# ============================================================================
# Header bar height (increased for better title display)
HEADER_HEIGHT = 45

# ============================================================================
# MAZE & BOARD SETTINGS
# ============================================================================
TILE_SIZE = 40
MAZE_ROWS = 15
MAZE_COLS = 20
BOARD_WIDTH = MAZE_COLS * TILE_SIZE   # 800
BOARD_HEIGHT = MAZE_ROWS * TILE_SIZE  # 600

# Board position (top-left corner) - adjusted for header
BOARD_X = 20
BOARD_Y = 65  # 20 + HEADER_HEIGHT - moved down to make space for header

# Maze values
PATH = 0  # Walkable path
WALL = 1  # Wall

# ============================================================================
# UI LAYOUT SETTINGS - ALL ADJUSTED FOR HEADER
# ============================================================================
# Main buttons
BUTTON_WIDTH = 240
BUTTON_HEIGHT = 60
BUTTON_X = 840
MAP_BUTTON_Y = 145        # 100 + HEADER_HEIGHT
PLAYER_BUTTON_Y = 365     # 320 + HEADER_HEIGHT
SOLVER_BUTTON_Y = 445     # 400 + HEADER_HEIGHT
RESTART_BUTTON_Y = 525    # 480 + HEADER_HEIGHT
HISTORY_BUTTON_Y = 605    # 560 + HEADER_HEIGHT

# Speed control buttons
SPEED_BUTTON_WIDTH = 50
SPEED_BUTTON_HEIGHT = 40
SPEED_DECREASE_X = 840
SPEED_INCREASE_X = 1030
SPEED_DISPLAY_X = 900
SPEED_DISPLAY_WIDTH = 120
SPEED_BUTTONS_Y = 225      # 180 + HEADER_HEIGHT

# Move count display
MOVE_COUNT_X = 840
MOVE_COUNT_Y = 65          # 20 + HEADER_HEIGHT

# ============================================================================
# COLOR SETTINGS
# ============================================================================
# Basic colors
COLOR_BACKGROUND = (10, 25, 47)
COLOR_WALL = (20, 40, 65)
COLOR_PATH_PAINTED = (119, 176, 170)
COLOR_PLAYER = (255, 140, 60)
COLOR_FONT = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Accent colors
SHADOW_COLOR = (21, 21, 21)
YELLOW = (246, 255, 0)
BLUE = (148, 224, 255)
DARK_BLUE = (11, 64, 150)
RED = (255, 0, 0)

# Tile colors
TILE_TEXT = (255, 255, 255)
EMPTY_COLOR = (13, 27, 71)

# Space theme colors
SPACE_WALL = (10, 15, 30)
PATH_GLOW = (100, 200, 255)
PATH_OVERLAY = (30, 100, 200, 180)
UNVISITED_OVERLAY = (0, 0, 0, 100)
PLAYER_GLOW = (255, 150, 0, 60)

# Algorithm visualization colors
VISITED_TILE_COLOR = (100, 100, 255, 100)
ALGORITHM_PATH_COLOR = (255, 200, 0)

# ============================================================================
# SOUND SETTINGS
# ============================================================================
SOUND_ENABLED = True
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.5
MUSIC_VOLUME = 0.3

# Sound paths
SOUND_PATH = "./asset/sound/"
SOUND_MOVE = SOUND_PATH + "move.mp3"
SOUND_WIN = SOUND_PATH + "victory.mp3"
SOUND_BUTTON = SOUND_PATH + "button.mp3"
SOUND_ALGORITHM_START = SOUND_PATH + "algorithm_start.mp3"
SOUND_ALGORITHM_STEP = SOUND_PATH + "step.mp3"
BACKGROUND_MUSIC = SOUND_PATH + "background.mp3"
VICTORY_MUSIC = SOUND_PATH + "victory.mp3"
VICTORY_PHASE3_SOUND = SOUND_PATH + "victory2.mp3"

# ============================================================================
# ASSET PATHS
# ============================================================================
ASSET_FOLDER = "./asset/"
IMAGE_FOLDER = ASSET_FOLDER + "image/"
SPACESHIP_FOLDER = IMAGE_FOLDER + "spaceship/"
PLANET_FOLDER = IMAGE_FOLDER + "planet/"
FONT_FOLDER = ASSET_FOLDER + "fonts/"

IMAGE_FORMAT = ".png"

# Asset cache settings
ASSET_MAX_CACHE_SIZE = 100
ASSET_PRELOAD_ALL = True
ASSET_PRELOAD_TIMEOUT = 5.0  # seconds

# ============================================================================
# PLAYER SETTINGS
# ============================================================================
PLAYER_RADIUS = TILE_SIZE // 3

# Spaceship
SPACESHIP_SIZE = 40
SPACESHIP_SCALE = 1.5
SPACESHIP_ROTATION_SMOOTH = 0.15

# Spaceship particles
SPACESHIP_STAR_PARTICLE_COUNT = 8
SPACESHIP_STAR_PARTICLE_SPEED = 2
SPACESHIP_STAR_PARTICLE_LIFETIME = 20

# ============================================================================
# ANIMATION & MOVEMENT SETTINGS
# ============================================================================
# Smooth movement
SMOOTH_MOVE_SPEED = 0.9
PLAYER_MOVE_INTERVAL = 180  # ms cooldown

# Solver speed
SOLVER_MOVE_INTERVAL = 800  # 1x speed
BASE_SOLVER_INTERVAL = 800

# Movement queue
MAX_QUEUE_SIZE = 2
INPUT_BUFFER_TIME = 50  # ms

# ============================================================================
# UI BUTTON SETTINGS (UPDATED POSITIONS)
# ============================================================================
# Speed control buttons
SPEED_BUTTON_WIDTH = 50
SPEED_BUTTON_HEIGHT = 40
SPEED_DECREASE_X = 840
SPEED_INCREASE_X = 1030
SPEED_DISPLAY_X = 900
SPEED_DISPLAY_WIDTH = 120
SPEED_BUTTONS_Y = 225      # 180 + 45 (header)

# Move count display
MOVE_COUNT_X = 840
MOVE_COUNT_Y = 65          # 20 + 45 (header)

# UI rendering
TEXT_OUTLINE_WIDTH = 1
BUTTON_SHADOW_ALPHA = 80
BUTTON_BORDER_RADIUS = 10
HISTORY_Y_OFFSET = 25

# ============================================================================
# VISUAL EFFECTS SETTINGS
# ============================================================================
# Stars
STARS_FAR_COUNT = 50
STARS_MID_COUNT = 40
STARS_NEAR_COUNT = 30
STAR_FAR_SPEED = 0.1
STAR_MID_SPEED = 0.2
STAR_NEAR_SPEED = 0.3

# Planets
PLANET_SPAWN_DELAY = 60  # frames
PLANET_WAVE_COOLDOWN = 300
PLANET_WAVE_COUNT = 3
PLANET_SPEED_MIN = 0.5
PLANET_SPEED_MAX = 2.0
PLANET_SIZE_MIN = 30
PLANET_SIZE_MAX = 80

# Player trail
MAX_TRAIL_LENGTH = 5
TRAIL_ALPHA_START = 200
TRAIL_ALPHA_DECAY = 40
TRAIL_WIDTH = 3

# Tile completion effect
COMPLETION_GLOW_RADIUS = 5
COMPLETION_PARTICLE_COUNT = 3
COMPLETION_ANIMATION_DURATION = 30

# ============================================================================
# WALL RENDERING SETTINGS
# ============================================================================
ASTEROID_TYPES = ["crystalline", "metallic", "volcanic", "normal"]
ASTEROID_TEXTURE_DENSITY = 20
ASTEROID_HIGHLIGHT_OFFSET = 40

# ============================================================================
# WIDGET SETTINGS
# ============================================================================
# Algorithm selector
SELECTOR_CARD_WIDTH = 180
SELECTOR_CARD_HEIGHT = 120
SELECTOR_CARD_SPACING = 20
SELECTOR_ANIMATION_SPEED = 0.3
SELECTOR_GLOW_INTENSITY = 150

# Dialog
DIALOG_PADX = 20
DIALOG_PADY = 20

# ============================================================================
# MENU SETTINGS
# ============================================================================
SELECTED_SPACESHIP = 0  # Default selected spaceship (0-8)

# Menu animations
MENU_TITLE_GLOW_SPEED = 0.05
MENU_TITLE_GLOW_MAX = 50
MENU_BUTTON_HOVER_SCALE = 1.1
MENU_STAR_COUNT = 100
MENU_PARTICLE_COUNT = 50

# ============================================================================
# INTRO ANIMATION SETTINGS
# ============================================================================
INTRO_FADE_IN_DURATION = 60
INTRO_ZOOM_DURATION = 120
INTRO_TITLE_DURATION = 90
INTRO_MENU_FADE_DURATION = 60

# Loading bar
LOADING_BAR_WIDTH = 400
LOADING_BAR_HEIGHT = 30

# ============================================================================
# ALGORITHM SETTINGS
# ============================================================================
ALGORITHM_STEP_DELAY = 100  # ms
SHOW_VISITED_TILES = True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def set_selected_spaceship(ship_id):
    """Set selected spaceship ID"""
    global SELECTED_SPACESHIP
    SELECTED_SPACESHIP = ship_id

def get_selected_spaceship():
    """Get selected spaceship ID"""
    return SELECTED_SPACESHIP

