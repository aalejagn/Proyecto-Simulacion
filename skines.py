# skines.py
import os
import pygame
import pygame_menu
from pygame_menu import themes

# Carpeta donde se almacenan las skins
SKIN_FOLDER = "SKIN_FOLDER"
PREVIEW_PREFIX = "modelo"
GAME_PREFIX = "skin"

class SkinManager:
    def __init__(self, width, height):
        """
        width, height: tamaño de la ventana para ajustar el menú
        """
        self.width = width
        self.height = height
        self.current_index = 0
        self.available_skins = []
        self._ensure_folder()
        self._load_skins()

    def _ensure_folder(self):
        if not os.path.isdir(SKIN_FOLDER):
            os.makedirs(SKIN_FOLDER)

    def _load_skins(self):
        """Carga pares preview/game y crea defaults si no hay ninguno"""
        previews = [f for f in os.listdir(SKIN_FOLDER)
                    if f.startswith(PREVIEW_PREFIX) and f.endswith('.png')]
        self.available_skins = []
        for preview in previews:
            num = preview[len(PREVIEW_PREFIX):-4]
            game_file = f"{GAME_PREFIX}{num}.png"
            if num.isdigit() and os.path.isfile(os.path.join(SKIN_FOLDER, game_file)):
                self.available_skins.append((int(num), preview, game_file))
        self.available_skins.sort(key=lambda x: x[0])
        if not self.available_skins:
            self._create_default_skins()
            # tras crear, recargamos
            self._load_skins()

    def _create_default_skins(self):
        """Crea 2 skins por defecto: azul y roja"""
        # Necesita inicializar pygame para crear surfaces
        pygame.init()
        for num, preview_c, game_c in (
            (1, (0, 100, 255), (0, 162, 255)),
            (2, (255, 50, 50), (255, 0, 85)),
        ):
            # Preview (200x200)
            surf = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.rect(surf, preview_c, (20, 20, 160, 160))
            pygame.draw.rect(surf, (255, 255, 0), (60, 60, 80, 80), 4)
            pygame.image.save(surf, os.path.join(
                SKIN_FOLDER, f"{PREVIEW_PREFIX}{num}.png"))
            # Game skin (100x60)
            gs = pygame.Surface((100, 60), pygame.SRCALPHA)
            pygame.draw.rect(gs, game_c, (10, 10, 80, 40))
            pygame.draw.rect(gs, (255, 255, 0), (20, 15, 60, 30), 3)
            pygame.image.save(gs, os.path.join(
                SKIN_FOLDER, f"{GAME_PREFIX}{num}.png"))
        pygame.quit()

    def get_current_game_skin(self) -> pygame.Surface:
        """Devuelve surface de la skin seleccionada (100×60)"""
        if not self.available_skins:
            return pygame.Surface((100, 60), pygame.SRCALPHA)
        _, _, game_file = self.available_skins[self.current_index]
        path = os.path.join(SKIN_FOLDER, game_file)
        return pygame.image.load(path).convert_alpha()

    def get_current_preview(self) -> pygame.Surface:
        """Devuelve surface de la vista previa seleccionada (200×200)"""
        if not self.available_skins:
            return pygame.Surface((200, 200), pygame.SRCALPHA)
        _, preview_file, _ = self.available_skins[self.current_index]
        path = os.path.join(SKIN_FOLDER, preview_file)
        return pygame.image.load(path).convert_alpha()

    def next(self):
        """Avanza a la siguiente skin"""
        if self.available_skins:
            self.current_index = (self.current_index + 1) % len(self.available_skins)

    def prev(self):
        """Retrocede a la skin anterior"""
        if self.available_skins:
            self.current_index = (self.current_index - 1) % len(self.available_skins)
            
            

    def create_skin_selection_menu(self, surface, on_return, on_select=None):
        """
        Construye y devuelve un pygame_menu.Menu para elegir skins.
        on_return: función a llamar al pulsar 'Regresar'.
        """
        # Tema retro neón
        theme = themes.THEME_DARK.copy()
        theme.title_font = pygame_menu.font.FONT_8BIT
        theme.title_font_size = 40
        theme.title_font_color = (255, 255, 0)
        theme.widget_font = pygame_menu.font.FONT_8BIT
        theme.widget_font_size = 24
        theme.background_color = (0, 0, 30)
        from pygame_menu.widgets import HighlightSelection
        theme.widget_selection_effect = HighlightSelection(
            border_width=2,
            margin_x=10,
            margin_y=5
        )
        theme.widget_selection_color = (255, 255, 0, 100)

        menu = pygame_menu.Menu(
            title='Seleccionar Skin',
            width=self.width,
            height=self.height,
            theme=theme,
            onclose=on_return
        )
        # Flechas y vista previa
        menu.add.button('◀', lambda: self._navigate(menu, -1))
        menu.add.surface(pygame.transform.scale(self.get_current_preview(), (250, 250)))
        menu.add.button('▶', lambda: self._navigate(menu, +1))
        # Estado
        menu.add.label(lambda: f"Skin {self.current_index+1}/{len(self.available_skins)}", font_size=20)
        # Acciones
        # — Seleccionar: ejecuta callback, pero NO hace BACK/EXIT
        if on_select:
            menu.add.button('Seleccionar', on_select)
        else:
            # placeholder, no hace nada
            menu.add.button('Seleccionar', lambda: None)
        # — Regresar: cierra el submenú y vuelve al principal
        menu.add.button('Regresar', on_return)
        return menu

    def _navigate(self, menu, direction):
        """Helper para actualizar preview + label en el menú"""
        if direction > 0:
            self.next()
        else:
            self.prev()
        # Actualiza preview
        surf_preview = pygame.transform.scale(self.get_current_preview(), (250, 250))
        # widgets: [0]=◀, [1]=surface, [2]=▶, [3]=label, [4]=Seleccionar, [5]=Regresar
        menu.get_widgets()[1].set_surface(surf_preview)
        menu.get_widgets()[3].set_title(f"Skin {self.current_index+1}/{len(self.available_skins)}")
        menu.force_surface_update()
