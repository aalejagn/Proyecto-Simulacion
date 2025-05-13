import pygame
import pygame_menu
import random
import json
import os
import sys
import math
import pygame_menu.events
import pygame_menu.widgets

# --- Configuración Básica ---
WIDTH, HEIGHT = 1000, 600
LANES = 6
LANE_WIDTH = WIDTH // LANES
FPS = 60
LIVES = 3
SCORES_FILE = 'highscores.json'
TOP_SCORES = 3

# --- Configuración de Niveles ---
# Curva de velocidad: progresión geométrica (20% más rápido por nivel)
BASE_SPEED = 3
SPEED_GROWTH_RATE = 1.2  # 20% más rápido cada nivel
MAX_SPEED = 10  # Velocidad máxima para no hacer el juego imposible

# Puntos por rebasar: lineal + bonus por nivel
BASE_POINTS = 10
POINTS_GROWTH = 5  # Puntos adicionales por nivel

# Umbral para subir de nivel: crecimiento exponencial suave
BASE_LEVEL_UP = 100
LEVEL_UP_GROWTH_RATE = 1.3  # 30% más puntos requeridos cada nivel

# Configuración de densidad de objetos
BASE_ENEMIES = 2
BASE_OBSTACLES = 2
MAX_ENEMIES = 5
MAX_OBSTACLES = 4

# --- Funciones de Configuración Dinámica ---
def get_level_speed(level):
    """Calcula la velocidad para un nivel dado usando crecimiento geométrico con límite"""
    speed = BASE_SPEED * (SPEED_GROWTH_RATE ** (level - 1))
    return min(speed, MAX_SPEED)

def get_level_points(level):
    """Calcula los puntos por rebasar un vehículo en un nivel"""
    return BASE_POINTS + (level - 1) * POINTS_GROWTH

def get_level_up_threshold(level):
    """Calcula los puntos necesarios para alcanzar el siguiente nivel"""
    return int(BASE_LEVEL_UP * (LEVEL_UP_GROWTH_RATE ** (level - 1)))

