# tienda.py
# Gestiona la tienda del juego donde los jugadores compran skins con puntos acumulados.
import os
import pygame
import pygame_menu
from pygame_menu import themes
from funciones_botones import create_buy_button, create_return_button

# Carpeta para datos de la tienda y skins
STORE_FOLDER = "STORE_FOLDER"
SKIN_FOLDER = "SKIN_STORE"
STORE_DATA_FILE = os.path.join(STORE_FOLDER, "store_data.json")

class StoreManager:
    def __init__(self, width, height, skin_manager):
        """
        Inicializa el gestor de la tienda.
        Argumentos:
            width, height: Dimensiones de la ventana para el menú.
            skin_manager: Instancia de SkinManager para acceder y desbloquear skins.
        """
        self.width = width
        self.height = height
        self.skin_manager = skin_manager
        self.points = 0
        self.available_skins = []
        self._ensure_folder()
        self._load_store_data()

    def _ensure_folder(self):
        """Crea la carpeta de la tienda si no existe."""
        # TODO: Crear carpetas STORE_FOLDER y SKIN_STORE si no existen
        if not os.path.isdir(STORE_FOLDER):
            os.makedirs(STORE_FOLDER)
        if not os.path.isdir(SKIN_FOLDER):
            os.makedirs(SKIN_FOLDER)

    def _load_store_data(self):
        """
        Carga datos de la tienda desde JSON o inicializa con skins predeterminadas.
        """
        import json
        # TODO: Definir las skins por defecto usando skin_store*.png
        default_skins = [
            (1, "skin_store1.png", "skin_store1.png", 0, True),
            (2, "skin_store2.png", "skin_store2.png", 0, True),
            (3, "skin_store3.png", "skin_store3.png", 500, False),
        ]

        # TODO: Cargar datos desde store_data.json si existe
        try:
            if os.path.exists(STORE_DATA_FILE):
                with open(STORE_DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.points = data.get('points', 0)
                    self.available_skins = data.get('skins', default_skins)
            else:
                self.available_skins = default_skins
                self.save_store_data()
        except Exception as e:
            # TODO: Usar skins por defecto si falla la carga del JSON
            print(f"Error cargando store_data.json: {e}")
            self.available_skins = default_skins
            self.save_store_data()

        # TODO: Notificar a SkinManager para que actualice sus skins desbloqueadas
        self.skin_manager._load_skins()

    def save_store_data(self):
        """Guarda los datos de la tienda en JSON."""
        import json
        # TODO: Guardar puntos y estado de las skins en store_data.json
        data = {
            'points': self.points,
            'skins': self.available_skins
        }
        try:
            with open(STORE_DATA_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            # TODO: Informar si falla el guardado del JSON
            print(f"Error guardando store_data.json: {e}")

    def add_points(self, points):
        """Añade puntos al total del jugador."""
        # TODO: Sumar puntos y guardar el nuevo total
        self.points += points
        self.save_store_data()

    def purchase_skin(self, skin_num):
        """Intenta comprar una skin por su número."""
        # TODO: Buscar la skin por número y verificar si se puede comprar
        for i, (num, preview, game, cost, unlocked) in enumerate(self.available_skins):
            if num == skin_num and not unlocked and self.points >= cost:
                # TODO: Marcar la skin como desbloqueada y restar puntos
                self.available_skins[i] = (num, preview, game, cost, True)
                self.points -= cost
                self.save_store_data()
                # TODO: Actualizar SkinManager para incluir la nueva skin
                self.skin_manager._load_skins()
                return True
        # TODO: Retornar False si no se pudo comprar
        return False

    def create_store_menu(self, surface, on_return):
        """Crea el menú de la tienda con skins en disposición horizontal."""
        # TODO: Configurar el tema del menú con estilo retro
        theme = themes.THEME_DARK.copy()
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

        # TODO: Crear el menú de la tienda
        menu = pygame_menu.Menu(
            title='Tienda',
            width=self.width,
            height=self.height,
            theme=theme,
            onclose=on_return
        )

        # TODO: Mostrar los puntos actuales del jugador
        menu.add.label(f"Puntos: {self.points}", font_size=20)
        menu.add.vertical_margin(20)

        # TODO: Crear un frame horizontal para alinear las skins
        skin_frame = menu.add.frame_h(
            width=self.width - 200,  # 800px, disponible ~734px
            height=300,
            frame_id='skin_frame',
            align=pygame_menu.locals.ALIGN_CENTER
        )
        skin_frame._relax = True  # TODO: Relajar restricciones de tamaño para evitar excepciones
        skin_frame.pack(menu.add.horizontal_margin(10), align=pygame_menu.locals.ALIGN_LEFT)

        # TODO: Iterar sobre cada skin para crear su sección
# En create_store_menu de tienda.py
        for num, preview_file, game_file, cost, unlocked in self.available_skins:
            item_frame = skin_frame.pack(
                menu.add.frame_v(width=200, height=280, frame_id=f'skin_{num}_frame'),
                align=pygame_menu.locals.ALIGN_CENTER
            )
            # Vista previa
            preview_path = os.path.join(SKIN_FOLDER, preview_file)
            try:
                if not os.path.exists(preview_path):
                    raise FileNotFoundError(f"No file '{preview_path}'")
                preview_surf = pygame.image.load(preview_path).convert_alpha()
                scaled_preview = pygame.transform.scale(preview_surf, (100, 100))
                item_frame.pack(menu.add.surface(scaled_preview), align=pygame_menu.locals.ALIGN_CENTER)
            except Exception as e:
                print(f"Error cargando vista previa de skin {num}: {e}")
                fallback = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.rect(fallback, (100, 100, 100), (0, 0, 100, 100))
                item_frame.pack(menu.add.surface(fallback), align=pygame_menu.locals.ALIGN_CENTER)
            # Estado
            status = "Desbloqueado" if unlocked else f"Costo: {cost} puntos"
            label_widget = menu.add.label(f"Skin {num} - {status}", font_size=14)
            label_widget.set_max_width(180)
            item_frame.pack(label_widget, align=pygame_menu.locals.ALIGN_CENTER)
            # Botón Comprar
            if not unlocked:
                buy_button = menu.add.button(
                    'Comprar',
                    create_buy_button(self, num, menu),
                    font_size=16
                )
                buy_button.set_background_color((255, 165, 0))
                item_frame.pack(buy_button, align=pygame_menu.locals.ALIGN_CENTER)

            # TODO: Agregar margen entre ítems para mejor separación
            skin_frame.pack(menu.add.horizontal_margin(10), align=pygame_menu.locals.ALIGN_LEFT)

        # TODO: Agregar botón Regresar para volver al menú principal
        menu.add.button('Regresar', create_return_button(menu))
        return menu