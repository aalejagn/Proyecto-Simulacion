import pygame
import os

def load_images():
    """
    Carga las imágenes estáticas del juego (enemigos y obstáculos).
    Las skins de los jugadores se manejan en SkinManager.
    """
    try:
        enemy_path = os.path.join("IMG_FOLDER", "enemy_img.png")  # Corregido a "enemy_img.png"
        obstacle_path = os.path.join("IMG_FOLDER", "obstaculo.png")
        print(f"Loading enemy image from: {os.path.abspath(enemy_path)}")
        print(f"Loading obstacle image from: {os.path.abspath(obstacle_path)}")
        if not os.path.exists(enemy_path):
            print(f"Enemy image not found: {enemy_path}")
        if not os.path.exists(obstacle_path):
            print(f"Obstacle image not found: {obstacle_path}")
        ENEMY_IMG = pygame.image.load(enemy_path).convert_alpha()
        OBSTACLE_IMG = pygame.image.load(obstacle_path).convert_alpha()
        print(f"Enemy image size: {ENEMY_IMG.get_size()}")
        print(f"Obstacle image size: {OBSTACLE_IMG.get_size()}")
    except Exception as e:
        print(f"Error cargando imágenes: {e}")
        # Imágenes de respaldo
        ENEMY_IMG = pygame.Surface((50, 80), pygame.SRCALPHA)
        pygame.draw.rect(ENEMY_IMG, (255, 0, 0), (10, 0, 30, 80))
        OBSTACLE_IMG = pygame.Surface((50, 80), pygame.SRCALPHA)
        pygame.draw.rect(OBSTACLE_IMG, (100, 100, 100), (10, 0, 30, 80))
        print(f"Using fallback images. Enemy size: {ENEMY_IMG.get_size()}, Obstacle size: {OBSTACLE_IMG.get_size()}")
    return ENEMY_IMG, OBSTACLE_IMG