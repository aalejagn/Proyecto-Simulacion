import pygame
import pygame_menu
import random
import json
import os
import sys
import math
import traceback
import pygame_menu.events
import pygame_menu.widgets
from pygame.locals import *
from skines_obtenidas import SkinManager
from tienda import StoreManager
from canciones import ManejoMusica
from sprites import LaneManager, Player, Rival, Obstacle, Explosion, ScoreDisplay
from juego_dos_jugadores import game_loop_2p
from config import (
    WIDTH, HEIGHT, LANES, LANE_WIDTH, FPS, LIVES, SCORES_FILE, TOP_SCORES,
    BASE_SPEED, SPEED_GROWTH_RATE, MAX_SPEED, BASE_POINTS, POINTS_GROWTH,
    BASE_LEVEL_UP, LEVEL_UP_GROWTH_RATE, BASE_ENEMIES, BASE_OBSTACLES,
    MAX_ENEMIES, MAX_OBSTACLES, get_level_speed, get_level_points,
    get_level_up_threshold, get_enemy_count, get_obstacle_count,
    load_scores, save_scores
)
from assets import load_images

def game_loop(surface, store_manager, music_manager, player_skin):
    music_manager.play_game('game_music.mp3')
    clock = pygame.time.Clock()
    lane_manager = LaneManager()
    player = Player(2, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}, player_skin)
    score_display = ScoreDisplay(player_skin)
    current_level = 1
    current_speed = get_level_speed(current_level)
    points_per_car = get_level_points(current_level)
    enemy_count = get_enemy_count(current_level)
    obstacle_count = get_obstacle_count(current_level)
    rivals = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    explosions = pygame.sprite.Group()

    # Cargar imágenes y crear enemigos y obstáculos iniciales
    ENEMY_IMG, OBSTACLE_IMG = load_images()
    print(f"Loaded ENEMY_IMG size: {ENEMY_IMG.get_size()}")
    print(f"Loaded OBSTACLE_IMG size: {OBSTACLE_IMG.get_size()}")
    print(f"LANE_WIDTH: {LANE_WIDTH}")  # Añadido para depurar el tamaño del carril

    # Crear enemigos iniciales
    for _ in range(enemy_count):
        rivals.add(Rival(current_speed, lane_manager, ENEMY_IMG))

    # Crear obstáculos iniciales
    for _ in range(obstacle_count):
        obstacles.add(Obstacle(current_speed, lane_manager, OBSTACLE_IMG, debug=False))

    score = 0
    lives = LIVES
    running = True
    paused = False
    font = pygame.font.SysFont(None, 48)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                music_manager.limpieza()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == player.controls['left']:
                    player.move_left()
                elif event.key == player.controls['right']:
                    player.move_right()
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    if paused:
                        store_manager.add_points(score)
                        music_manager.play_game('menu_music.mp3')
                        return
                    paused = True

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
                store_manager.add_points(score)
                music_manager.play_game('game_music.mp3')
                return game_loop(surface, store_manager, music_manager, player_skin)
            clock.tick(FPS)
            continue

        player.update()
        explosions.update()
        for r in rivals:
            if r.update(player.lane):
                score += points_per_car
                new_level = math.floor(score / get_level_up_threshold(current_level)) + 1
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
                        obstacles.add(Obstacle(current_speed, lane_manager, OBSTACLE_IMG, debug=False))

        for o in obstacles:
            o.update(player.lane)

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
                    print("Reproduciendo explosión")
                    music_manager.play_sound('explosion_sound.mp3')
                    obstacle_hit.reset(player.lane)
                if lives == 0:
                    scores = load_scores()
                    scores.append(score)
                    save_scores(sorted(scores, reverse=True)[:TOP_SCORES])
                    store_manager.add_points(score)
                    break

        surface.fill((50, 50, 50))
        for i in range(1, LANES):
            pygame.draw.line(surface, (200, 200, 200), (i*LANE_WIDTH, 0), (i*LANE_WIDTH, HEIGHT))
        rivals.draw(surface)
        obstacles.draw(surface)
        surface.blit(player.image, player.rect)
        explosions.draw(surface)
        score_display.update(score, 0, current_level, lives)
        score_display.draw(surface)
        pygame.display.flip()
        clock.tick(FPS)

    music_manager.play_game('menu_music.mp3')
    menu_over_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_over_theme.background_color = (15, 10, 25)
    menu_over_theme.title_font = pygame_menu.font.FONT_8BIT
    menu_over_theme.title_font_size = 48
    menu_over_theme.title_background_color = (120, 0, 20)
    menu_over_theme.title_font_color = (255, 255, 255)
    menu_over_theme.widget_font_size = 26
    menu_over_theme.widget_font_color = (255, 255, 255)
    menu_over_theme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection(arrow_size=(15, 20))
    menu_over_theme.widget_background_color = (40, 20, 40)
    menu_over_theme.widget_alignment = pygame_menu.locals.ALIGN_CENTER
    
    menu_over_theme.widget_border_radius   = 25    # esquinas redondeadas
    menu_over_theme.widget_border_width    = 2
    menu_over_theme.widget_border_color    = (255, 255, 255)
    menu_over_theme.widget_padding         = (8, 35)  # (vertical, horizontal)
    menu_over_theme.widget_margin          = (0, 10)   # separación entre botones
    

    
    menu_over = pygame_menu.Menu('Fin del Juego', WIDTH, HEIGHT, theme=menu_over_theme)
    menu_over.add.label(f"Puntuación Final  {score}", font_size=32)
    menu_over.add.vertical_margin(15)
    scores = load_scores()
    if scores:
        menu_over.add.label("Mejores Puntuaciones", font_size=26)
        for i, s in enumerate(scores[:3]):
            menu_over.add.label(f"{i+1}. {s}", font_size=22)
        menu_over.add.vertical_margin(20)
        
        # 3) Fuente y color de texto
    menu_over_theme.widget_font            = pygame_menu.font.FONT_8BIT
    lobby_selected = [False]  # Mutable para modificar dentro del botón
    
    menu_over.add.button('Reiniciar', lambda: game_loop(surface, store_manager, music_manager, player_skin))
    menu_over.add.button('Lobby', lambda: lobby_selected.__setitem__(0, True))

    while True:
        surface.fill((15, 10, 25))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if lobby_selected[0]:
            break  # Salir del menú y volver al menú principal

        menu_over.update(events)
        menu_over.draw(surface)
        pygame.display.flip()
    



