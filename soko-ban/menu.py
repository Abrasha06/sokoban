import pygame

class Boton:
    def __init__(self, texto, ancho, alto, color_normal, color_resaltado):
        
        if not pygame.font.get_init():
            pygame.font.init()
        
        self.texto = texto
        self.ancho = ancho
        self.alto = alto
        
        
        self.rect = pygame.Rect(0, 0, ancho, alto)
        
        self.color_normal = color_normal
        self.color_resaltado = color_resaltado
        
        
        self.fuente = pygame.font.SysFont("Arial", 32, bold=True)

    def dibujar(self, superficie, posicion_x, posicion_y):
        
        self.rect.topleft = (posicion_x, posicion_y)
        
        posicion_mouse = pygame.mouse.get_pos()
        
        
        esta_encima = self.rect.collidepoint(posicion_mouse)
        color_actual = self.color_resaltado if esta_encima else self.color_normal
        
        
        pygame.draw.rect(superficie, color_actual, self.rect, border_radius=8)
        
        pygame.draw.rect(superficie, (255, 255, 255), self.rect, 2, border_radius=8)
        
        
        imagen_texto = self.fuente.render(self.texto, True, (255, 255, 255))
        rectangulo_texto = imagen_texto.get_rect(center=self.rect.center)
        
        superficie.blit(imagen_texto, rectangulo_texto)

    def fue_presionado(self, evento):
        
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
        
            if self.rect.collidepoint(evento.pos):
                return True
        return False


class InterfazMenu:
    def __init__(self):
        self.submenu = "principal"
        
        
        self.boton_jugar = Boton("INICIAR JUEGO", 350, 70, (40, 80, 160), (60, 100, 200))
        self.boton_ayuda = Boton("CÓMO JUGAR", 350, 70, (40, 80, 160), (60, 100, 200))
        self.boton_salir = Boton("SALIR", 350, 70, (160, 40, 40), (200, 60, 60))
        
        self.boton_facil = Boton("FÁCIL", 300, 65, (40, 140, 40), (60, 180, 60))
        self.boton_medio = Boton("MEDIO", 300, 65, (140, 140, 40), (180, 180, 60))
        self.boton_dificil = Boton("DIFÍCIL", 300, 65, (140, 40, 40), (180, 60, 60))
        self.boton_contrareloj = Boton("CONTRARRELOJ", 300, 65, (120, 60, 160), (160, 80, 200))
        
        self.boton_volver = Boton("VOLVER", 150, 50, (80, 80, 80), (120, 120, 120))



