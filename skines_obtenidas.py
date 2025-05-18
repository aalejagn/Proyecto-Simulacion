import os
import pygame
import pygame_menu
from pygame_menu import themes

# Carpetas
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
        self.current_index = 0  # Skin para jugador 1
        self.current_index2 = 0  # Skin para jugador 2
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
        default_skins = [(1, "skin_store1.png", "skin_store1.png")]
        try:
            if os.path.exists(STORE_DATA_FILE):
                with open(STORE_DATA_FILE, 'r') as f:
                    data = json.load(f)
                    for num, preview, game, cost, unlocked in data.get('skins', []):
                        if unlocked:
                            self.available_skins.append((num, preview, game))
            self.available_skins.sort(key=lambda x: x[0])
            if not self.available_skins:
                self.available_skins = default_skins
        except Exception as e:
            print(f"Error cargando store_data.json: {e}")
            self.available_skins = default_skins
        if self.current_index >= len(self.available_skins):
            self.current_index = 0
        if self.current_index2 >= len(self.available_skins):
            self.current_index2 = 0

    def get_current_game_skin(self, player=1) -> pygame.Surface:
        """Devuelve surface de la skin seleccionada (100×60)"""
        index = self.current_index if player == 1 else self.current_index2
        if not self.available_skins:
            return pygame.Surface((100, 60), pygame.SRCALPHA)
        _, _, game_file = self.available_skins[index]
        path = os.path.join(SKIN_FOLDER, game_file)
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (100, 60))
        except Exception as e:
            print(f"Error cargando skin {game_file}: {e}")
            return pygame.Surface((100, 60), pygame.SRCALPHA)

    def get_current_preview(self, player=1) -> pygame.Surface:
        """Devuelve surface de la vista previa seleccionada (200×200)"""
        index = self.current_index if player == 1 else self.current_index2
        if not self.available_skins:
            return pygame.Surface((200, 200), pygame.SRCALPHA)
        _, preview_file, _ = self.available_skins[index]
        path = os.path.join(SKIN_FOLDER, preview_file)
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (200, 200))
        except Exception as e:
            print(f"Error cargando preview {preview_file}: {e}")
            return pygame.Surface((200, 200), pygame.SRCALPHA)

    def next(self, player=1):
        """Avanza a la siguiente skin"""
        if self.available_skins:
            if player == 1:
                self.current_index = (self.current_index + 1) % len(self.available_skins)
            else:
                self.current_index2 = (self.current_index2 + 1) % len(self.available_skins)

    def prev(self, player=1):
        """Retrocede a la skin anterior"""
        if self.available_skins:
            if player == 1:
                self.current_index = (self.current_index - 1) % len(self.available_skins)
            else:
                self.current_index2 = (self.current_index2 - 1) % len(self.available_skins)

    def create_skin_selection_menu(self, surface, on_return, on_select=None):
        """
        Construye y devuelve un pygame_menu.Menu para elegir skins para ambos jugadores.
        on_return: función a llamar al pulsar 'Regresar'.
        on_select: función a llamar al seleccionar una skin.
        """
        theme = pygame_menu.themes.THEME_DARK.copy()
        theme.title_font = pygame_menu.font.FONT_8BIT
        theme.title_font_size = 40
        theme.title_font_color = (255, 255, 0)
        theme.widget_font = pygame_menu.font.FONT_8BIT
        theme.widget_font_size = 24
        theme.background_color = (0, 0, 30)
        theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
            border_width=2, margin_x=10, margin_y=5
        )
        theme.widget_selection_color = (255, 255, 0, 100)

        menu = pygame_menu.Menu(
            title='Seleccionar Skin',
            width=self.width,
            height=self.height,
            theme=theme,
            onclose=on_return
        )

        # Frame para alinear las secciones de los dos jugadores
        frame = menu.add.frame_h(width=self.width - 100, height=300, frame_id='skin_frame')
        frame._relax = True

        # Sección Jugador 1
        player1_frame = frame.pack(
            menu.add.frame_v(width=300, height=280, frame_id='player1_frame'),
            align=pygame_menu.locals.ALIGN_LEFT
        )
        player1_frame._relax = True  # Allow overflow
        player1_frame.pack(menu.add.label("Jugador 1", font_size=20), align=pygame_menu.locals.ALIGN_CENTER)
        player1_frame.pack(
            menu.add.button('◀', lambda: self._navigate(menu, -1, player=1), font_size=16),
            align=pygame_menu.locals.ALIGN_CENTER
        )
        player1_frame.pack(
            menu.add.surface(pygame.transform.scale(self.get_current_preview(player=1), (150, 150))),  # Reduced size
            align=pygame_menu.locals.ALIGN_CENTER
        )
        player1_frame.pack(
            menu.add.button('▶', lambda: self._navigate(menu, 1, player=1), font_size=16),
            align=pygame_menu.locals.ALIGN_CENTER
        )
        player1_frame.pack(
            menu.add.label(lambda: f"Skin {self.current_index+1}/{len(self.available_skins)}", font_size=16),
            align=pygame_menu.locals.ALIGN_CENTER
        )

        # Separador
        frame.pack(menu.add.horizontal_margin(50), align=pygame_menu.locals.ALIGN_LEFT)

        # Sección Jugador 2
        player2_frame = frame.pack(
            menu.add.frame_v(width=300, height=280, frame_id='player2_frame'),
            align=pygame_menu.locals.ALIGN_LEFT
        )
        player2_frame._relax = True  # Allow overflow
        player2_frame.pack(menu.add.label("Jugador 2", font_size=20), align=pygame_menu.locals.ALIGN_CENTER)
        player2_frame.pack(
            menu.add.button('◀', lambda: self._navigate(menu, -1, player=2), font_size=16),
            align=pygame_menu.locals.ALIGN_CENTER
        )
        player2_frame.pack(
            menu.add.surface(pygame.transform.scale(self.get_current_preview(player=2), (150, 150))),  # Reduced size
            align=pygame_menu.locals.ALIGN_CENTER
        )
        player2_frame.pack(
            menu.add.button('▶', lambda: self._navigate(menu, 1, player=2), font_size=16),
            align=pygame_menu.locals.ALIGN_CENTER
        )
        player2_frame.pack(
            menu.add.label(lambda: f"Skin {self.current_index2+1}/{len(self.available_skins)}", font_size=16),
            align=pygame_menu.locals.ALIGN_CENTER
        )

        # Botones de acción
        menu.add.button('Seleccionar', on_select if on_select else lambda: None)
        menu.add.button('Regresar', on_return)
        return menu

    def _navigate(self, menu, direction, player=1):
        """Helper para actualizar preview + label en el menú"""
        if direction > 0:
            self.next(player)
        else:
            self.prev(player)
        index = self.current_index if player == 1 else self.current_index2
        frame_index = 0 if player == 1 else 2  # Índice del frame en frame_h
        preview_widget = menu.get_widget(f'player{player}_frame').get_widgets()[2]  # Surface
        label_widget = menu.get_widget(f'player{player}_frame').get_widgets()[4]  # Label
        surf_preview = pygame.transform.scale(self.get_current_preview(player), (200, 200))
        preview_widget.set_surface(surf_preview)
        label_widget.set_title(f"Skin {index+1}/{len(self.available_skins)}")
        menu.force_surface_update()