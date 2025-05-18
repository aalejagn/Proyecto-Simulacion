
import json
import os

# --- Configuración Básica ---
WIDTH, HEIGHT = 1000, 600
LANES = 6
LANE_WIDTH = WIDTH // LANES
FPS = 60
LIVES = 3
SCORES_FILE = 'highscores.json'
TOP_SCORES = 3

# --- Configuración de Niveles ---
BASE_SPEED = 3
SPEED_GROWTH_RATE = 1.2
MAX_SPEED = 10
BASE_POINTS = 10
POINTS_GROWTH = 5
BASE_LEVEL_UP = 100
LEVEL_UP_GROWTH_RATE = 1.3
BASE_ENEMIES = 2
BASE_OBSTACLES = 2
MAX_ENEMIES = 5
MAX_OBSTACLES = 4

# --- Funciones de Configuración Dinámica ---
def get_level_speed(level):
    speed = BASE_SPEED * (SPEED_GROWTH_RATE ** (level - 1))
    return min(speed, MAX_SPEED)

def get_level_points(level):
    return BASE_POINTS + (level - 1) * POINTS_GROWTH

def get_level_up_threshold(level):
    return int(BASE_LEVEL_UP * (LEVEL_UP_GROWTH_RATE ** (level - 1)))

def get_enemy_count(level):
    return min(BASE_ENEMIES + (level // 2), MAX_ENEMIES)

def get_obstacle_count(level):
    return min(BASE_OBSTACLES + (level // 3), MAX_OBSTACLES)

# --- Gestión de Puntuaciones ---
def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f)