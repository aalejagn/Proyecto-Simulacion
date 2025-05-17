import pygame
import os

class ManejoMusica:
    def __init__(self, music_folder="CANCIONES"):
        """
        Inicializa el gestor de música y sonidos.
        Args:
            music_folder (str): Carpeta donde están las canciones y sonidos.
        """
        self.musica_folder = music_folder
        self.pista_actual = None
        self._asegurar_folder()
        pygame.mixer.init()  # Arranca el sistema de audio de Pygame
        pygame.mixer.set_num_channels(8)  # Soporte para múltiples efectos simultáneos

    def _asegurar_folder(self):
        """Crea la carpeta CANCIONES si no existe."""
        if not os.path.isdir(self.musica_folder):
            os.makedirs(self.musica_folder)

    def cargar_musica(self, nombre_pista):
        """
        Carga una canción desde la carpeta CANCIONES.
        Args:
            nombre_pista (str): Nombre del archivo (ej. 'menu_music.mp3').
        Returns:
            bool: True si se cargó bien, False si hubo error.
        """
        paquete_pista = os.path.join(self.musica_folder, nombre_pista)
        try:
            if not os.path.exists(paquete_pista):
                raise FileNotFoundError(f"No se encontró la canción: {paquete_pista}")
            pygame.mixer.music.load(paquete_pista)
            self.pista_actual = nombre_pista
            return True
        except Exception as e:
            print(f"Error al cargar {nombre_pista}: {e}")
            return False

    def play_game(self, nombre_pista, loops=-1):
        """
        Toca una canción.
        Args:
            nombre_pista (str): Nombre del archivo.
            loops (int): Cuántas veces repetir (-1 para infinito).
        """
        if self.pista_actual != nombre_pista:
            self.stop_music()
            if self.cargar_musica(nombre_pista):
                pygame.mixer.music.play(loops=loops)

    def play_sound(self, sound_name):
        """
        Reproduce un efecto de sonido.
        Args:
            sound_name (str): Nombre del archivo (ej. 'explosion_sound.mp3').
        Returns:
            bool: True si se reprodujo, False si hubo error.
        """
        sound_path = os.path.join(self.musica_folder, sound_name)
        try:
            if not os.path.exists(sound_path):
                raise FileNotFoundError(f"No encontré el sonido: {sound_path}")
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(1.0)  # Volumen máximo
            channel = pygame.mixer.find_channel()  # Busca un canal libre
            if channel is None:
                print(f"No hay canales libres para reproducir {sound_name}")
                return False
            channel.play(sound, loops=0)  # Reproduce una vez
            return True
        except Exception as e:
            print(f"Error al reproducir {sound_name}: {e}")
            return False

    def stop_music(self):
        """Para la música que está sonando."""
        pygame.mixer.music.stop()
        self.pista_actual = None

    def limpieza(self):
        """Limpia los recursos de audio al cerrar el juego."""
        self.stop_music()
        pygame.mixer.quit()