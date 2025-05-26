import pygame
import os

class ManejoMusica:
    def __init__(self):
        pygame.mixer.init()
        self.current_music = None
        self.sounds = {}

    def play_game(self, music_file):
        """Play background music."""
        try:
            if self.current_music != music_file:
                pygame.mixer.music.stop()
                music_path = os.path.join('CANCIONES', music_file)  # Adjust path as needed
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.current_music = music_file
        except Exception as e:
            print(f"Error playing music {music_file}: {e}")

    def play_sound(self, sound_file, loop=False):
        """Play a sound effect, with optional looping."""
        try:
            if sound_file not in self.sounds:
                sound_path = os.path.join('CANCIONES', sound_file)  # Adjust path as needed
                self.sounds[sound_file] = pygame.mixer.Sound(sound_path)
            sound = self.sounds[sound_file]
            if loop:
                sound.play(loops=-1)  # Loop indefinitely
            else:
                sound.play()
        except Exception as e:
            print(f"Error playing sound {sound_file}: {e}")

    def stop_sound(self, sound_file):
        """Stop a specific sound effect."""
        try:
            if sound_file in self.sounds:
                self.sounds[sound_file].stop()
        except Exception as e:
            print(f"Error stopping sound {sound_file}: {e}")

    def limpieza(self):
        """Clean up music and sounds."""
        pygame.mixer.music.stop()
        for sound in self.sounds.values():
            sound.stop()
        self.sounds.clear()
        self.current_music = None