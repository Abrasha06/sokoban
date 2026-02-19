import pygame
import sys
from enfocate import GameBase, GameMetadata, COLORS

class MiJuego(GameBase):
    def __init__(self) -> None:
        
        meta = GameMetadata(
            title="Sokoban",
            description="El rompecabezas de lógica, estrategia y ordenar sin quedar atrapado.",
            authors=["Abraham Sosa", "Luis Millán", "Joyce Valerio", "Edgardo Quiñones."],
            group_number=6
        )
        
        
        super().__init__(meta)
        
        
        
        self.TAMANO_CELDA = 60
        

        self.puntuacion = 0

        self.victoria = False

    def verificar_victoria(self):
        #Revisa si todas las metas tienen una caja encima.
        for (f, c) in self.posiciones_metas:
            if self.mapa[f][c] != "B":
                return
        self.victoria = True

    def on_start(self):
        """Carga de recursos dinámicos (assets)."""
        
        # Mapa de Prueba
        # W = Muro, B = Caja, P = Jugador, G = Meta, " " = espacio vacio
        self.mapa = [

            ["W", "W", "W", "W", "W", "W", "W", "W"],
            ["W", "P", " ", " ", " ", " ", " ", "W"],
            ["W", " ", " ", " ", " ", " ", " ", "W"],
            ["W", " ", " ", " ", " ", " ", " ", "W"], 
            ["W", " ", " ", " ", " ", " ", " ", "W"],
            ["W", " ", "B", "B", "B", "G", " ", "W"], 
            ["W", " ", " ", " ", " ", " ", " ", "W"],
            ["W", "W", "W", "W", "W", "W", "W", "W"]
        ]

        for f in range(len(self.mapa)):
            for c in range(len(self.mapa[f])):
                if self.mapa[f][c] == "P":
                    self.pos_p = [f, c] 

        # Guardar coordenadas de las metas
        self.posiciones_metas = []
        for f in range(len(self.mapa)):
            for c in range(len(self.mapa[f])):
                if self.mapa[f][c] == "G":
                    self.posiciones_metas.append((f, c))
                if self.mapa[f][c] == "P":
                    self.pos_p = [f, c]    
    



    def update(self, dt: float):

        """Actualización de lógica física y estados (dt = delta time)."""
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                
                # 'self.is_running = False' tarda en cerrar el juego asi que uso esta otra forma
                pygame.quit() 
                sys.exit()    
                

            if event.type == pygame.KEYDOWN:
                    dif_filas, dif_col = 0, 0 
                    
                    #controles (WASD o flechas)
                    # Arriba
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        dif_filas = -1
                    # Abajo
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        dif_filas = 1
                    # Izquierda
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        dif_col = -1
                    # Derecha
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        dif_col = 1
                    
                    
                    nueva_fila = self.pos_p[0] + dif_filas
                    nueva_col = self.pos_p[1] + dif_col
                    
                    # ver que no es un muro 
                    if self.mapa[nueva_fila][nueva_col] != "W" and self.mapa[nueva_fila][nueva_col] != "B":
                        
                        f_ant, c_ant = self.pos_p[0], self.pos_p[1]
                        self.mapa[f_ant][c_ant] = "G" if (f_ant, c_ant) in self.posiciones_metas else " "
                    
                        self.pos_p = [nueva_fila, nueva_col]
                        self.mapa[nueva_fila][nueva_col] = "P"

                    elif self.mapa[nueva_fila][nueva_col] == "B":
                    # Revisar que hay delante de la caja
                     del_f = nueva_fila + dif_filas
                     del_c = nueva_col + dif_col

                    #mover la caja
                     if self.mapa[del_f][del_c] in [" ", "G"]:
                        self.mapa[del_f][del_c] = "B"
                        self.mapa[nueva_fila][nueva_col] = "P"
                        self.mapa[self.pos_p[0]][self.pos_p[1]] = " "
                        self.pos_p = [nueva_fila, nueva_col]


        self.verificar_victoria()
        

    def draw(self):
        """Renderizado en la superficie inyectada por el motor."""
        self.surface.fill(COLORS["carbon_oscuro"])


        for (f_meta, c_meta) in self.posiciones_metas:
            x = c_meta * self.TAMANO_CELDA
            y = f_meta * self.TAMANO_CELDA
            rect = (x, y, self.TAMANO_CELDA, self.TAMANO_CELDA)
            pygame.draw.rect(self.surface, (255, 255, 100), rect, 3)

        for fila in range(len(self.mapa)):
            for columna in range(len(self.mapa[fila])):
                
                
                x = columna * self.TAMANO_CELDA
                y = fila * self.TAMANO_CELDA
                rect = (x, y, self.TAMANO_CELDA, self.TAMANO_CELDA)
                
                contenido = self.mapa[fila][columna]
                
                #dibujar elementos
                if contenido == "W": # Muro
                    pygame.draw.rect(self.surface, (100, 100, 100), rect) 
                
                elif contenido == "B": # Caja
                    #Si está en la meta cambia el color
                    color_caja = (50, 200, 50) if (fila, columna) in self.posiciones_metas else (200, 150, 50)
                    pygame.draw.rect(self.surface, color_caja, rect) 
                
                elif contenido == "P": #Jugador
                    
                    centro = (x + self.TAMANO_CELDA // 2, y + self.TAMANO_CELDA // 2)
                    pygame.draw.circle(self.surface, (50, 150, 255), centro, 25)
                
                ''' elif contenido == "G": #Meta
                    pygame.draw.rect(self.surface, (255, 255, 100), rect, 3) 
                    '''
                # Rejilla
                pygame.draw.rect(self.surface, (45, 45, 45), rect, 1)

        #texto victoria
        if self.victoria:
            fuente = pygame.font.SysFont("Arial", 48, bold=True)
            texto = fuente.render("¡NIVEL COMPLETADO!", True, (255, 255, 255))
            fondo_texto = texto.get_rect(center=(self.surface.get_width()//2, self.surface.get_height()//2))
            #fondo
            pygame.draw.rect(self.surface, (0, 0, 0), fondo_texto.inflate(20, 20))
            self.surface.blit(texto, fondo_texto)

if __name__ == "__main__":
    # Ejecuta el mini-motor integrado bajo los estándares del Core
    MiJuego().run_preview()
    pygame.quit()