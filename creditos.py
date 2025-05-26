import pygame
import pygame_menu
import os

# Inicializa Pygame y el mixer (asegúrate de hacerlo sólo una vez en tu aplicación)
pygame.init()
pygame.mixer.init()

def mostrar_creditos(surface, volver_al_menu_callback, bgfun=None):
    """
    Muestra la pantalla de créditos con autores, logo y meme usando translate y set_float.
    Recibe:
      - surface: pantalla donde dibujar
      - volver_al_menu_callback: función a ejecutar al pulsar "Regresar"
      - bgfun: función opcional para redibujar el fondo del menú principal
    """
    W, H = surface.get_size()

    # Tema personalizado
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.title_font = pygame_menu.font.FONT_8BIT
    theme.widget_font = pygame_menu.font.FONT_8BIT
    theme.title_font_size = 40
    theme.widget_font_size = 25
    # Hacemos el fondo del theme transparente para que bgfun pueda verse
    theme.background_color = (10, 10, 30)
    theme.title_font_color = (255, 255, 0)
    theme.widget_font_color = (255, 255, 255)
    theme.title_background_color = (50, 20, 100)

    # Carga y reproduce la música de créditos
    music_path = os.path.join("FOLDER_CREDITOS", "credit_music.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        print(f"[ERROR] Archivo de música no encontrado: {music_path}")

    # Crea el menú de créditos
    menu = pygame_menu.Menu(
        height=H,
        width=W,
        title='Equipo de Desarrollo',
        theme=theme
    )

    # Labels de autores
    lbl_title = menu.add.label('Desarrollado Por')
    lbl_title.translate(-280, -180)
    lbl_title.set_float(True)

    lbl_name1 = menu.add.label('Jeizer Oswaldo Guzman Chable')
    lbl_name1.translate(-150, -120)
    lbl_name1.set_float(True)

    lbl_name2 = menu.add.label('Alejandro Gutierrez Nunez')
    lbl_name2.translate(-185, -80)
    lbl_name2.set_float(True)

    # Logo flotante (si existe)
    logo_path = os.path.join('FOLDER_CREDITOS', 'logo.png')
    if os.path.isfile(logo_path):
        logo_w = menu.add.image(logo_path, scale=(0.3, 0.3))
        logo_w.translate(300, -180)
        logo_w.set_float(True)

    # Meme flotante (si existe)
    meme_path = os.path.join('FOLDER_CREDITOS', 'brawl.png')
    if os.path.isfile(meme_path):
        meme_w = menu.add.image(meme_path, scale=(1.2, 1.2))
        meme_w.translate(0, 20)
        meme_w.set_float(True)

    # Botón "Regresar"
    btn_volver = menu.add.button('Regresar', volver_al_menu_callback)
    btn_volver.translate(0, 280)
    btn_volver.set_float(True)

    # Ejecuta el menú; pasa bgfun para que tu fondo siga apareciendo
    menu.mainloop(surface, bgfun=bgfun)

    # Al salir, detiene la música de créditos
    pygame.mixer.music.stop()
