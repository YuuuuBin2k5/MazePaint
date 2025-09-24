# -- CÀI ĐẶT CỬA SỔ --
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 640
WINDOW_TITLE = "Maze Paint"
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
# -- CÀI ĐẶT NGƯỜI CHƠI --
PLAYER_RADIUS = TILE_SIZE // 3

