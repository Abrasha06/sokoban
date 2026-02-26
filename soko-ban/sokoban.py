import sys
import os

from enfocate import GameBase, GameMetadata, COLORS

import pygame
import random

from niveles import MAPAS
from menu import InterfazMenu
from audio import GestorAudio 


class Tablero:
    def __init__(self, mapa_datos, imagenes):
        self.muros = [(fila, columna) 
                      for fila, datos_fila in enumerate(mapa_datos) 
                      for columna, valor in enumerate(datos_fila) if valor == "W"]
        
        self.metas = [(fila, columna) 
                      for fila, datos_fila in enumerate(mapa_datos) 
                      for columna, valor in enumerate(datos_fila) if valor == "G"]
        
        self.total_filas = len(mapa_datos)
        self.total_columnas = len(mapa_datos[0])

        self.img_suelo = imagenes['suelo']
        self.img_muro = imagenes['muro']
        self.img_meta = imagenes['meta']
        

    def es_muro(self, fila, columna): 
        return (fila, columna) in self.muros

    def dibujar(self, superficie, tamano_celda, margen_x, margen_y):
        # suelo 
        for fila in range(self.total_filas):
            for columna in range(self.total_columnas):
                x = columna * tamano_celda + margen_x
                y = fila * tamano_celda + margen_y
                superficie.blit(self.img_suelo, (x, y))

        # metas
        for (fila, columna) in self.metas:
            x = columna * tamano_celda + margen_x
            y = fila * tamano_celda + margen_y
            superficie.blit(self.img_meta, (x, y))

        # muros
        for (fila, columna) in self.muros:
            x = columna * tamano_celda + margen_x
            y = fila * tamano_celda + margen_y
            superficie.blit(self.img_muro, (x, y))

class Caja:
    def __init__(self, fila, columna, imagenes): 
        self.fila = fila
        self.columna = columna
        self.img_normal = imagenes['caja']
        self.img_meta = imagenes['caja_meta']

    def dibujar(self, superficie, tamano_celda, tablero, margen_x, margen_y):
        x = self.columna * tamano_celda + margen_x
        y = self.fila * tamano_celda + margen_y
        
        imagen_a_usar = self.img_meta if (self.fila, self.columna) in tablero.metas else self.img_normal
        superficie.blit(imagen_a_usar, (x, y))


class Jugador:
    def __init__(self, fila, columna, sprites): 
        self.fila = fila
        self.columna = columna
        self.sprites = sprites
        self.direccion_actual = "idle"

    def dibujar(self, superficie, tamano_celda, margen_x, margen_y):
        x = self.columna * tamano_celda + margen_x
        y = self.fila * tamano_celda + margen_y
        
        imagen = self.sprites.get(self.direccion_actual, self.sprites["idle"])
        superficie.blit(imagen, (x, y))


