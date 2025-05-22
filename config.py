import json
import os

# --- Configuración Básica ---
WIDTH, HEIGHT = 1000, 600
LANES = 6
LANE_WIDTH = WIDTH // LANES
FPS = 60
LIVES = 3
SCORES_FILE = 'highscores.json'
TOP_SCORES = 5  # Cambiado de 3 a 5 para mantener las 5 mejores puntuaciones

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
            try:
                scores = json.load(f)
                print(f"Puntuaciones cargadas desde el archivo: {scores}")
                # Manejar el formato antiguo (solo números) y el nuevo formato (iniciales y puntuación)
                if scores and isinstance(scores[0], (int, float)):  # Formato antiguo: [10, 20, 30]
                    converted_scores = [('---', score) for score in scores]
                    print(f"Convertido formato antiguo a: {converted_scores}")
                    return converted_scores
                else:  # Formato nuevo: [{"initials": "ALE", "score": 500}, ...]
                    converted_scores = [(entry['initials'], entry['score']) for entry in scores]
                    print(f"Formato nuevo cargado: {converted_scores}")
                    return converted_scores
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error al cargar highscores.json: {e}. Inicializando como lista vacía.")
                return []
    print("No se encontró highscores.json, inicializando como lista vacía.")
    return []

def save_scores(scores):
    try:
        formatted_scores = [{'initials': initials, 'score': score} for initials, score in scores]
        with open(SCORES_FILE, 'w') as f:
            json.dump(formatted_scores, f)
        print(f"Puntuaciones guardadas en el archivo: {formatted_scores}")
    except Exception as e:
        print(f"Error al guardar las puntuaciones en highscores.json: {e}")

def add_score(initials, score):
    try:
        scores = load_scores()
        scores.append((initials.upper(), score))
        scores.sort(key=lambda x: x[1], reverse=True)
        scores = scores[:TOP_SCORES]
        save_scores(scores)
        print(f"Nueva puntuación añadida: {initials}, {score}. Lista actual: {scores}")
    except Exception as e:
        print(f"Error al añadir la puntuación: {e}")