def get_enemy_count(level):
    """Calcula el número de enemigos para un nivel"""
    return min(BASE_ENEMIES + (level // 2), MAX_ENEMIES)

def get_obstacle_count(level):
    """Calcula el número de obstáculos para un nivel"""
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

# --- Clases de Sprites ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = PLAYER_IMG
        self.image = pygame.transform.scale(self.original_image, (LANE_WIDTH-20, 60))
        self.lane = LANES // 2
        self.rect = self.image.get_rect()
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.invincible = False
        self.invincible_timer = 0

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2

    def move_right(self):
        if self.lane < LANES - 1:
            self.lane += 1
            self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
            
    def update(self):
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.image = pygame.transform.scale(self.original_image, (LANE_WIDTH-20, 60))
            elif self.invincible_timer % 10 < 5:
                self.image = pygame.transform.scale(self.original_image, (LANE_WIDTH-20, 60))
            else:
                self.image = pygame.Surface((LANE_WIDTH-20, 60), pygame.SRCALPHA)
                
    def set_invincible(self, duration):
        self.invincible = True
        self.invincible_timer = duration

class LaneManager:
    """Gestión inteligente de carriles para garantizar al menos uno libre"""
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.occupied = {lane: None for lane in range(LANES)}
        
    def get_available_lane(self, obj_type, player_lane):
        """Obtiene un carril disponible para un tipo de objeto"""
        # Prioridad 1: Carriles completamente libres
        free_lanes = [lane for lane, obj in self.occupied.items() if obj is None]
        
        # Prioridad 2: Carriles compatibles (enemigos evitan obstáculos y viceversa)
        if obj_type == 'enemy':
            available_lanes = [lane for lane, obj in self.occupied.items() if obj != 'obstacle']
        else:  # obstacle
            available_lanes = [lane for lane, obj in self.occupied.items() if obj != 'enemy']
        
        # Asegurar que el jugador tenga al menos un carril adyacente libre
        adjacent_lanes = [player_lane - 1, player_lane + 1]
        adjacent_lanes = [l for l in adjacent_lanes if 0 <= l < LANES]
        
        # Si estamos bloqueando al jugador, liberar un carril adyacente
        if all(self.occupied[l] is not None for l in adjacent_lanes):
            lane_to_free = random.choice(adjacent_lanes)
            self.occupied[lane_to_free] = None
            free_lanes.append(lane_to_free)
        
        # Seleccionar el mejor carril disponible
        if free_lanes:
            return random.choice(free_lanes)
        elif available_lanes:
            return random.choice(available_lanes)
        else:
            return random.randint(0, LANES-1)
    
    def occupy_lane(self, lane, obj_type):
        if 0 <= lane < LANES:
            self.occupied[lane] = obj_type
    
    def free_lane(self, lane):
        if 0 <= lane < LANES:
            self.occupied[lane] = None

class Rival(pygame.sprite.Sprite):
    def __init__(self, speed, lane_manager):
        super().__init__()
        self.speed = speed
        self.lane_manager = lane_manager
        self.lane = -1
        self.image = pygame.transform.scale(ENEMY_IMG, (LANE_WIDTH-20, 60))
        self.rect = self.image.get_rect()
        self.reset()
        
    def reset(self, player_lane=None):
        if player_lane is None:
            player_lane = LANES // 2  # Default si no se especifica
            
        self.lane = self.lane_manager.get_available_lane('enemy', player_lane)
        self.lane_manager.occupy_lane(self.lane, 'enemy')
        
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.y = -self.rect.height - random.randint(0, 100)  # Espaciado aleatorio

    def update(self, player_lane=None):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.lane_manager.free_lane(self.lane)
            self.reset(player_lane)
            return True
        return False

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed, lane_manager):
        super().__init__()
        self.speed = speed
        self.lane_manager = lane_manager
        self.lane = -1
        self.image = pygame.transform.scale(OBSTACLE_IMG, (LANE_WIDTH-20, 60))
        self.rect = self.image.get_rect()
        self.reset()
        
    def reset(self, player_lane=None):
        if player_lane is None:
            player_lane = LANES // 2
            
        self.lane = self.lane_manager.get_available_lane('obstacle', player_lane)
        self.lane_manager.occupy_lane(self.lane, 'obstacle')
        
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.y = -self.rect.height - random.randint(0, 100)

    def update(self, player_lane=None):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.lane_manager.free_lane(self.lane)
            self.reset(player_lane)
            return True
        return False

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.images = []
        for i in range(1, 6):
            img = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(img, (255, 255, 0, 200), (40, 40), 40 - (i*5))
            pygame.draw.circle(img, (255, 0, 0, 200), (40, 40), 20 - (i*3))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=pos)
        self.counter = 0

    def update(self):
        explosion_speed = 4
        self.counter += 1
        
        if self.counter >= explosion_speed:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]

class ScoreDisplay:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.lives = LIVES
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.high_scores = load_scores()
        
    def update(self, score, level, lives):
        self.score = score
        self.level = level
        self.lives = lives
        
    def draw(self, surface):
        # Fondo semitransparente
        hud = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 150))
        surface.blit(hud, (0, 0))
        
        # Puntuación
        score_text = self.big_font.render(f"{self.score}", True, (255, 255, 255))
        surface.blit(score_text, (20, 20))
        
        # Nivel
        level_text = self.font.render(f"Nivel: {self.level}", True, (200, 200, 200))
        surface.blit(level_text, (WIDTH - 120, 20))
        
        # Vidas
        life_icon = pygame.transform.scale(PLAYER_IMG, (30, 30))
        for i in range(self.lives):
            surface.blit(life_icon, (20 + i * 40, 60))
            
        # Barra de progreso al siguiente nivel
        threshold = get_level_up_threshold(self.level)
        progress = (self.score % threshold) / threshold
        pygame.draw.rect(surface, (100, 100, 100), (WIDTH - 120, 60, 100, 10))
        pygame.draw.rect(surface, (0, 255, 0), (WIDTH - 120, 60, int(100 * progress), 10))

