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
        """Crea carpetas con verificación de permisos"""
        try:
            if not os.path.isdir(STORE_FOLDER):
                os.makedirs(STORE_FOLDER, exist_ok=True)
                print(f"Carpeta de tienda creada: {STORE_FOLDER}")
            
            if not os.path.isdir(SKIN_FOLDER):
                os.makedirs(SKIN_FOLDER, exist_ok=True)
                print(f"Carpeta de skins creada: {SKIN_FOLDER}")
                
            # Verificar permisos de escritura
            test_file = os.path.join(STORE_FOLDER, 'test_permission.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
        except Exception as e:
            print(f"ERROR configurando carpetas: {e}")
            raise

    def _load_store_data(self):
        """Carga datos de la tienda con validación robusta"""
        import json
        default_skins = [
            (1, "skin_store1.png", "skin_store1.png", 0, True),
            (2, "skin_store2.png", "skin_store2.png", 0, True),
            (3, "skin_store3.png", "skin_store3.png", 500, False),
            (4, "skin_store4.png", "skin_store4.png", 500, False),
            (5, "skin_store5.png", "skin_store5.png", 500, False)
        ]

        try:
            if os.path.exists(STORE_DATA_FILE):
                print(f"Intentando cargar datos de tienda desde: {STORE_DATA_FILE}")
                
                # Leer el archivo primero como texto para validar
                with open(STORE_DATA_FILE, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                    print("Contenido crudo del archivo:", raw_content[:100])  # Mostrar solo parte para debug
                    
                    # Verificar si contiene texto ruso/corrupto
                    if "Какой" in raw_content or "этаж" in raw_content:
                        raise ValueError("Archivo corrupto - Contiene texto en ruso")
                    
                    data = json.loads(raw_content)
                    
                    # Validar estructura básica
                    if not isinstance(data, dict):
                        raise ValueError("El archivo JSON no contiene un objeto válido")
                    
                    # Validar puntos
                    points = data.get('points', 0)
                    if not isinstance(points, (int, float)):
                        raise ValueError("Los puntos deben ser numéricos")
                    
                    # Validar skins
                    skins = data.get('skins', [])
                    if not isinstance(skins, list):
                        raise ValueError("Las skins deben estar en una lista")
                    
                    # Validar cada skin
                    validated_skins = []
                    for skin in skins:
                        if (isinstance(skin, list) and len(skin)) == 5:
                            validated_skins.append(skin)
                        else:
                            print(f"Skin inválida ignorada: {skin}")
                    
                    self.points = points
                    self.available_skins = validated_skins or default_skins
            else:
                print("Creando datos de tienda por defecto")
                self.available_skins = default_skins
                self.points = 0
                
        except Exception as e:
            print(f"ERROR cargando datos de tienda: {e}")
            print("Usando datos por defecto")
            self.available_skins = default_skins
            self.points = 0
        
        # Forzar guardado para reparar archivo corrupto si es necesario
        self.save_store_data()
        self.skin_manager._load_skins()


    def save_store_data(self):
        """Guarda los datos de forma segura"""
        import json
        import tempfile
        
        data = {
            'points': self.points,
            'skins': self.available_skins
        }
        
        try:
            # Guardar primero en archivo temporal
            temp_path = os.path.join(STORE_FOLDER, 'temp_store_data.json')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            # Verificar que el archivo temporal es válido
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)  # Validar que se puede leer
            
            # Reemplazar el archivo original
            if os.path.exists(STORE_DATA_FILE):
                os.remove(STORE_DATA_FILE)
            os.rename(temp_path, STORE_DATA_FILE)
            
        except Exception as e:
            print(f"ERROR crítico guardando datos: {e}")
            # Intentar guardar en archivo alternativo
            backup_path = os.path.join(STORE_FOLDER, 'backup_store_data.json')
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                print(f"Datos guardados en archivo de respaldo: {backup_path}")
            except Exception as backup_e:
                print(f"ERROR en respaldo: {backup_e}")

    def check_data_integrity(self):
        """Verifica que todos los datos sean consistentes"""
        valid = True
        for num, preview, game, cost, unlocked in self.available_skins:
            if not os.path.exists(os.path.join(SKIN_FOLDER, preview)):
                print(f"ADVERTENCIA: Vista previa faltante para skin {num}")
                valid = False
            if not os.path.exists(os.path.join(SKIN_FOLDER, game)):
                print(f"ADVERTENCIA: Imagen de juego faltante para skin {num}")
                valid = False
        return valid

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