def main():
    pygame.init()
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Juego Retro de Carritos")

    skin_manager = SkinManager(WIDTH, HEIGHT)
    store_manager = StoreManager(WIDTH, HEIGHT, skin_manager)
    music_manager = ManejoMusica()

    menu_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_theme.background_color = (10, 10, 30)
    menu_theme.title_font = pygame_menu.font.FONT_8BIT
    menu_theme.title_font_size = 50
    menu_theme.widget_font_size = 28
    menu_theme.title_background_color = (50, 20, 100)
    menu_theme.title_font_color = (255, 255, 0)
    menu_theme.widget_font_color = (255, 255, 255)
    menu_theme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection(arrow_size=(15, 20))
    menu_theme.widget_background_color = (30, 30, 60)
    menu_theme.widget_alignment = pygame_menu.locals.ALIGN_CENTER
    # 2) Bordes y padding
    menu_theme.widget_border_radius   = 25    # esquinas redondeadas
    menu_theme.widget_border_width    = 2
    menu_theme.widget_border_color    = (255, 255, 255)
    menu_theme.widget_padding         = (8, 35)  # (vertical, horizontal)
    menu_theme.widget_margin          = (0, 10)   # separación entre botones
    
    # 3) Fuente y color de texto
    menu_theme.widget_font            = pygame_menu.font.FONT_8BIT

    
  # 4) Crea tu menú con este tema
    menu = pygame_menu.Menu(
        title='Carreras Retro',
        width=WIDTH,
        height=HEIGHT,
        theme=menu_theme
    )
    music_manager.play_game('menu_music.mp3')


    def show_skin_menu(menu, surface, skin_manager):
        music_manager.play_game('menu_music.mp3')
        menu.disable()
        def on_select():
            menu.enable()
            music_manager.play_game('menu_music.mp3')
        def volver():
            menu.enable()
            music_manager.play_game('menu_music.mp3')
        skin_menu = skin_manager.create_skin_selection_menu(
            surface,
            on_return=volver,
            on_select=on_select
        )
        skin_menu.mainloop(surface)

    def show_store_menu(menu, surface, store_manager):
        music_manager.play_game('menu_music.mp3')
        menu.disable()
        def on_return():
            menu.enable()
            music_manager.play_game('menu_music.mp3')
        try:
            store_menu = store_manager.create_store_menu(surface, on_return)
            store_menu.mainloop(surface)
        except Exception as e:
            print(f"Error abriendo menú de tienda: {e}\nTraceback:\n{traceback.format_exc()}")
            print("Revisa la carpeta SKIN_STORE para skin_store1.png, skin_store2.png, skin_store3.png")
            menu.enable()

    scores = load_scores()
    if scores:
        menu.add.label("Records", font_size=20, align=pygame_menu.locals.ALIGN_LEFT)
        for i, s in enumerate(scores[:3]):
            menu.add.label(f"N{i+1}  {s}", font_size=12, align=pygame_menu.locals.ALIGN_LEFT)
        menu.add.vertical_margin(20)

    def crear_botones(texto, accion, color_fondo, color_texto):
        boton = menu.add.button(texto, accion, font_color=color_texto, align=pygame_menu.locals.ALIGN_CENTER)
        boton.set_padding((10, 20, 10, 20))
        boton.set_max_width(300)
        boton.set_background_color(color_fondo)



    menu_theme.widget_font_size = 25  # Tamaño base para todos los widgets
    
    # 1 Jugador
    btn1 = menu.add.button(
        "1 Jugador",
        lambda: game_loop(
            surface,
            store_manager,
            music_manager,
            skin_manager.get_current_game_skin(player=1)
        ),
        align=pygame_menu.locals.ALIGN_CENTER
    )
    btn1.set_background_color((30, 144, 255))
    btn1.translate(
        0,  # Posición X (20px desde la derecha)
        -100  # Posición Y (20px desde abajo)
    )

    # 2 Jugadores
    btn2 = menu.add.button(
        "2 Jugadores",
        lambda: game_loop_2p(
            surface,
            store_manager,
            music_manager,
            skin_manager.get_current_game_skin(player=1),
            skin_manager.get_current_game_skin(player=2)
        ),
        align=pygame_menu.locals.ALIGN_CENTER
    )
    btn2.set_background_color((50, 205, 50))
    btn2.translate(
        0,  # Posición X (20px desde la derecha)
        -95  # Posición Y (20px desde abajo)
    )


    # Salir
    btn_exit = menu.add.button("Salir", pygame_menu.events.EXIT, align=pygame_menu.locals.ALIGN_CENTER)
    btn_exit.set_background_color((220, 20, 60))
    btn_exit.translate(
        0,  # Posición X (20px desde la derecha)
        -65  # Posición Y (20px desde abajo)
    )
    
    # Skins (esquina)
    skin_btn = menu.add.button(
        """Skins""",
        lambda: show_skin_menu(menu, surface, skin_manager)
    )
    skin_btn.set_background_color((138, 43, 226))  # púrpura

    

    # Posicionamiento usando translate (funciona en todas versiones)
    skin_btn.translate(
        350,  # Posición X (20px desde la derecha)
        40  # Posición Y (20px desde abajo)
    )

    # Opcional: Configuración para que se mantenga visible
    skin_btn.set_float(True)  # Esto evita que se mueva con el scroll si lo hay
    
    # Tienda
    store_btn = menu.add.button(
        "Tienda",
        show_store_menu,
        menu, surface, store_manager,
        align=pygame_menu.locals.ALIGN_CENTER
        
    )
    store_btn.set_background_color((255, 215, 0))
    
        # Posicionamiento usando translate (funciona en todas versiones)
    store_btn.translate(
        -350,  # Posición X (20px desde la derecha)
        40  # Posición Y (20px desde abajo)
    )

    # Opcional: Configuración para que se mantenga visible
    store_btn.set_float(True)  # Esto evita que se mueva con el scroll si lo hay

    menu.mainloop(surface)
    music_manager.limpieza()
    pygame.quit()

if __name__ == '__main__':
    main()