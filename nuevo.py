import pygame
import pygame_menu
from config import save_scores, load_scores, add_score, WIDTH, HEIGHT

def show_initials_input_menu(surface, score, music_manager, on_return):
    print(f"Mostrando menú para ingresar iniciales con puntuacion: {score}")
    music_manager.play_game('menu_music.mp3')
    
    menu_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_theme.background_color = (15, 10, 25)
    menu_theme.title_font = pygame_menu.font.FONT_8BIT
    menu_theme.title_font_size = 40
    menu_theme.title_background_color = (120, 0, 20)
    menu_theme.title_font_color = (255, 255, 255)
    menu_theme.widget_font_size = 26
    menu_theme.widget_font_color = (255, 255, 255)
    menu_theme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection(arrow_size=(15, 20))
    menu_theme.widget_background_color = (40, 20, 40)
    menu_theme.widget_alignment = pygame_menu.locals.ALIGN_CENTER
    menu_theme.widget_border_radius = 25
    menu_theme.widget_border_width = 2
    menu_theme.widget_border_color = (255, 255, 255)
    menu_theme.widget_padding = (8, 35)
    menu_theme.widget_margin = (0, 10)
    menu_theme.widget_font = pygame_menu.font.FONT_8BIT

    menu = pygame_menu.Menu('Ingresa tus iniciales', WIDTH, HEIGHT, theme=menu_theme)
    initials_input = menu.add.text_input('Iniciales  ', maxchar=3, input_type=pygame_menu.locals.INPUT_TEXT, input_underline=' ')
    error_label = None
    ERROR_TIMEOUT_EVENT = pygame.USEREVENT + 1

    def save_initials_and_return():
        nonlocal error_label
        initials = initials_input.get_value().strip().upper()
        print(f"Iniciales ingresadas  {initials}")
        if len(initials) != 3 or not initials.isalpha():
            print("Error: No se ingresaron exactamente 3 letras")
            if error_label:
                menu.remove_widget(error_label)
            error_label = menu.add.label("Ingresa exactamente 3 letras", font_size=20, font_color=(255, 0, 0))
            pygame.time.set_timer(ERROR_TIMEOUT_EVENT, 2000, 1)
            return
        try:
            add_score(initials, score)  # Use add_score instead of save_scores
            print(f"Iniciales y puntuacion guardadas: {initials}, {score}")
            menu.disable()
            if callable(on_return):
                on_return()
        except Exception as e:
            print(f"Error al guardar las iniciales: {e}")
            if error_label:
                menu.remove_widget(error_label)
            error_label = menu.add.label("Error al guardar, intenta de nuevo", font_size=20, font_color=(255, 0, 0))
            pygame.time.set_timer(ERROR_TIMEOUT_EVENT, 2000, 1)

    menu.add.label(f"Puntuacion  {score}", font_size=24)
    menu.add.vertical_margin(20)
    menu.add.button('Guardar', save_initials_and_return)
    menu.add.button('Volver', on_return)

    def handle_events(events):
        nonlocal error_label
        for event in events:
            if event.type == ERROR_TIMEOUT_EVENT and error_label:
                menu.remove_widget(error_label)
                error_label = None
        return events

    menu.mainloop(surface, events_callback=handle_events)

def show_game_over_menu(surface, score1, score2, music_manager, skin1, skin2, store_manager):
    print("Mostrando menú de fin de juego")
    music_manager.play_game('menu_music.mp3')
    menu_over_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_over_theme.background_color = (15, 10, 25)
    menu_over_theme.title_font = pygame_menu.font.FONT_8BIT
    menu_over_theme.title_font_size = 40
    menu_over_theme.title_background_color = (120, 0, 20)
    menu_over_theme.title_font_color = (255, 255, 255)
    menu_over_theme.widget_font_size = 20
    menu_over_theme.widget_font_color = (255, 255, 255)
    menu_over_theme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection(arrow_size=(15, 20))
    menu_over_theme.widget_background_color = (40, 20, 40)
    menu_over_theme.widget_alignment = pygame_menu.locals.ALIGN_CENTER
    menu_over_theme.widget_border_radius = 25
    menu_over_theme.widget_border_width = 2
    menu_over_theme.widget_border_color = (255, 255, 255)
    menu_over_theme.widget_padding = (8, 20)
    menu_over_theme.widget_margin = (0, 10)
    menu_over_theme.widget_font = pygame_menu.font.FONT_8BIT

    menu_over = pygame_menu.Menu('Fin del Juego', WIDTH, HEIGHT, theme=menu_over_theme)

    if score2 > 0:
        menu_over.add.label(f"Puntuacion J1 {score1}", font_size=20)
        menu_over.add.label(f"Puntuacion J2 {score2}", font_size=20)
        menu_over.add.label(f"Total {max(score1, score2)}", font_size=22)
    else:
        menu_over.add.label(f"Puntuacion Final: {score1}", font_size=22)
    menu_over.add.vertical_margin(15)

    scores = load_scores()
    print(f"Puntuaciones mostradas en el menú de fin de juego: {scores}")
    menu_over.add.label("Mejores Puntuaciones", font_size=20)
    if scores:
        for i, (initials, s) in enumerate(scores[:5]):
            menu_over.add.label(f"{i+1}. {initials}: {s}", font_size=18)
    else:
        menu_over.add.label("No hay puntuaciones registradas", font_size=22)
    for i in range(len(scores), 5):
        menu_over.add.label(f"{i+1}. ---: 0", font_size=22)
    menu_over.add.vertical_margin(20)

    def restart_game():
        from juego_retro import game_loop
        from juego_dos_jugadores import game_loop_2p
        menu_over.disable()
        if score2 > 0:
            game_loop_2p(surface, store_manager, music_manager, skin1, skin2)
        else:
            game_loop(surface, store_manager, music_manager, skin1)

    def return_to_lobby():
        menu_over.disable()

    menu_over.add.button('Reiniciar', restart_game)
    menu_over.add.button('Lobby', return_to_lobby)

    menu_over.mainloop(surface)