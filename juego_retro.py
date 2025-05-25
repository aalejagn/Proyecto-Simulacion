import pygame
import pygame_menu
from nuevo import show_initials_input_menu, show_game_over_menu
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
from sprites import LaneManager, Player, Rival, Obstacle, Explosion, ScoreDisplay, Rain, Lightning, Snow, Sunrise
from juego_dos_jugadores import game_loop_2p
import config  # Importar configuraciones del juego
from assets import load_images  # Importar utilidad para cargar imágenes

# Bucle principal del juego para un jugador
def game_loop(surface, store_manager, music_manager, player_skin):
    music_manager.play_game('game_music.mp3')  # Inicia la música de fondo del juego
    clock = pygame.time.Clock()
    lane_manager = LaneManager()  # Administra la ocupación de carriles
    player = Player(2, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}, player_skin)  # Inicializa al jugador
    score_display = ScoreDisplay(player_skin)  # Inicializa la interfaz de usuario (HUD)
    current_level = 1
    current_speed = config.get_level_speed(current_level)  # Obtiene velocidad inicial
    points_per_car = config.get_level_points(current_level)  # Puntos por rival superado
    enemy_count = config.get_enemy_count(current_level)  # Cantidad de rivales
    obstacle_count = config.get_obstacle_count(current_level)  # Cantidad de obstáculos
    rivals = pygame.sprite.Group()  # Grupo para autos rivales
    obstacles = pygame.sprite.Group()  # Grupo para obstáculos
    explosions = pygame.sprite.Group()  # Grupo para efectos de explosión
    
    # Inicializa efectos climáticos según CURRENT_WEATHER
    weather_sprites = pygame.sprite.Group()
    weather_effect = None
    #TODO: Asegurar consistencia en la configuración del clima entre modos de juego
    print(f"Clima actual en game_loop: {config.CURRENT_WEATHER}")  # Depuración de configuración de clima
    if config.CURRENT_WEATHER == 'lluvioso':
        for _ in range(50):
            weather_sprites.add(Rain())  # Añade partículas de lluvia
        weather_effect = Lightning()  # Añade efecto de relámpago
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
    print(f"Loaded ENEMY_IMG size: {ENEMY_IMG.get_size()}")
    print(f"Loaded OBSTACLE_IMG size: {OBSTACLE_IMG.get_size()}")
    print(f"LANE_WIDTH: {config.LANE_WIDTH}")

    for _ in range(enemy_count):
        rivals.add(Rival(current_speed, lane_manager, ENEMY_IMG))  # Genera rivales
    for _ in range(obstacle_count):
        obstacles.add(Obstacle(current_speed, lane_manager, OBSTACLE_IMG, debug=False))  # Genera obstáculos

    score = 0
    lives = config.LIVES
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
                if event.key == player.controls['left']:
                    player.move_left()
                elif event.key == player.controls['right']:
                    player.move_right()
                elif event.key == pygame.K_p:
                    paused = not paused  # Alterna estado de pausa
                elif event.key == pygame.K_ESCAPE:
                    if paused:
                        store_manager.add_points(score)  # Guarda puntuación
                        music_manager.play_game('menu_music.mp3')
                        return
                    paused = True

        if paused:
            pause_surface = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            pause_surface.fill((0, 0, 0, 150))  # Superposición semi-transparente para pausa
            surface.blit(pause_surface, (0, 0))
            pause_text = font.render("PAUSA", True, (255, 255, 255))
            continue_text = font.render("P: Continuar", True, (200, 200, 200))
            restart_text = font.render("R: Reiniciar", True, (200, 200, 200))
            quit_text = font.render("ESC: Salir", True, (200, 200, 200))
            surface.blit(pause_text, (config.WIDTH//2 - pause_text.get_width()//2, config.HEIGHT//2 - 100))
            surface.blit(continue_text, (config.WIDTH//2 - continue_text.get_width()//2, config.HEIGHT//2))
            surface.blit(restart_text, (config.WIDTH//2 - restart_text.get_width()//2, config.HEIGHT//2 + 50))
            surface.blit(quit_text, (config.WIDTH//2 - quit_text.get_width()//2, config.HEIGHT//2 + 100))
            pygame.display.flip()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                store_manager.add_points(score)
                music_manager.play_game('game_music.mp3')
                return game_loop(surface, store_manager, music_manager, player_skin)
            clock.tick(config.FPS)
            continue

        player.update()
        explosions.update()
        weather_sprites.update()
        if weather_effect:
            weather_effect.update(music_manager)

        for r in rivals:
            if r.update(player.lane):
                score += points_per_car
                new_level = math.floor(score / config.get_level_up_threshold(current_level)) + 1
                if new_level > current_level:
                    current_level = new_level
                    current_speed = config.get_level_speed(current_level)
                    points_per_car = config.get_level_points(current_level)
                    for spr in rivals:
                        spr.speed = current_speed
                    for spr in obstacles:
                        spr.speed = current_speed
                    new_enemy_count = config.get_enemy_count(current_level)
                    new_obstacle_count = config.get_obstacle_count(current_level)
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
                    store_manager.add_points(score)
                    #TODO: Verificar si la puntuación califica para el top 5
                    current_scores = config.load_scores()
                    qualifies_for_top_5 = len(current_scores) < 5 or any(score > s[1] for s in current_scores[:5])
                    if qualifies_for_top_5:
                        show_initials_input_menu(surface, score, music_manager, lambda: show_game_over_menu(surface, score, 0, music_manager, player_skin, None, store_manager))
                    else:
                        show_game_over_menu(surface, score, 0, music_manager, player_skin, None, store_manager)
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
        for i in range(1, config.LANES):
            pygame.draw.line(surface, (200, 200, 200), (i*config.LANE_WIDTH, 0), (i*config.LANE_WIDTH, config.HEIGHT))
        rivals.draw(surface)
        obstacles.draw(surface)
        surface.blit(player.image, player.rect)
        explosions.draw(surface)
        if weather_effect and config.CURRENT_WEATHER != 'amanecer':
            weather_effect.draw(surface)
        score_display.update(score, 0, current_level, lives)
        score_display.draw(surface)
        pygame.display.flip()
        clock.tick(config.FPS)

    music_manager.play_game('menu_music.mp3')
    return

# Función principal para inicializar el juego
def main():
    pygame.init()
    surface = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Juego Retro de Carritos")

    skin_manager = SkinManager(config.WIDTH, config.HEIGHT)
    store_manager = StoreManager(config.WIDTH, config.HEIGHT, skin_manager)
    music_manager = ManejoMusica()

    # Configura el tema del menú
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
    menu_theme.widget_border_radius = 25
    menu_theme.widget_border_width = 2
    menu_theme.widget_border_color = (255, 255, 255)
    menu_theme.widget_padding = (8, 35)
    menu_theme.widget_margin = (0, 10)
    menu_theme.widget_font = pygame_menu.font.FONT_8BIT

    menu = pygame_menu.Menu(
        title='Carreras Retro',
        width=config.WIDTH,
        height=config.HEIGHT,
        theme=menu_theme
    )
    music_manager.play_game('menu_music.mp3')

    # Muestra el menú de selección de skins
    def show_skin_menu(menu, surface, skin_manager):
        music_manager.play_game('menu_music.mp3')
        menu.disable()
        def on_select():
            menu.enable()
            music_manager.play_game('menu_music.mp3')
        def volver():
            menu.enable()  # Reactiva el menú principal
            music_manager.play_game('menu_music.mp3')
        
        skin_menu = skin_manager.create_skin_selection_menu(
            surface,
            on_return=volver,  # Asigna la función volver como callback
            on_select=on_select
        )
        skin_menu.mainloop(surface)

    # Muestra el menú de la tienda
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

    # Cambia el clima del juego
    def change_weather(value, weather):
        #TODO: Actualizar CURRENT_WEATHER en config para reflejar el cambio
        config.CURRENT_WEATHER = weather
        print(f"Clima cambiado a: {config.CURRENT_WEATHER}")

    #TODO: Cargar y mostrar las puntuaciones altas en el menú principal
    scores = config.load_scores()
    if scores:
        menu.add.label("Records", font_size=20, align=pygame_menu.locals.ALIGN_LEFT)
        for i, (initials, s) in enumerate(scores[:5]):
            menu.add.label(f"N{i+1}  {initials}: {s}", font_size=12, align=pygame_menu.locals.ALIGN_LEFT)
        menu.add.vertical_margin(20)

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
    btn1.translate(0, -100)

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
    btn2.translate(0, -95)

    btn_exit = menu.add.button("Salir", pygame_menu.events.EXIT, align=pygame_menu.locals.ALIGN_CENTER)
    btn_exit.set_background_color((220, 20, 60))
    btn_exit.translate(0, -65)

    skin_btn = menu.add.button(
        "Skins",
        lambda: show_skin_menu(menu, surface, skin_manager)
    )
    skin_btn.set_background_color((138, 43, 226))
    skin_btn.translate(389, -440)
    skin_btn.set_float(True)

    store_btn = menu.add.button(
        "Tienda",
        show_store_menu,
        menu, surface, store_manager,
        align=pygame_menu.locals.ALIGN_CENTER
    )
    store_btn.set_background_color((255, 215, 0))
    store_btn.translate(-350, 40)
    store_btn.set_float(True)

    # Añade selector de clima
    weather_selector = menu.add.selector(
        title="Clima: ",
        items=[('Lluvioso', 'lluvioso'), ('Nevado', 'nevado'), ('Amanecer', 'amanecer')],
        default=0,
        onchange=change_weather,
        align=pygame_menu.locals.ALIGN_CENTER
    )
    weather_selector.set_background_color((0, 191, 255))
    weather_selector.translate(230, 40)
    weather_selector.set_float(True)

    menu.mainloop(surface)
    music_manager.limpieza()
    pygame.quit()
    
if __name__ == '__main__':
    main()