class MiJuego(GameBase):
    def __init__(self) -> None:
        pygame.init()
        meta = GameMetadata(
            title="Sokoban",
            description="El rompecabezas de lógica, estrategia y ordenar sin quedar atrapado.",
            authors=["Abraham Sosa", "Luis Millán", "Joyce Valerio", "Edgardo Quiñones."],
            group_number=6
        )
        super().__init__(meta)
        
        self.TAMANO_CELDA = 60
        self.estado_actual = "MENU"
        self.interfaz_menu = InterfazMenu()
        
        

        self.modo_de_juego = "normal"
        self.dificultad_actual = "facil"
        self.indice_nivel = 0
        self.historial_movimientos = []
        self.nivel_completado = False
        
        
        self.tiempo_restante = 0.0
        self.niveles_superados_contrareloj = 0
        self.tiempo_agotado = False
        self.audio = GestorAudio()


    def cargar_recursos_graficos(self):
        
        ruta_base = os.path.dirname(__file__)

        def preparar(archivo):
            
            ruta_completa = os.path.join(ruta_base, "assets", "sprites", archivo)
            
            
            if not os.path.exists(ruta_completa):
                print(f"Error crítico: No se encontró el archivo {archivo} en {ruta_completa}")
                pygame.quit()
                sys.exit()

            img = pygame.image.load(ruta_completa).convert_alpha()
            return pygame.transform.scale(img, (self.TAMANO_CELDA, self.TAMANO_CELDA))

        
        img_caja_base = preparar("caja.png")
        
        
        img_caja_meta = img_caja_base.copy()
        filtro_verde = pygame.Surface((self.TAMANO_CELDA, self.TAMANO_CELDA), pygame.SRCALPHA)
        filtro_verde.fill((100, 255, 100, 180)) 
        img_caja_meta.blit(filtro_verde, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.imagenes = {
            'suelo': preparar("suelo.png"),
            'muro': preparar("muro.png"),
            'meta': preparar("meta.png"),
            'caja': img_caja_base,
            'caja_meta': img_caja_meta
        }

        sprite_der = preparar("jugador_der.png")
        sprite_izq = pygame.transform.flip(sprite_der, True, False)

        self.sprites_jugador = {
            'idle': preparar("jugador_idle.png"),
            'arriba': preparar("jugador_arriba.png"),
            'abajo': preparar("jugador_abajo.png"),
            'derecha': sprite_der,
            'izquierda': sprite_izq
        }

        self.fuente_titulos = pygame.font.SysFont("Arial", 72, bold=True) 
        self.fuente_textos = pygame.font.SysFont("Arial", 22)
        self.fuente_reloj = pygame.font.SysFont("Arial", 28, bold=True)
        self.fuente_fin = pygame.font.SysFont("Arial", 36, bold=True)
    

    def on_start(self):

        pygame.key.set_repeat(200, 100)
        self.cargar_recursos_graficos()
        self.audio.reproducir_musica("MusicaFondo.ogg")

    def iniciar_modo_normal(self, dificultad):
        self.modo_de_juego = "normal"
        self.cargar_nivel(dificultad, 0)

    def iniciar_modo_contrareloj(self):
        self.modo_de_juego = "contrareloj"
        self.tiempo_restante = 180.0 
        self.niveles_superados_contrareloj = 0
        self.tiempo_agotado = False
        self.cargar_nivel_aleatorio()

    def cargar_nivel_aleatorio(self):
        opciones_dificultad = list(MAPAS.keys())
        dificultad_al_azar = random.choice(opciones_dificultad)
        indice_al_azar = random.randint(0, len(MAPAS[dificultad_al_azar]) - 1)
        
        self.cargar_nivel(dificultad_al_azar, indice_al_azar)

    def cargar_nivel(self, dificultad, indice):
        if dificultad in MAPAS and indice < len(MAPAS[dificultad]):
            datos_mapa = MAPAS[dificultad][indice]
            
            self.tablero = Tablero(datos_mapa, self.imagenes)
            self.cajas = [Caja(f, c, self.imagenes) for f, fila in enumerate(datos_mapa) 
                          for c, val in enumerate(fila) if val == "B"]
            
            pos_p = [(f, c) for f, fila in enumerate(datos_mapa) for c, val in enumerate(fila) if val == "P"][0]
            self.jugador = Jugador(pos_p[0], pos_p[1], self.sprites_jugador)
            
            self.nivel_completado = False
            self.historial_movimientos = []
            self.dificultad_actual = dificultad
            self.indice_nivel = indice
            self.estado_actual = "JUGANDO"
        else:
            self.estado_actual = "MENU"


    def update(self, dt: float):
        
        if self.estado_actual == "JUGANDO" and self.modo_de_juego == "contrareloj":
            if not self.nivel_completado and not self.tiempo_agotado:
                self.tiempo_restante -= dt
                if self.tiempo_restante <= 0:
                    self.tiempo_restante = 0
                    self.tiempo_agotado = True

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.estado_actual == "MENU":
                self.gestionar_logica_menu(evento)
            else:
                self.gestionar_logica_juego(evento)

    def gestionar_logica_menu(self, evento):
        menu = self.interfaz_menu
        
        if menu.submenu == "principal":
            if menu.boton_jugar.fue_presionado(evento): 
                menu.submenu = "dificultad"
            elif menu.boton_ayuda.fue_presionado(evento): 
                menu.submenu = "instrucciones"
            elif menu.boton_salir.fue_presionado(evento): 
                pygame.quit(); sys.exit()
        
        elif menu.submenu == "dificultad":
            if menu.boton_volver.fue_presionado(evento): 
                menu.submenu = "principal"
            elif menu.boton_facil.fue_presionado(evento): 
                self.iniciar_modo_normal("facil")
            elif menu.boton_medio.fue_presionado(evento): 
                self.iniciar_modo_normal("medio")
            elif menu.boton_dificil.fue_presionado(evento): 
                self.iniciar_modo_normal("dificil")
            elif menu.boton_contrareloj.fue_presionado(evento):
                self.iniciar_modo_contrareloj()
            
        elif menu.submenu == "instrucciones":
            if menu.boton_volver.fue_presionado(evento): 
                menu.submenu = "principal"

    def gestionar_logica_juego(self, evento):
        if evento.type == pygame.KEYDOWN:
            
            if evento.key == pygame.K_ESCAPE: 
                self.estado_actual = "MENU"
            
        
            elif self.tiempo_agotado:
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.estado_actual = "MENU"
                return
            
            elif evento.key == pygame.K_r: 
                self.cargar_nivel(self.dificultad_actual, self.indice_nivel)
            
            elif evento.key == pygame.K_z: 
                self.deshacer_ultimo_movimiento()
            
            elif self.nivel_completado and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                pygame.mixer.music.set_volume(0.5)
                if self.modo_de_juego == "contrareloj":
                    self.niveles_superados_contrareloj += 1
                    self.cargar_nivel_aleatorio()
                else:
                    self.cargar_nivel(self.dificultad_actual, self.indice_nivel + 1)
            
            elif not self.nivel_completado:
                controles = {
                    pygame.K_UP: (-1, 0, "arriba"),    pygame.K_w: (-1, 0, "arriba"),
                    pygame.K_DOWN: (1, 0, "abajo"),   pygame.K_s: (1, 0, "abajo"),
                    pygame.K_LEFT: (0, -1, "izquierda"),  pygame.K_a: (0, -1, "izquierda"),
                    pygame.K_RIGHT: (0, 1, "derecha"),  pygame.K_d: (0, 1, "derecha")
                }
        
                if evento.key in controles:
        
                    paso_fila, paso_columna, nombre_dir = controles[evento.key] 
                
        
                    self.procesar_movimiento(paso_fila, paso_columna, nombre_dir)

    def procesar_movimiento(self, delta_fila, delta_columna, nombre_dir):
        self.jugador.direccion_actual = nombre_dir
        
        estado_previo = {
            'jugador': (self.jugador.fila, self.jugador.columna),
            'cajas': [(caja.fila, caja.columna) for caja in self.cajas]
        }
        
        nueva_f, nueva_c = self.jugador.fila + delta_fila, self.jugador.columna + delta_columna
        
        if self.tablero.es_muro(nueva_f, nueva_c): return
        
        caja = next((c for c in self.cajas if c.fila == nueva_f and c.columna == nueva_c), None)
        
        if caja:
            tras_f, tras_c = nueva_f + delta_fila, nueva_c + delta_columna
            if self.tablero.es_muro(tras_f, tras_c) or any(c.fila == tras_f and c.columna == tras_c for c in self.cajas):
                return
            caja.fila, caja.columna = tras_f, tras_c
        
        self.jugador.fila, self.jugador.columna = nueva_f, nueva_c
        self.historial_movimientos.append(estado_previo)
        self.nivel_completado = all((c.fila, c.columna) in self.tablero.metas for c in self.cajas)
        
        if self.nivel_completado:
            pygame.mixer.music.set_volume(0.2)
            self.audio.reproducir_sfx("victoria") 
            self.nivel_completado = True


    def deshacer_ultimo_movimiento(self):
        if self.historial_movimientos:
            estado_anterior = self.historial_movimientos.pop()
            
            self.jugador.fila, self.jugador.columna = estado_anterior['jugador']
            for i, posicion in enumerate(estado_anterior['cajas']):
                self.cajas[i].fila, self.cajas[i].columna = posicion
                
            self.nivel_completado = False

    def draw(self):

        self.surface.fill((35, 45, 60))
        
        if self.estado_actual == "MENU":
            self.dibujar_interfaz_menu()
        else:
            self.dibujar_escena_juego()


    def dibujar_titulo_decorado(self, texto, x, y):
        
        texto_sombra = self.fuente_titulos.render(texto, True, (20, 20, 30))
        self.surface.blit(texto_sombra, (x + 4, y + 4))
        
        
        texto_contorno = self.fuente_titulos.render(texto, True, (0, 0, 0))
        self.surface.blit(texto_contorno, (x - 2, y))
        self.surface.blit(texto_contorno, (x + 2, y))
        self.surface.blit(texto_contorno, (x, y - 2))
        self.surface.blit(texto_contorno, (x, y + 2))
        
        
        texto_principal = self.fuente_titulos.render(texto, True, (255, 215, 0))
        self.surface.blit(texto_principal, (x, y))

    def dibujar_interfaz_menu(self):
        menu = self.interfaz_menu
        ancho_v, alto_v = self.surface.get_width(), self.surface.get_height()
        centro_x = ancho_v // 2 - 175
        centro_x_dificultad = ancho_v // 2 - 150
        
        if menu.submenu == "principal":
        
            texto = "SOKOBAN MASTER"
            ancho_texto = self.fuente_titulos.size(texto)[0]
            self.dibujar_titulo_decorado(texto, ancho_v // 2 - ancho_texto // 2, 80)
            
            menu.boton_jugar.dibujar(self.surface, centro_x, 200)
            menu.boton_ayuda.dibujar(self.surface, centro_x, 320) # CÓMO JUGAR a Y=260
            menu.boton_salir.dibujar(self.surface, centro_x, 440)

        
            escala = 3
            tamano_grande = self.TAMANO_CELDA * escala
            jugador_der = pygame.transform.scale(self.sprites_jugador['derecha'], (tamano_grande, tamano_grande))
            
            y_alineado = 320 + (70 // 2) - (tamano_grande // 2)
            
        
            separacion = 60
            x_decoracion = centro_x - tamano_grande - separacion
            
            self.surface.blit(jugador_der, (x_decoracion, y_alineado))
            
        elif menu.submenu == "dificultad":
            texto = "SELECCIONA MODO"
            ancho_texto = self.fuente_titulos.size(texto)[0]
            self.dibujar_titulo_decorado(texto, ancho_v // 2 - ancho_texto // 2, 60)
            
            menu.boton_facil.dibujar(self.surface, centro_x_dificultad, 160)
            menu.boton_medio.dibujar(self.surface, centro_x_dificultad, 250)
            menu.boton_dificil.dibujar(self.surface, centro_x_dificultad, 340)
            menu.boton_contrareloj.dibujar(self.surface, centro_x_dificultad, 430)
            
            menu.boton_volver.dibujar(self.surface, 20, alto_v - 90)
            
        elif menu.submenu == "instrucciones":
            texto = "COMO JUGAR"
            ancho_texto = self.fuente_titulos.size(texto)[0]
            self.dibujar_titulo_decorado(texto, ancho_v // 2 - ancho_texto // 2, 80)
            
            lineas = [" ",
                "Empuja las cajas a las metas sin quedar atrapado!",
                "• Flechas / WASD: Moverse", 
                "• Z: Deshacer movimiento", 
                "• R: Reiniciar nivel", 
                "• ESC: Volver al menú",
                "• Contrarreloj: Completa niveles antes de que el tiempo se agote"
            ]
            
            for i, linea in enumerate(lineas):
                color = (255, 230, 150) if i == 0 else (220, 220, 220)
                img_texto = self.fuente_textos.render(linea, True, color)
                self.surface.blit(img_texto, (ancho_v // 2 - img_texto.get_width() // 2, 160 + i * 50))
            
            menu.boton_volver.dibujar(self.surface, 20, alto_v - 90)
    def dibujar_escena_juego(self):
        ancho_mapa = self.tablero.total_columnas * self.TAMANO_CELDA
        alto_mapa = self.tablero.total_filas * self.TAMANO_CELDA
        
        desplazamiento_x = (self.surface.get_width() - ancho_mapa) // 2
        desplazamiento_y = (self.surface.get_height() - alto_mapa) // 2
        
        self.tablero.dibujar(self.surface, self.TAMANO_CELDA, desplazamiento_x, desplazamiento_y)
        
        for caja in self.cajas:
            caja.dibujar(self.surface, self.TAMANO_CELDA, self.tablero, desplazamiento_x, desplazamiento_y)
            
        self.jugador.dibujar(self.surface, self.TAMANO_CELDA, desplazamiento_x, desplazamiento_y)
        
        
        if self.modo_de_juego == "contrareloj":
            
            minutos = int(self.tiempo_restante) // 60
            segundos = int(self.tiempo_restante) % 60
            
            texto_tiempo = self.fuente_reloj.render(f"TIEMPO: {minutos:02d}:{segundos:02d}", True, (255, 100, 100))
            self.surface.blit(texto_tiempo, (self.surface.get_width() // 2 - texto_tiempo.get_width() // 2, 20))
            
            texto_puntaje = self.fuente_reloj.render(f"NIVELES: {self.niveles_superados_contrareloj}", True, (100, 255, 100))
            self.surface.blit(texto_puntaje, (20, 20))
            
        
        if self.tiempo_agotado:
            
            texto_fin = self.fuente_fin.render("¡TIEMPO AGOTADO!", True, (255, 100, 100))
            texto_resumen = pygame.font.SysFont("Arial", 22).render(f"Niveles superados: {self.niveles_superados_contrareloj} (ESPACIO para salir)", True, (200, 200, 200))
            
            rectangulo_fondo = texto_fin.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2 - 20))
            pygame.draw.rect(self.surface, (0, 0, 0), rectangulo_fondo.inflate(60, 100))
            self.surface.blit(texto_fin, rectangulo_fondo)
            self.surface.blit(texto_resumen, (self.surface.get_width() // 2 - texto_resumen.get_width() // 2, self.surface.get_height() // 2 + 20))
            
        elif self.nivel_completado:
            fuente_victoria = pygame.font.SysFont("Arial", 30, bold=True)
            texto_v = fuente_victoria.render("¡NIVEL COMPLETADO!", True, (255, 255, 255))
            rectangulo_texto = texto_v.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
            
            pygame.draw.rect(self.surface, (0, 0, 0), rectangulo_texto.inflate(40, 40))
            self.surface.blit(texto_v, rectangulo_texto)


if __name__ == "__main__":
    MiJuego().run_preview()
    pygame.quit()