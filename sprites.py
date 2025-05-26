import pygame
import random
from config import WIDTH, HEIGHT, LANES, LANE_WIDTH, LIVES, get_level_up_threshold, load_scores

# Clase Player maneja el sprite del jugador, su movimiento e invencibilidad
class Player(pygame.sprite.Sprite):
    def __init__(self, initial_lane, controls, skin):
        super().__init__()
        self.original_image = skin  # Almacena la imagen original del skin del jugador
        self.image = pygame.transform.scale(self.original_image, (LANE_WIDTH-20, 60))  # Escala la imagen para ajustarse al carril
        self.lane = initial_lane  # Establece el carril inicial
        self.rect = self.image.get_rect()  # Obtiene el rectángulo para detección de colisiones
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2  # Centra al jugador en el carril
        self.rect.bottom = HEIGHT - 10  # Posiciona al jugador cerca del fondo de la pantalla
        self.invincible = False  # Controla el estado de invencibilidad
        self.invincible_timer = 0  # Temporizador para la duración de la invencibilidad
        self.controls = controls  # Almacena las teclas de control del jugador
        self.active = True  # Indica si el jugador está activo (no muerto)

    # Mueve al jugador a la izquierda si no está en el carril más a la izquierda y está activo
    def move_left(self):
        if not self.active:
            return
        if self.lane > 0:
            self.lane -= 1
            self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2

    # Mueve al jugador a la derecha si no está en el carril más a la derecha y está activo
    def move_right(self):
        if not self.active:
            return
        if self.lane < LANES - 1:
            self.lane += 1
            self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2

    # Actualiza el estado del jugador, manejando efectos visuales de invencibilidad
    def update(self):
        if not self.active:
            return
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.image = pygame.transform.scale(self.original_image, (LANE_WIDTH-20, 60))  # Restaura la imagen original
            elif self.invincible_timer % 10 < 5:
                self.image = pygame.transform.scale(self.original_image, (LANE_WIDTH-20, 60))  # Fotograma visible
            else:
                self.image = pygame.Surface((LANE_WIDTH-20, 60), pygame.SRCALPHA)  # Fotograma transparente para parpadeo

    # Establece la invencibilidad por una duración específica
    def set_invincible(self, duration):
        self.invincible = True
        self.invincible_timer = duration

# Clase LaneManager gestiona la ocupación de carriles y la selección aleatoria
class LaneManager:
    def __init__(self):
        self.reset()  # Inicializa la ocupación de carriles

    # Reinicia todos los carriles a no ocupados
    def reset(self):
        self.occupied = {lane: None for lane in range(LANES)}  # Diccionario para rastrear ocupación de carriles

    # Obtiene un carril aleatorio
    def get_random_lane(self):
        return random.randint(0, LANES - 1)

    # Obtiene un carril aleatorio, evitando carriles adyacentes al jugador si es posible
    def get_random_lane_avoiding(self, player_lane):
        adjacent_lanes = [player_lane - 1, player_lane + 1]
        adjacent_lanes = [l for l in adjacent_lanes if 0 <= l < LANES]
        free_lanes = [lane for lane in range(LANES) if lane not in adjacent_lanes or self.occupied.get(lane) is None]
        if free_lanes:
            return random.choice(free_lanes)
        return random.randint(0, LANES - 1)

    # Marca un carril como ocupado por un objeto
    def occupy_lane(self, lane, obj_type):
        if 0 <= lane < LANES:
            self.occupied[lane] = obj_type

    # Libera un carril de la ocupación
    def free_lane(self, lane):
        if 0 <= lane < LANES:
            self.occupied[lane] = None