def game_loop(surface):
    clock = pygame.time.Clock()
    
    # Inicializar sistemas
    lane_manager = LaneManager()
    player = Player()
    score_display = ScoreDisplay()
    
    # Configuración inicial de nivel
    current_level = 1
    current_speed = get_level_speed(current_level)
    points_per_car = get_level_points(current_level)
    enemy_count = get_enemy_count(current_level)
    obstacle_count = get_obstacle_count(current_level)
    
    # Grupos de sprites
    rivals = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    
    # Inicializar enemigos y obstáculos
    for _ in range(enemy_count):
        rivals.add(Rival(current_speed, lane_manager))
    
    for _ in range(obstacle_count):
        obstacles.add(Obstacle(current_speed, lane_manager))
    
    # Variables de juego
    score = 0
    lives = LIVES
    running = True
    paused = False
    
    # Fuente para menú de pausa
    font = pygame.font.SysFont(None, 48)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move_left()
                elif event.key == pygame.K_RIGHT:
                    player.move_right()
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    if paused:
                        return  # Volver al lobby
                    paused = True

        if paused:
            # Dibujar menú de pausa
            pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pause_surface.fill((0, 0, 0, 150))
            surface.blit(pause_surface, (0, 0))
            
            pause_text = font.render("PAUSA", True, (255, 255, 255))
            continue_text = font.render("P: Continuar", True, (200, 200, 200))
            restart_text = font.render("R: Reiniciar", True, (200, 200, 200))
            quit_text = font.render("ESC: Salir", True, (200, 200, 200))
            
            surface.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 100))
            surface.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2))
            surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
            surface.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 100))
            
            pygame.display.flip()
            
            # Manejar eventos durante la pausa
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                return game_loop(surface)  # Reiniciar
            
            clock.tick(FPS)
            continue

        # Actualizar sprites
        player.update()
        explosions.update()
        
        # Actualizar enemigos y obstáculos
        for r in rivals:
            if r.update(player.lane):
                score += points_per_car
                
                # Verificar si subimos de nivel
                new_level = math.floor(score / get_level_up_threshold(current_level)) + 1
                if new_level > current_level:
                    current_level = new_level
                    current_speed = get_level_speed(current_level)
                    points_per_car = get_level_points(current_level)
                    
                    # Actualizar velocidad de todos los objetos
                    for spr in rivals:
                        spr.speed = current_speed
                    for spr in obstacles:
                        spr.speed = current_speed
                    
                    # Ajustar cantidad de enemigos y obstáculos
                    new_enemy_count = get_enemy_count(current_level)
                    new_obstacle_count = get_obstacle_count(current_level)
                    
                    # Añadir enemigos si es necesario
                    while len(rivals) < new_enemy_count:
                        rivals.add(Rival(current_speed, lane_manager))
                    
                    # Añadir obstáculos si es necesario
                    while len(obstacles) < new_obstacle_count:
                        obstacles.add(Obstacle(current_speed, lane_manager))
        
        for o in obstacles:
            o.update(player.lane)

        # Detección de colisiones
        if not player.invincible:
            rival_hit = pygame.sprite.spritecollideany(player, rivals)
            obstacle_hit = pygame.sprite.spritecollideany(player, obstacles)
            
            if rival_hit or obstacle_hit:
                explosion = Explosion(player.rect.center)
                explosions.add(explosion)
                lives -= 1
                player.set_invincible(90)
                
                if rival_hit:
                    rival_hit.reset(player.lane)
                if obstacle_hit:
                    obstacle_hit.reset(player.lane)
                
                if lives == 0:
                    scores = load_scores()
                    scores.append(score)
                    save_scores(sorted(scores, reverse=True)[:TOP_SCORES])
                    break

        # Dibujar todo
        surface.fill((50, 50, 50))
        
        # Líneas de carril
        for i in range(1, LANES):
            pygame.draw.line(surface, (200, 200, 200), (i*LANE_WIDTH, 0), (i*LANE_WIDTH, HEIGHT), 2)
        
        # Dibujar sprites
        rivals.draw(surface)
        obstacles.draw(surface)
        surface.blit(player.image, player.rect)
        explosions.draw(surface)
        
        # Actualizar y dibujar HUD
        score_display.update(score, current_level, lives)
        score_display.draw(surface)

        pygame.display.flip()
        clock.tick(FPS)

    # Menú de fin de juego
    # Tema personalizado para menú de fin de juego
    menu_over_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_over_theme.background_color = (15, 10, 25)  # Fondo aún más oscuro
    menu_over_theme.title_font = pygame_menu.font.FONT_8BIT
    menu_over_theme.title_font_size = 48
    menu_over_theme.title_background_color = (120, 0, 20)  # Rojo oscuro
    menu_over_theme.title_font_color = (255, 255, 255)
    menu_over_theme.widget_font_size = 26
    menu_over_theme.widget_font_color = (255, 255, 255)
    menu_over_theme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection(arrow_size=(15, 20))
    menu_over_theme.widget_background_color = (40, 20, 40)
    menu_over_theme.widget_alignment = pygame_menu.locals.ALIGN_CENTER

    # Crear menú de fin de juego con el nuevo tema
    menu_over = pygame_menu.Menu('Fin del Juego', WIDTH, HEIGHT, theme=menu_over_theme)

    # Mostrar puntuación final
    menu_over.add.label(f"Puntuación Final: {score}", font_size=32)
    menu_over.add.vertical_margin(15)

    # Mostrar mejores puntuaciones si existen
    scores = load_scores()
    if scores:
        menu_over.add.label("🏆 Mejores Puntuaciones:", font_size=26)
        for i, s in enumerate(scores[:3]):
            menu_over.add.label(f"{i+1}. {s}", font_size=22)
        menu_over.add.vertical_margin(20)

    # Botones
    menu_over.add.button('🔁 Reiniciar', lambda: game_loop(surface))
    menu_over.add.button('🏠 Lobby', pygame_menu.events.EXIT)

    menu_over.mainloop(surface)


