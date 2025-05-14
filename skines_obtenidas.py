# skines_obtenidas.py
import os
import pygame
import pygame_menu
from pygame_menu import themes

# Carpeta donde se almacenan las skins
SKIN_FOLDER = "SKIN_STORE"
STORE_FOLDER = "STORE_FOLDER"
STORE_DATA_FILE = os.path.join(STORE_FOLDER, "store_data.json")

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
        if not os.path.isdir(STORE_FOLDER):
            os.makedirs(STORE_FOLDER)

    def _load_skins(self):
        """Carga skins desbloqueadas desde store_data.json"""
        import json
        self.available_skins = []
        if os.path.exists(STORE_DATA_FILE):
            with open(STORE_DATA_FILE, 'r') as f:
                data = json.load(f)
                for num, preview, game, cost, unlocked in data.get('skins', []):
                    if unlocked:
                        self.available_skins.append((num, preview, game))
        self.available_skins.sort(key=lambda x: x[0])
        if not self.available_skins:
            # Fallback: al menos una skin por defecto
            self.available_skins = [(1, "modelo1.png", "skin1.png")]
        if self.current_index >= len(self.available_skins):
            self.current_index = 0

    def get_current_game_skin(self) -> pygame.Surface:
        """Devuelve surface de la skin seleccionada (100×60)"""
        if not self.available_skins:
            return pygame.Surface((100, 60), pygame.SRCALPHA)
        _, _, game_file = self.available_skins[self.current_index]
        path = os.path.join(SKIN_FOLDER, game_file)
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error cargando skin {game_file}: {e}")
            return pygame.Surface((100, 60), pygame.SRCALPHA)

    def get_current_preview(self) -> pygame.Surface:
        """Devuelve surface de la vista previa seleccionada (200×200)"""
        if not self.available_skins:
            return pygame.Surface((200, 200), pygame.SRCALPHA)
        _, preview_file, _ = self.available_skins[self.current_index]
        path = os.path.join(SKIN_FOLDER, preview_file)
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error cargando preview {preview_file}: {e}")
            return pygame.Surface((200, 200), pygame.SRCALPHA)

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
        theme = themes.THEME_DARK.copy()
        theme.title_font = pygame_menu.font.FONT_8BIT
        theme.title_font_size = 40
        theme.title_font_color = (255, 255, 0)
        theme.widget_font = pygame_menu.font.FONT_8BIT
        theme.widget_font_size = 24
        theme.background_color = (0, 0, 30)
        theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
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
        if on_select:
            menu.add.button('Seleccionar', on_select)
        else:
            menu.add.button('Seleccionar', lambda: None)
        menu.add.button('Regresar', on_return)
        return menu

    def _navigate(self, menu, direction):
        """Helper para actualizar preview + label en el menú"""
        if direction > 0:
            self.next()
        else:
            self.prev()
        surf_preview = pygame.transform.scale(self.get_current_preview(), (250, 250))
        menu.get_widgets()[1].set_surface(surf_preview)
        menu.get_widgets()[3].set_title(f"Skin {self.current_index+1}/{len(self.available_skins)}")
        menu.force_surface_update()