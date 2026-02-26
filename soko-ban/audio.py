import pygame
import os

class GestorAudio:
    def __init__(self):
       
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            
        self.ruta_base = os.path.dirname(os.path.abspath(__file__))
        self.ruta_audio = os.path.join(self.ruta_base, "assets", "audio")
        
        self.sonidos = {}
        self.cargar_recursos()

    def cargar_recursos(self):
        
        try:
            self.sonidos["victoria"] = pygame.mixer.Sound(os.path.join(self.ruta_audio, "victoria.wav"))
            
            self.sonidos["victoria"].set_volume(1.0)
        except:
            print("Aviso: No se encontró el archivo victoria.wav")

    def reproducir_musica(self, nombre_archivo, volumen=0.3):
        
        ruta = os.path.join(self.ruta_audio, nombre_archivo)
        if os.path.exists(ruta):
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(volumen)
            pygame.mixer.music.play(-1) 
        else:
            print(f"Error: No se encontró la música {nombre_archivo}")

    def detener_musica(self):
        pygame.mixer.music.stop()

    def reproducir_sfx(self, nombre):
        
        if nombre in self.sonidos:
            self.sonidos[nombre].play()