def main():
    pygame.init()
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Juego Retro de Carritos")

    # Cargar imágenes
    global PLAYER_IMG, ENEMY_IMG, OBSTACLE_IMG
    try:
        PLAYER_IMG = pygame.image.load(os.path.join("IMG_FOLDER", 'carro1.png')).convert_alpha()
        ENEMY_IMG = pygame.image.load(os.path.join("IMG_FOLDER", 'carro2.png')).convert_alpha()
        OBSTACLE_IMG = pygame.image.load(os.path.join("IMG_FOLDER", 'obstaculo.png')).convert_alpha()
    except:
        # Imágenes de respaldo
        PLAYER_IMG = pygame.Surface((50, 80), pygame.SRCALPHA)
        pygame.draw.rect(PLAYER_IMG, (0, 0, 255), (10, 0, 30, 80))
        ENEMY_IMG = pygame.Surface((50, 80), pygame.SRCALPHA)
        pygame.draw.rect(ENEMY_IMG, (255, 0, 0), (10, 0, 30, 80))
        OBSTACLE_IMG = pygame.Surface((50, 80), pygame.SRCALPHA)
        pygame.draw.rect(OBSTACLE_IMG, (100, 100, 100), (10, 0, 30, 80))

    # Configurar menú principal
    menu_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_theme.background_color = (10, 10, 30)  # Fondo más oscuro
    menu_theme.title_font = pygame_menu.font.FONT_8BIT  # Fuente estilo retro
    menu_theme.title_font_size = 50
    menu_theme.widget_font_size = 28
    menu_theme.title_background_color = (50, 20, 100)  # Fondo del título
    menu_theme.title_font_color = (255, 255, 0)  # Título amarillo
    menu_theme.widget_font_color = (255, 255, 255)  # Texto blanco
    menu_theme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection(arrow_size=(15, 20))  # Selector visual retro
    menu_theme.widget_background_color = (30, 30, 60)  # Fondo de widgets
    menu_theme.widget_alignment = pygame_menu.locals.ALIGN_CENTER  # Centrar todos los widgets por defecto

    # Crear menú principal
    menu = pygame_menu.Menu(
        title='Carreras Retro',
        width=WIDTH,
        height=HEIGHT,
        theme=menu_theme
    )

    # Mostrar mejores puntuaciones alineadas a la derecha
    scores = load_scores()
    if scores:
        menu.add.label("Récords:", font_size=20, align=pygame_menu.locals.ALIGN_LEFT)
        for i, s in enumerate(scores[:3]):
            menu.add.label(f"{i+1}. {s}", font_size=18, align=pygame_menu.locals.ALIGN_LEFT)
        menu.add.vertical_margin(20)

    # Función para crear botones centrados
    def crear_botones(texto, accion, color_fondo, color_texto):
        boton = menu.add.button(texto, accion, font_color=color_texto, align=pygame_menu.locals.ALIGN_CENTER)
        boton.set_padding((10, 20, 10, 20))
        boton.set_max_width(300)
        boton.set_background_color(color_fondo)

    # Añadir botones centrados
    crear_botones("🚗1 Jugador", lambda: game_loop(surface), (20, 40, 20), (255, 255, 0))
    # crear_botones("👾2 Jugadores", lambda: game_loop(surface), (30,60,20), 255,255,200)
    crear_botones("Salir", pygame_menu.events.EXIT, (80, 20, 20), (255, 255, 255))

    menu.mainloop(surface)
    pygame.quit()

if __name__ == '__main__':
    main()