# Clase Rival representa los autos enemigos que se mueven hacia abajo
class Rival(pygame.sprite.Sprite):
    def __init__(self, speed, lane_manager, enemy_img):
        super().__init__()
        self.speed = speed  # Velocidad de movimiento del rival
        self.lane_manager = lane_manager  # Referencia al administrador de carriles
        self.lane = -1  # Carril inicial (se establece en reset)
        self.image = pygame.transform.scale(enemy_img, (LANE_WIDTH-20, 60))  # Escala la imagen del rival
        self.rect = self.image.get_rect()  # Obtiene el rectángulo para colisiones
        self.reset()  # Inicializa la posición

    # Reinicia el rival a un carril aleatorio y posición fuera de pantalla
    def reset(self, player_lane=None):
        if player_lane is None:
            player_lane = LANES // 2
        self.lane = self.lane_manager.get_random_lane_avoiding(player_lane)
        self.lane_manager.occupy_lane(self.lane, 'enemy')
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.y = -self.rect.height - random.randint(0, 100)

    # Actualiza la posición del rival, reinicia si sale de la pantalla
    def update(self, player_lane=None):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.lane_manager.free_lane(self.lane)
            self.reset(player_lane)
            return True  # Indica que el rival salió de la pantalla
        return False

# Clase Obstacle representa obstáculos estáticos en los carriles
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed, lane_manager, image, debug=False):
        super().__init__()
        self.image = pygame.transform.scale(image, (LANE_WIDTH-20, 60))  # Escala la imagen del obstáculo
        self.rect = self.image.get_rect()
        if debug:
            print(f"Obstáculo inicializado con tamaño de imagen: {self.image.get_size()}, rect: {self.rect}")
        self.lane_manager = lane_manager
        self.lane = self.lane_manager.get_random_lane()  # Asigna un carril aleatorio
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.bottom = 0
        self.speed = speed

    # Actualiza la posición del obstáculo, reinicia si sale de la pantalla
    def update(self, player_lane=None):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.lane_manager.free_lane(self.lane)
            self.reset(player_lane)
            return True
        return False

    # Reinicia el obstáculo a un nuevo carril aleatorio
    def reset(self, player_lane):
        self.lane = self.lane_manager.get_random_lane_avoiding(player_lane)
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.bottom = 0

# Clase Explosion maneja el efecto visual de las colisiones
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

    # Actualiza la animación de la explosión
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

# Clase Rain representa partículas de lluvia para el efecto climático
class Rain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((2, 10), pygame.SRCALPHA)
        pygame.draw.line(self.image, (150, 150, 255, 200), (1, 0), (1, 10), 2)  # Dibuja una gota de lluvia
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(10, 15)

    # Actualiza la posición de la gota, reinicia si sale de la pantalla
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = random.randint(-HEIGHT, 0)

# Clase Lightning maneja el efecto de relámpago
class Lightning:
    def __init__(self):
        self.timer = random.randint(120, 600)  # Frames entre relámpagos (2-10 segundos a 60 FPS)
        self.flash_duration = 10  # Duración del destello en frames
        self.flash_alpha = 100  # Alfa máximo para el destello (semi-transparente)
        self.flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.is_flashing = False
        self.flash_counter = 0

    # Actualiza el temporizador y el efecto de destello
    def update(self, music_manager):
        self.timer -= 1
        if self.timer <= 0:
            self.is_flashing = True
            self.flash_counter = self.flash_duration
            music_manager.play_sound('thunder_sound.mp3')  # Reproduce sonido de trueno
            self.timer = random.randint(120, 600)  # Reinicia temporizador
        if self.is_flashing:
            self.flash_counter -= 1
            if self.flash_counter <= 0:
                self.is_flashing = False
            # Calcula alfa para efecto de desvanecimiento
            alpha = int(self.flash_alpha * (self.flash_counter / self.flash_duration))
            self.flash_surface.fill((255, 255, 255, alpha))

    # Dibuja el destello de relámpago en pantalla
    def draw(self, surface):
        if self.is_flashing:
            surface.blit(self.flash_surface, (0, 0))

