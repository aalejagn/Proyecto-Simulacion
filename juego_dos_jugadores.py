import pygame
import sys
import math
import pygame_menu
import pygame_menu.widgets
from nuevo import show_initials_input_menu, show_game_over_menu
from config import (
    WIDTH, HEIGHT, LANES, LANE_WIDTH, FPS, LIVES, TOP_SCORES,
    get_level_speed, get_level_points, get_level_up_threshold,
    get_enemy_count, get_obstacle_count, load_scores
)
from assets import load_images
from sprites import LaneManager, Player, Rival, Obstacle, Explosion, ScoreDisplay2

def game_loop_2p(surface, store_manager, music_manager, skin1, skin2):
    music_manager.play_game('game_music.mp3')
    clock = pygame.time.Clock()
    lane_manager = LaneManager()
    player1 = Player(2, {'left': pygame.K_a, 'right': pygame.K_d}, skin1)  # J1 en carril 2
    player2 = Player(4, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}, skin2)  # J2 en carril 4
    players = pygame.sprite.Group()
    players.add(player1, player2)
    
    score_display = ScoreDisplay2(skin1)
    current_level = 1
    current_speed = get_level_speed(current_level)
    points_per_car = get_level_points(current_level)
    enemy_count = get_enemy_count(current_level)
    obstacle_count = get_obstacle_count(current_level)
    rivals = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    explosions = pygame.sprite.Group()

    ENEMY_IMG, OBSTACLE_IMG = load_images()

    for _ in range(enemy_count):
        rivals.add(Rival(current_speed, lane_manager, ENEMY_IMG))
    for _ in range(obstacle_count):
        obstacles.add(Obstacle(current_speed, lane_manager, OBSTACLE_IMG))

    # Inicialización previa al bucle
    score1 = 0
    score2 = 0
    lives1 = LIVES
    lives2 = LIVES
    running = True
    paused = False
    font = pygame.font.SysFont(None, 48)

    while running:
        # —————— Manejo de eventos ——————
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                music_manager.limpieza()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Movimiento J1
                if event.key == player1.controls['left']:
                    player1.move_left()
                elif event.key == player1.controls['right']:
                    player1.move_right()
                # Movimiento J2
                elif event.key == player2.controls['left']:
                    player2.move_left()
                elif event.key == player2.controls['right']:
                    player2.move_right()
                # Pausa
                elif event.key == pygame.K_p:
                    paused = not paused
                # Salir al menú
                elif event.key == pygame.K_ESCAPE and paused:
                    store_manager.add_points(score1 + score2)
                    music_manager.play_game('menu_music.mp3')
                    return

        if paused:
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
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                store_manager.add_points(score1 + score2)
                music_manager.play_game('game_music.mp3')
                return game_loop_2p(surface, store_manager, music_manager, skin1, skin2)
            clock.tick(FPS)
            continue

        player1.update()
        player2.update()
        explosions.update()
        for r in rivals:
            if r.update(min(player1.lane, player2.lane)):
                # Asignar puntos al jugador más cercano al carril del rival
                distance1 = abs(player1.lane - r.lane)
                distance2 = abs(player2.lane - r.lane)
                if distance1 < distance2:
                    score1 += points_per_car
                elif distance2 < distance1:
                    score2 += points_per_car
                else:
                    # Si están equidistantes, dividir puntos
                    score1 += points_per_car // 2
                    score2 += points_per_car // 2
                new_level = math.floor(max(score1, score2) / get_level_up_threshold(current_level)) + 1
                if new_level > current_level:
                    current_level = new_level
                    current_speed = get_level_speed(current_level)
                    points_per_car = get_level_points(current_level)
                    for spr in rivals:
                        spr.speed = current_speed
                    for spr in obstacles:
                        spr.speed = current_speed
                    new_enemy_count = get_enemy_count(current_level)
                    new_obstacle_count = get_obstacle_count(current_level)
                    while len(rivals) < new_enemy_count:
                        rivals.add(Rival(current_speed, lane_manager, ENEMY_IMG))
                    while len(obstacles) < new_obstacle_count:
                        obstacles.add(Obstacle(current_speed, lane_manager, OBSTACLE_IMG))

        for o in obstacles:
            o.update(min(player1.lane, player2.lane))

        if player1.alive() and not player1.invincible:
            rival_hit1 = pygame.sprite.spritecollideany(player1, rivals)
            obstacle_hit1 = pygame.sprite.spritecollideany(player1, obstacles)
            if rival_hit1 or obstacle_hit1:
                explosion = Explosion(player1.rect.center)
                explosions.add(explosion)
                lives1 -= 1
                player1.set_invincible(90)
                if lives1 <= 0 and player1.alive():
                    player1.kill()  # Lo elimina de todos los grupos a los que pertenece
                    player1.image = pygame.Surface((0, 0))
                    player1.rect.x = -1000
                if rival_hit1:
                    rival_hit1.reset(min(player1.lane, player2.lane))
                if obstacle_hit1:
                    print("Reproduciendo explosión")
                    music_manager.play_sound('explosion_sound.mp3')
                    obstacle_hit1.reset(min(player1.lane, player2.lane))

        if player2.alive() and not player2.invincible:
            rival_hit2 = pygame.sprite.spritecollideany(player2, rivals)
            obstacle_hit2 = pygame.sprite.spritecollideany(player2, obstacles)
            if rival_hit2 or obstacle_hit2:
                explosion = Explosion(player2.rect.center)
                explosions.add(explosion)
                lives2 -= 1
                player2.set_invincible(90)
                if lives2 <= 0 and player2.alive():
                    player2.kill()
                    player2.image = pygame.Surface((0, 0))
                    player2.rect.x = -1000
                if rival_hit2:
                    rival_hit2.reset(min(player1.lane, player2.lane))
                if obstacle_hit2:
                    print("Reproduciendo explosión")
                    music_manager.play_sound('explosion_sound.mp3')
                    obstacle_hit2.reset(min(player1.lane, player2.lane))

        # Verificar si ambos jugadores han perdido
        if lives1 <= 0 and lives2 <= 0:
            final_score = max(score1, score2)
            store_manager.add_points(final_score)
            current_scores = load_scores()
            if current_scores and len(current_scores) >= TOP_SCORES and final_score <= current_scores[-1][1]:
                # Si la puntuación no entra en el top 5, no pedimos iniciales
                show_game_over_menu(surface, score1, score2, music_manager, skin1, skin2, store_manager)
            elif current_level == "":
                show_game_over_menu(surface, score1, score2, music_manager, skin1, skin2, store_manager)
            else:
                # Si la puntuación entra en el top 5, pedimos iniciales
                show_initials_input_menu(surface, final_score, music_manager, lambda: show_game_over_menu(surface, score1, score2, music_manager, skin1, skin2, store_manager))
            break

        surface.fill((50, 50, 50))
        for i in range(1, LANES):
            pygame.draw.line(surface, (200, 200, 200), (i*LANE_WIDTH, 0), (i*LANE_WIDTH, HEIGHT))
        rivals.draw(surface)
        obstacles.draw(surface)
        if player1.alive():
            surface.blit(player1.image, player1.rect)   
        if player2.alive():
            surface.blit(player2.image, player2.rect)
        explosions.draw(surface)
        score_display.update(score1, score2, current_level, lives1, lives2)
        score_display.draw(surface)
        pygame.display.flip()
        clock.tick(FPS)

    # El menú de fin de juego ya se maneja dentro del bloque anterior, así que simplemente retornamos
    return