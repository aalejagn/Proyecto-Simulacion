import pygame
import sys
import math
import config  # Importar módulo de configuración
from nuevo import show_initials_input_menu, show_game_over_menu
from config import (
    WIDTH, HEIGHT, LANES, LANE_WIDTH, FPS, LIVES, TOP_SCORES,
    get_level_speed, get_level_points, get_level_up_threshold,
    get_enemy_count, get_obstacle_count, load_scores, add_score
)
from assets import load_images
from sprites import LaneManager, Player, Rival, Obstacle, Explosion, ScoreDisplay2, Rain, Lightning, Snow, Sunrise

# Bucle principal para el modo de dos jugadores
def game_loop_2p(surface, store_manager, music_manager, skin1, skin2,background):
    music_manager.play_game('game_music.mp3')  # Inicia la música de fondo
    clock = pygame.time.Clock()
    lane_manager = LaneManager()  # Administra ocupación de carriles
    player1 = Player(2, {'left': pygame.K_a, 'right': pygame.K_d}, skin1)  # Inicializa jugador 1
    player2 = Player(4, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}, skin2)  # Inicializa jugador 2
    players = pygame.sprite.Group()
    players.add(player1, player2)  # Agrupa ambos jugadores
    score_display = ScoreDisplay2(skin1)  # Inicializa HUD para dos jugadores
    current_level = 1
    current_speed = get_level_speed(current_level)  # Velocidad inicial
    points_per_car = get_level_points(current_level)  # Puntos por rival
    enemy_count = get_enemy_count(current_level)  # Cantidad de rivales
    obstacle_count = get_obstacle_count(current_level)  # Cantidad de obstáculos
    rivals = pygame.sprite.Group()  # Grupo de rivales
    obstacles = pygame.sprite.Group()  # Grupo de obstáculos
    explosions = pygame.sprite.Group()  # Grupo de explosiones
    
    # Inicializa efectos climáticos según CURRENT_WEATHER
    weather_sprites = pygame.sprite.Group()
    weather_effect = None
    #TODO: Asegurar que la configuración de clima sea consistente con el modo de un jugador
    print(f"Clima actual en game_loop_2p: {config.CURRENT_WEATHER}")  # Depuración de clima
    if config.CURRENT_WEATHER == 'lluvioso':
        for _ in range(50):
            weather_sprites.add(Rain())  # Añade partículas de lluvia
        weather_effect = Lightning()  # Añade relámpago
    elif config.CURRENT_WEATHER == 'nevado':
        for _ in range(50):
            weather_sprites.add(Snow())  # Añade partículas de nieve
        weather_effect = None
    elif config.CURRENT_WEATHER == 'amanecer':
        weather_effect = Sunrise()  # Añade efecto de amanecer
    else:
        print(f"Advertencia: Clima desconocido '{config.CURRENT_WEATHER}', usando lluvia por defecto")
        for _ in range(50):
            weather_sprites.add(Rain())
        weather_effect = Lightning()
    
    ENEMY_IMG, OBSTACLE_IMG = load_images()  # Carga imágenes de rivales y obstáculos

    for _ in range(enemy_count):
        rivals.add(Rival(current_speed, lane_manager, ENEMY_IMG))  # Genera rivales
    for _ in range(obstacle_count):
        obstacles.add(Obstacle(current_speed, lane_manager, OBSTACLE_IMG))  # Genera obstáculos

    score1 = 0
    score2 = 0
    lives1 = LIVES
    lives2 = LIVES
    running = True
    paused = False
    font = pygame.font.SysFont(None, 48)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                music_manager.limpieza()  # Libera recursos de música
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == player1.controls['left']:
                    player1.move_left()
                elif event.key == player1.controls['right']:
                    player1.move_right()
                elif event.key == player2.controls['left']:
                    player2.move_left()
                elif event.key == player2.controls['right']:
                    player2.move_right()
                elif event.key == pygame.K_p:
                    paused = not paused  # Alterna pausa
                elif event.key == pygame.K_ESCAPE and paused:
                    store_manager.add_points(score1 + score2)  # Guarda suma de puntuaciones
                    music_manager.play_game('menu_music.mp3')
                    return

        if paused:
            pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pause_surface.fill((0, 0, 0, 150))  # Superposición de pausa
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
        weather_sprites.update()
        if weather_effect:
            weather_effect.update(music_manager)
        for r in rivals:
            if r.update(min(player1.lane, player2.lane)):
                distance1 = abs(player1.lane - r.lane)
                distance2 = abs(player2.lane - r.lane)
                if distance1 < distance2:
                    score1 += points_per_car
                elif distance2 < distance1:
                    score2 += points_per_car
                else:
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
                    player1.kill()
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

        if lives1 <= 0 and lives2 <= 0:
            store_manager.add_points(score1 + score2)
            #TODO: Verificar si las puntuaciones de ambos jugadores califican para el top 5
            current_scores = load_scores()
            qualifies_for_top_5_p1 = len(current_scores) < TOP_SCORES or any(score1 > s[1] for s in current_scores[:TOP_SCORES])
            qualifies_for_top_5_p2 = len(current_scores) < TOP_SCORES or any(score2 > s[1] for s in current_scores[:TOP_SCORES])
            
            def show_game_over():
                show_game_over_menu(surface, score1, score2, music_manager, skin1, skin2, store_manager)
            
            if qualifies_for_top_5_p1:
                show_initials_input_menu(surface, score1, music_manager, 
                    lambda: show_initials_input_menu(surface, score2, music_manager, show_game_over) if qualifies_for_top_5_p2 else show_game_over())
            elif qualifies_for_top_5_p2:
                show_initials_input_menu(surface, score2, music_manager, show_game_over)
            else:
                show_game_over()
            break

        # Cambia el fondo según el clima
        if config.CURRENT_WEATHER == 'lluvioso':
            surface.fill((10, 10, 30))
        elif config.CURRENT_WEATHER == 'nevado':
            surface.fill((50, 50, 80))
        elif config.CURRENT_WEATHER == 'amanecer':
            weather_effect.draw(surface)
        else:
            surface.fill((10, 10, 30))

        weather_sprites.draw(surface)
        for i in range(1, LANES):
            pygame.draw.line(surface, (200, 200, 200), (i*LANE_WIDTH, 0), (i*LANE_WIDTH, HEIGHT))
        rivals.draw(surface)
        obstacles.draw(surface)
        if player1.alive():
            surface.blit(player1.image, player1.rect)
        if player2.alive():
            surface.blit(player2.image, player2.rect)
        explosions.draw(surface)
        if weather_effect and config.CURRENT_WEATHER != 'amanecer':
            weather_effect.draw(surface)
        score_display.update(score1, score2, current_level, lives1, lives2)
        score_display.draw(surface)
        pygame.display.flip()
        clock.tick(FPS)

    music_manager.play_game('menu_music.mp3')
    return