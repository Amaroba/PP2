import os

# Window and grid settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
CELL_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Gameplay progression
BASE_MOVE_DELAY_MS = 180
FOOD_PER_LEVEL = 5
MAX_OBSTACLES_PER_LEVEL = 30

# Timings
NORMAL_FOOD_TTL_MS = 7000
POISON_RESPAWN_MS = 4000
POWER_UP_TTL_MS = 8000
POWER_UP_EFFECT_MS = 5000

# Colors
BACKGROUND_COLOR = (20, 20, 28)
TEXT_COLOR = (240, 240, 240)
BORDER_COLOR = (60, 60, 80)
FOOD_COLOR = (250, 200, 30)
POISON_COLOR = (120, 10, 10)
OBSTACLE_COLOR = (90, 90, 105)
GRID_COLOR = (45, 45, 58)

# DB connection settings (override with environment variables if needed)
DB_NAME = os.getenv("SNAKE_DB_NAME", "snake_db")
DB_USER = os.getenv("SNAKE_DB_USER", "postgres")
DB_PASSWORD = os.getenv("SNAKE_DB_PASSWORD", "postgres")
DB_HOST = os.getenv("SNAKE_DB_HOST", "localhost")
DB_PORT = int(os.getenv("SNAKE_DB_PORT", "5432"))
