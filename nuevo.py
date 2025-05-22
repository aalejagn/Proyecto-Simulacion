import pygame
import pygame_menu
from config import load_scores, add_score, WIDTH, HEIGHT

def show_initials_input_menu(surface, score, music_manager, on_return):
    """
    Muestra un menú para que el jugador ingrese sus iniciales (3 letras) después de perder.
    Args:
        surface: Superficie de pygame donde se renderiza el menú.
        score: Puntuación final del jugador.
        music_manager: Instancia de ManejoMusica para controlar la música.
        on_return: Función a llamar después de guardar las iniciales.
    """
    print(f"Mostrando menú para ingresar iniciales con puntuación: {score}")
    # TODO: Configurar el tema del menú para que sea simple y claro
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.title_font = pygame.font.SysFont('Arial', 20)
    theme.title_font_size = 20
    theme.widget_font = pygame.font.SysFont('Arial', 18)
    theme.widget_font_size = 24
    theme.background_color = (15, 10, 25)

    # TODO: Crear el menú con un campo de texto para las iniciales
    menu = pygame_menu.Menu(
        title='Ingresa tus iniciales',
        width=WIDTH,
        height=HEIGHT,
        theme=theme,
        onclose=pygame_menu.events.BACK
    )

    # TODO: Agregar un campo de texto que acepte solo 3 letras
    initials_input = menu.add.text_input(
        'Iniciales: ',
        maxchar=3,  # Máximo 3 caracteres
        input_type=pygame_menu.locals.INPUT_TEXT,
        textinput_id='initials',
        onreturn=lambda value: None  # No hacer nada al presionar Enter por ahora
    )

    # TODO: Agregar un botón para guardar las iniciales y volver
    def save_initials_and_return():
        initials = initials_input.get_value().strip().upper()  # Convertir a mayúsculas
        print(f"Iniciales ingresadas: {initials}")
        if len(initials) == 3:  # Asegurarse de que sean exactamente 3 letras
            try:
                add_score(initials, score)  # Guardar la puntuación con las iniciales
                print(f"Iniciales y puntuación enviadas a add_score: {initials}, {score}")
                menu.disable()
                if callable(on_return):
                    on_return()
            except Exception as e:
                print(f"Error al guardar las iniciales: {e}")
                error_label = menu.add.label("Error al guardar, intenta de nuevo", font_size=20, font_color=(255, 0, 0))
                menu.add.timer(2.0, lambda: menu.remove_widget(error_label))
        else:
            print("Error: No se ingresaron exactamente 3 letras")
            error_label = menu.add.label("Por favor ingresa 3 letras", font_size=20, font_color=(255, 0, 0))
            menu.add.timer(2.0, lambda: menu.remove_widget(error_label))

    menu.add.button('Guardar', save_initials_and_return)

    # TODO: Mostrar el menú en la pantalla
    menu.mainloop(surface)

def show_game_over_menu(surface, score1, score2, music_manager, skin1, skin2, store_manager):
    """
    Muestra el menú de fin de juego con las puntuaciones y opciones para reiniciar o volver al lobby.
    Args:
        surface: Superficie de pygame donde se renderiza el menú.
        score1: Puntuación del jugador 1.
        score2: Puntuación del jugador 2 (0 si es modo de 1 jugador).
        music_manager: Instancia de ManejoMusica para controlar la música.
        skin1: Skin del jugador 1.
        skin2: Skin del jugador 2 (puede ser None si es modo de 1 jugador).
        store_manager: Instancia de StoreManager para guardar puntos.
    """
    print("Mostrando menú de fin de juego")
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
    menu_over_theme.widget_border_radius = 25
    menu_over_theme.widget_border_width = 2
    menu_over_theme.widget_border_color = (255, 255, 255)
    menu_over_theme.widget_padding = (8, 20)
    menu_over_theme.widget_margin = (0, 10)
    menu_over_theme.widget_font = pygame_menu.font.FONT_8BIT

    menu_over = pygame_menu.Menu('Fin del Juego', WIDTH, HEIGHT, theme=menu_over_theme)

    if score2 > 0:
        menu_over.add.label(f"Puntuación J1: {score1}", font_size=32)
        menu_over.add.label(f"Puntuación J2: {score2}", font_size=32)
        menu_over.add.label(f"Total: {max(score1, score2)}", font_size=32)
    else:
        menu_over.add.label(f"Puntuación Final: {score1}", font_size=32)
    menu_over.add.vertical_margin(15)

    scores = load_scores()
    print(f"Puntuaciones mostradas en el menú de fin de juego: {scores}")
    if scores:
        menu_over.add.label("Mejores Puntuaciones:", font_size=26)
        for i, (initials, s) in enumerate(scores[:5]):
            menu_over.add.label(f"{i+1}. {initials}: {s}", font_size=22)
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