# Clase ScoreDisplay maneja la interfaz de usuario (HUD) para un jugador
class ScoreDisplay:
    def __init__(self, life_icon_img):
        self.score1 = 0
        self.score2 = 0
        self.level = 1
        self.lives = LIVES
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 36, bold=True)
        #TODO: Cargar puntuaciones altas para mostrar en el HUD
        self.high_scores = load_scores()
        self.life_icon_img = pygame.transform.scale(life_icon_img, (30, 30))  # Escala el ícono de vida

    # Actualiza puntuación, nivel y vidas
    def update(self, score1, score2, level, lives):
        self.score1 = score1
        self.score2 = score2
        self.level = level
        self.lives = lives

    # Dibuja elementos del HUD (puntuación, nivel, vidas, barra de progreso)
    def draw(self, surface):
        hud = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 150))  # Fondo semi-transparente para el HUD
        surface.blit(hud, (0, 0))
        score1_text = self.big_font.render(f"J1: {self.score1}", True, (255, 255, 255))
        surface.blit(score1_text, (20, 20))
        level_text = self.font.render(f"Nivel: {self.level}", True, (200, 200, 200))
        surface.blit(level_text, (WIDTH - 120, 20))
        for i in range(self.lives):
            surface.blit(self.life_icon_img, (20 + i * 40, 60))
        threshold = get_level_up_threshold(self.level)
        progress = (max(self.score1, self.score2) % threshold) / threshold
        pygame.draw.rect(surface, (100, 100, 100), (WIDTH - 120, 60, 100, 10))  # Fondo de barra de progreso
        pygame.draw.rect(surface, (0, 255, 0), (WIDTH - 120, 60, int(100 * progress), 10))  # Barra de progreso

# Clase ScoreDisplay2 maneja el HUD para el modo de dos jugadores
class ScoreDisplay2:
    def __init__(self, skin):
        self.score1 = 0
        self.score2 = 0
        self.level = 1
        self.lives1 = 0
        self.lives2 = 0
        self.font = pygame.font.SysFont(None, 36)

    # Actualiza puntuaciones, nivel y vidas de ambos jugadores
    def update(self, score1, score2, level, lives1, lives2):
        self.score1 = score1
        self.score2 = score2
        self.level = level
        self.lives1 = lives1
        self.lives2 = lives2

    # Dibuja elementos del HUD para ambos jugadores
    def draw(self, surface):
        text1 = self.font.render(f"J1: {self.score1}  Vidas: {self.lives1}", True, (255, 255, 255))
        text2 = self.font.render(f"J2: {self.score2}  Vidas: {self.lives2}", True, (255, 255, 255))
        level_text = self.font.render(f"Nivel: {self.level}", True, (255, 255, 0))
        surface.blit(text1, (20, 10))
        surface.blit(text2, (20, 50))
        surface.blit(level_text, (WIDTH - 150, 10))

    #TODO: Implementar barra de progreso o visualización de puntuaciones altas para modo de dos jugadores

# Clase Snow representa partículas de nieve para el efecto climático
class Snow(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255, 200), (2, 2), 2)  # Dibuja un copo de nieve
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(3, 7)  # Más lento que la lluvia para simular nieve

    # Actualiza la posición del copo, reinicia si sale de la pantalla
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = random.randint(-HEIGHT, 0)

# Clase Sunrise maneja el efecto climático de amanecer con estrellas fugaces
class Sunrise:
    def __init__(self):
        #TODO: Configurar gradiente y cantidad de estrellas según ajustes del juego
        self.gradient_surface = pygame.Surface((WIDTH, HEIGHT))
        self.gradient_surface.fill((10, 10, 10))  # Carretera negra, fondo de noche
        # Inicializa estrellas fugaces (x, y, velocidad, brillo)
        self.stars = []
        for _ in range(60):
            x = random.randint(0, WIDTH)
            y = random.randint(-HEIGHT, 0)
            speed = random.uniform(1, 3)
            brightness = random.randint(180, 255)
            self.stars.append([x, y, speed, brightness])

    # Actualiza posiciones de las estrellas
    def update(self, music_manager):
        for star in self.stars:
            star[1] += star[2]  # Mueve la estrella hacia abajo
            if star[1] > HEIGHT:
                star[1] = random.randint(-50, -10)  # Reinicia en la parte superior
                star[0] = random.randint(0, WIDTH)
                star[2] = random.uniform(1, 3)
                star[3] = random.randint(180, 255)

    # Dibuja gradiente y estrellas fugaces
    def draw(self, surface):
        surface.blit(self.gradient_surface, (0, 0))
        for x, y, speed, brightness in self.stars:
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (int(x), int(y)), 2)