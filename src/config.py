# -- CÀI ĐẶT CỬA SỔ --
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 640
WINDOW_TITLE = "Maze Paint"
ICON_PATH = "./asset/image/icon.png"
FPS = 60

# -- CÀI ĐẶT MÊ CUNG VÀ BOARD CỐ ĐỊNH --
TILE_SIZE = 40
MAZE_ROWS = 15
MAZE_COLS = 20
BOARD_WIDTH = MAZE_COLS * TILE_SIZE   # 800
BOARD_HEIGHT = MAZE_ROWS * TILE_SIZE  # 600

# Tọa độ góc trên bên trái của board để căn giữa màn hình
BOARD_X = 20
BOARD_Y = 20

# -- MAZE VALUES --
PATH = 0  # Ô đường đi
WALL = 1  # Ô tường

# -- MÀU SẮC --
COLOR_BACKGROUND = (10, 25, 47)
COLOR_WALL = (20, 40, 65)
COLOR_PATH_PAINTED = (119, 176, 170)
COLOR_PLAYER = (255, 140, 60)  # Màu cam sáng cho spaceship
COLOR_FONT = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
SHADOW_COLOR = (21, 21, 21)
YELLOW = (246, 255, 0)
BLUE = (148, 224, 255)
DARK_BLUE = (11, 64, 150)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TILE_TEXT = (255, 255, 255)
EMPTY_COLOR = (13, 27, 71)
SHADOW_COLOR = (180, 180, 180)
WHITE = (255, 255, 255)

# -- MÀU SẮC SPACE THEME --
SPACE_WALL = (10, 15, 30)          # Tường space tối
PATH_GLOW = (100, 200, 255)        # Viền xanh sáng cho đường đã đi
PATH_OVERLAY = (30, 100, 200, 180)  # Overlay xanh trong suốt
UNVISITED_OVERLAY = (0, 0, 0, 100)  # Overlay đen mờ cho ô chưa đi
PLAYER_GLOW = (255, 150, 0, 60)     # Hiệu ứng glow cam cho player

# -- CÀI ĐẶT ÂM THANH --
SOUND_ENABLED = True
MASTER_VOLUME = 0.7  # Âm lượng chính (0.0 - 1.0)
SFX_VOLUME = 0.5     # Âm lượng hiệu ứng âm thanh
MUSIC_VOLUME = 0.3   # Âm lượng nhạc nền

# Đường dẫn âm thanh
SOUND_PATH = "./asset/sound/"
SOUND_MOVE = SOUND_PATH + "move.mp3"          # Âm thanh di chuyển
SOUND_WIN = SOUND_PATH + "victory.mp3"        # Âm thanh chiến thắng
SOUND_BUTTON = SOUND_PATH + "button.mp3"      # Âm thanh nhấn nút
SOUND_ALGORITHM_START = SOUND_PATH + "algorithm_start.mp3"  # Âm thanh bắt đầu thuật toán
SOUND_ALGORITHM_STEP = SOUND_PATH + "step.mp3"              # Âm thanh mỗi bước thuật toán
BACKGROUND_MUSIC = SOUND_PATH + "background.mp3"            # Nhạc nền
VICTORY_MUSIC = SOUND_PATH + "victory.mp3"            # Nhạc chiến thắng (dài)
VICTORY_PHASE3_SOUND = SOUND_PATH + "victory2.mp3"  # Âm thanh đặc biệt phase 3

# -- CÀI ĐẶT NGƯỜI CHƠI --
PLAYER_RADIUS = TILE_SIZE // 3

# -- CÀI ĐẶT ANIMATION VÀ MOVEMENT --
SMOOTH_MOVE_SPEED = 0.9    # Tốc độ chuyển động mượt mà (tăng để nhanh hơn khi auto solve)
SOLVER_MOVE_INTERVAL = 800  # Tốc độ mặc định (1x) - giống như manual với đầy đủ animation
BASE_SOLVER_INTERVAL = 800  # Tốc độ cơ sở để tính toán multiple
PLAYER_MOVE_INTERVAL = 180  # Thời gian cooldown cho player movement

# -- CÀI ĐẶT UI BUTTONS --
BUTTON_WIDTH = 240
BUTTON_HEIGHT = 60
BUTTON_X = 840
MAP_BUTTON_Y = 100
PLAYER_BUTTON_Y = 320
SOLVER_BUTTON_Y = 400
RESTART_BUTTON_Y = 480
HISTORY_BUTTON_Y = 560

# Speed control buttons
SPEED_BUTTON_WIDTH = 50
SPEED_BUTTON_HEIGHT = 40
SPEED_DECREASE_X = 840
SPEED_INCREASE_X = 1030
SPEED_DISPLAY_X = 900
SPEED_DISPLAY_WIDTH = 120
SPEED_BUTTONS_Y = 180

# Move count display position
MOVE_COUNT_X = 840
MOVE_COUNT_Y = 20

# -- CÀI ĐẶT SPACE EFFECTS --
STARS_FAR_COUNT = 50
STARS_MID_COUNT = 40
STARS_NEAR_COUNT = 30
MAX_TRAIL_LENGTH = 5  # Số lượng vết player trail tối đa

# -- UI DIALOG SETTINGS --
DIALOG_PADX = 20  # Padding cho radio button trong dialog
DIALOG_PADY = 20  # Padding cho button trong dialog

# -- UI RENDERING SETTINGS --
TEXT_OUTLINE_WIDTH = 1  # Độ dày viền text
BUTTON_SHADOW_ALPHA = 80  # Độ mờ shadow button (0-255)
BUTTON_BORDER_RADIUS = 10  # Bo góc button
HISTORY_Y_OFFSET = 25  # Khoảng cách dòng trong history
PLANET_SPAWN_DELAY = 60  # Delay spawn hành tinh (frames)

# -- MENU SETTINGS --
SELECTED_SPACESHIP = 0  # Spaceship được chọn (0-8)

def set_selected_spaceship(ship_id):
    """Set spaceship đã chọn"""
    global SELECTED_SPACESHIP
    SELECTED_SPACESHIP = ship_id

def get_selected_spaceship():
    """Get spaceship đã chọn"""
    return SELECTED_SPACESHIP

