import pygame
import random
from config import WIDTH, HEIGHT, LANES, LANE_WIDTH, LIVES, get_level_up_threshold, load_scores

class Player(pygame.sprite.Sprite):
    def __init__(self, initial_lane, controls, skin):
        super().__init__()
        self.original_image = skin
        self.image = pygame.transform.scale(self.original_image, (LANE_WIDTH-20, 60))
        self.lane = initial_lane
        self.rect = self.image.get_rect()
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.invincible = False
        self.invincible_timer = 0
        self.controls = controls  # Ej: {"left": pygame.K_a, "right": pygame.K_d}
        self.active = True  # Está activo por defecto
        
    def move_left(self):
        if not self.active:
            return
        if self.lane > 0:
            self.lane -= 1
            self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2

    def move_right(self):
        if not self.active:
            return
        if self.lane < LANES - 1:
            self.lane += 1
            self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2

    def update(self):
        if not self.active:
            return  # Si está muerto, no hace nada
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
    def __init__(self):
        self.reset()

    def reset(self):
        self.occupied = {lane: None for lane in range(LANES)}

    def get_random_lane(self):
        return random.randint(0, LANES - 1)

    def get_random_lane_avoiding(self, player_lane):
        adjacent_lanes = [player_lane - 1, player_lane + 1]
        adjacent_lanes = [l for l in adjacent_lanes if 0 <= l < LANES]
        free_lanes = [lane for lane in range(LANES) if lane not in adjacent_lanes or self.occupied.get(lane) is None]
        if free_lanes:
            return random.choice(free_lanes)
        return random.randint(0, LANES - 1)

    def occupy_lane(self, lane, obj_type):
        if 0 <= lane < LANES:
            self.occupied[lane] = obj_type

    def free_lane(self, lane):
        if 0 <= lane < LANES:
            self.occupied[lane] = None

class Rival(pygame.sprite.Sprite):
    def __init__(self, speed, lane_manager, enemy_img):
        super().__init__()
        self.speed = speed
        self.lane_manager = lane_manager
        self.lane = -1
        self.image = pygame.transform.scale(enemy_img, (LANE_WIDTH-20, 60))
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self, player_lane=None):
        if player_lane is None:
            player_lane = LANES // 2
        self.lane = self.lane_manager.get_random_lane_avoiding(player_lane)
        self.lane_manager.occupy_lane(self.lane, 'enemy')
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.y = -self.rect.height - random.randint(0, 100)

    def update(self, player_lane=None):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.lane_manager.free_lane(self.lane)
            self.reset(player_lane)
            return True
        return False

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed, lane_manager, image, debug=False):
        super().__init__()
        # Escalar la imagen al tamaño deseado
        self.image = pygame.transform.scale(image, (LANE_WIDTH-20, 60))
        self.rect = self.image.get_rect()
        if debug:
            print(f"Obstacle initialized with image size: {self.image.get_size()}, rect: {self.rect}")
        self.lane_manager = lane_manager
        self.lane = self.lane_manager.get_random_lane()
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.bottom = 0
        self.speed = speed

    def update(self, player_lane=None):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.lane_manager.free_lane(self.lane)
            self.reset(player_lane)
            return True
        return False

    def reset(self, player_lane):
        self.lane = self.lane_manager.get_random_lane_avoiding(player_lane)
        self.rect.centerx = self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.rect.bottom = 0
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
    def __init__(self, life_icon_img):
        self.score1 = 0
        self.score2 = 0
        self.level = 1
        self.lives = LIVES
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.high_scores = load_scores()
        self.life_icon_img = pygame.transform.scale(life_icon_img, (30, 30))

    def update(self, score1, score2, level, lives):
        self.score1 = score1
        self.score2 = score2
        self.level = level
        self.lives = lives

    def draw(self, surface):
        hud = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 150))
        surface.blit(hud, (0, 0))
        score1_text = self.big_font.render(f"J1: {self.score1}", True, (255, 255, 255))
        score2_text = self.big_font.render(f"J2: {self.score2}", True, (255, 255, 255))
        surface.blit(score1_text, (20, 20))
        surface.blit(score2_text, (120, 20))
        level_text = self.font.render(f"Nivel: {self.level}", True, (200, 200, 200))
        surface.blit(level_text, (WIDTH - 120, 20))
        for i in range(self.lives):
            surface.blit(self.life_icon_img, (20 + i * 40, 60))
        threshold = get_level_up_threshold(self.level)
        progress = (max(self.score1, self.score2) % threshold) / threshold
        pygame.draw.rect(surface, (100, 100, 100), (WIDTH - 120, 60, 100, 10))
        pygame.draw.rect(surface, (0, 255, 0), (WIDTH - 120, 60, int(100 * progress), 10))
        
        
class ScoreDisplay2:
    def __init__(self, skin):
        self.score1 = 0
        self.score2 = 0
        self.level = 1
        self.lives1 = 0
        self.lives2 = 0
        self.font = pygame.font.SysFont(None, 36)

    def update(self, score1, score2, level, lives1, lives2):
        self.score1 = score1
        self.score2 = score2
        self.level = level
        self.lives1 = lives1
        self.lives2 = lives2

    def draw(self, surface):
        text1 = self.font.render(f"J1: {self.score1}  Vidas: {self.lives1}", True, (255, 255, 255))
        text2 = self.font.render(f"J2: {self.score2}  Vidas: {self.lives2}", True, (255, 255, 255))
        level_text = self.font.render(f"Nivel: {self.level}", True, (255, 255, 0))

        surface.blit(text1, (20, 10))
        surface.blit(text2, (20, 50))
        surface.blit(level_text, (WIDTH - 150, 10))
