import sys
import os
import pygame
import random


from niveles import MAPAS
from enfocate import GameBase, GameMetadata
from audio import GestorAudio
    




class Boton:
    def __init__(self, texto, x, y, ancho, alto, color_normal, color_resaltado):
        self.texto = texto
        self.color_normal = color_normal
        self.color_resaltado = color_resaltado
        self.fuente = pygame.font.SysFont("Arial", 32, bold=True)
        
        self.rect = pygame.Rect(x, y, ancho, alto)

    def dibujar(self, superficie, mouse_pos):
        
        esta_encima = self.rect.collidepoint(mouse_pos)
        color = self.color_resaltado if esta_encima else self.color_normal
        
        pygame.draw.rect(superficie, color, self.rect, border_radius=8)
        pygame.draw.rect(superficie, (255, 255, 255), self.rect, 2, border_radius=8)
        
        txt = self.fuente.render(self.texto, True, (255, 255, 255))
        superficie.blit(txt, txt.get_rect(center=self.rect.center))

    def fue_presionado(self, evento, mouse_pos_convertida):
        
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(mouse_pos_convertida)
        return False


class InterfazMenu:
    def __init__(self, ancho, alto):
        centro_x = ancho // 2
        self.submenu = "principal"
        
        
        self.btn_jugar = Boton("INICIAR JUEGO", centro_x - 175, 200, 350, 70, (40, 80, 160), (60, 100, 200))
        self.btn_ayuda = Boton("CÓMO JUGAR", centro_x - 175, 320, 350, 70, (40, 80, 160), (60, 100, 200))
        self.btn_salir = Boton("SALIR", centro_x - 175, 440, 350, 70, (160, 40, 40), (200, 60, 60))
        
        self.btn_facil = Boton("FÁCIL", centro_x - 150, 160, 300, 65, (40, 140, 40), (60, 180, 60))
        self.btn_medio = Boton("MEDIO", centro_x - 150, 250, 300, 65, (140, 140, 40), (180, 180, 60))
        self.btn_dificil = Boton("DIFÍCIL", centro_x - 150, 340, 300, 65, (140, 40, 40), (180, 60, 60))
        self.btn_reloj = Boton("CONTRARRELOJ", centro_x - 150, 430, 300, 65, (120, 60, 160), (160, 80, 200))
        
        self.btn_volver = Boton("VOLVER", 20, alto - 90, 150, 50, (80, 80, 80), (120, 120, 120))


class Tablero:
    def __init__(self, datos, imgs):
        self.muros = [(f, c) for f, fila in enumerate(datos) for c, v in enumerate(fila) if v == "W"]
        self.metas = [(f, c) for f, fila in enumerate(datos) for c, v in enumerate(fila) if v == "G"]
        self.filas = len(datos)
        self.cols = len(datos[0])
        self.imgs = imgs

    def es_muro(self, f, c): return (f, c) in self.muros

    def dibujar(self, superficie, tamano, offset_x, offset_y):
        for fila in range(self.filas):
            for columna in range(self.cols):
                superficie.blit(self.imgs['suelo'], (columna*tamano+offset_x, fila*tamano+offset_y))
        for fila, columna in self.metas: superficie.blit(self.imgs['meta'], (columna*tamano+offset_x, fila*tamano+offset_y))
        for fila, columna in self.muros: superficie.blit(self.imgs['muro'], (columna*tamano+offset_x, fila*tamano+offset_y))

class Caja:
    def __init__(self, f, c, imgs):
        self.f, self.c = f, c
        self.imgs = imgs
    
    def dibujar(self, sup, tam, tab, ox, oy):
        img = self.imgs['caja_meta'] if (self.f, self.c) in tab.metas else self.imgs['caja']
        sup.blit(img, (self.c*tam+ox, self.f*tam+oy))

class Jugador:
    def __init__(self, f, c, sprites):
        self.f, self.c = f, c
        self.sprites = sprites
        self.dir = "idle"
    
    def dibujar(self, sup, tam, ox, oy):
        img = self.sprites.get(self.dir, self.sprites["idle"])
        sup.blit(img, (self.c*tam+ox, self.f*tam+oy))


class MiJuego(GameBase):
    def __init__(self):
        pygame.init()
        meta = GameMetadata(
            title="Sokoban",
            description="Lógica y estrategia.",
            authors=["Grupo 6"],
            group_number=6
        )
        super().__init__(meta)
        
        self.TAM = 60
        self.estado = "MENU"
        self.menu = None 
        
        self.modo = "normal"
        self.dificultad = "facil"
        self.indice_niv = 0
        self.hist = []
        self.completado = False
        
        self.tiempo = 0.0
        self.ganados = 0
        self.agotado = False
        self.audio = GestorAudio()

    def escalar_mouse(self, pos):
        

        
        ventana_w, ventana_h = pygame.display.get_surface().get_size()
        juego_w, juego_h = self.surface.get_size()
        
        
        if ventana_w == 0 or ventana_h == 0: return (0, 0)
            
        rx = pos[0] * (juego_w / ventana_w)
        ry = pos[1] * (juego_h / ventana_h)
        return (rx, ry)

    def cargar_imgs(self):
        base = os.path.dirname(__file__)
        def load(n):
            path = os.path.join(base, "assets", "sprites", n)
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.TAM, self.TAM))
            except:
                surf = pygame.Surface((self.TAM, self.TAM))
                surf.fill((255, 0, 0) if "muro" in n else (0, 255, 0))
                return surf
        
        caja = load("caja.png")
        caja_meta = caja.copy()
        filtro = pygame.Surface((self.TAM, self.TAM), pygame.SRCALPHA)
        filtro.fill((100, 255, 100, 180))
        caja_meta.blit(filtro, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

        self.imgs = {'suelo': load("suelo.png"), 'muro': load("muro.png"), 
                     'meta': load("meta.png"), 'caja': caja, 'caja_meta': caja_meta}
        
        der = load("jugador_der.png")
        self.sprites = {
            'idle': load("jugador_idle.png"), 'arriba': load("jugador_arriba.png"),
            'abajo': load("jugador_abajo.png"), 'derecha': der, 
            'izquierda': pygame.transform.flip(der, True, False)
        }
        self.font_grande = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_chica = pygame.font.SysFont("Arial", 22)
        self.font_reloj = pygame.font.SysFont("Arial", 28, bold=True)

    def on_start(self):
        self.menu = InterfazMenu(self.surface.get_width(), self.surface.get_height())
        self.cargar_imgs()
        self.audio.reproducir_musica("MusicaFondo.ogg")

    def cargar_nivel(self, d, i):
        if d in MAPAS and i < len(MAPAS[d]):
            datos = MAPAS[d][i]
            self.tab = Tablero(datos, self.imgs)
            self.cajas = [Caja(f,c,self.imgs) for f, fila in enumerate(datos) for c, v in enumerate(fila) if v == "B"]
            pf, pc = [(f,c) for f, fila in enumerate(datos) for c, v in enumerate(fila) if v == "P"][0]
            self.player = Jugador(pf, pc, self.sprites)
            
            self.hist = []
            self.completado = False
            self.dificultad = d
            self.indice_niv = i
            self.estado = "JUGANDO"
        else:
            self.estado = "MENU"

    
    def handle_events(self, events):
        
        mouse_pos_actual = pygame.mouse.get_pos()
        mouse_convertido_actual = self.escalar_mouse(mouse_pos_actual)

        for evento in events:
            
            mouse_pos_click = None
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                
                mouse_pos_click = self.escalar_mouse(evento.pos)
            
            if evento.type == pygame.QUIT:
                self._stop_context()
            
            elif self.estado == "MENU":
                
                self.logica_menu(evento, mouse_pos_click, mouse_convertido_actual)
            
            elif self.estado == "JUGANDO":
                self.logica_juego(evento)

    def update(self, dt):
        if self.estado == "JUGANDO" and self.modo == "contrareloj":
            if not self.completado and not self.agotado:
                self.tiempo -= dt
                if self.tiempo <= 0:
                    self.tiempo = 0
                    self.agotado = True

    def logica_menu(self, evento, pos_click, pos_actual):
        menu = self.menu
        
        
        if pos_click:
            if menu.submenu == "principal":
                if menu.btn_jugar.rect.collidepoint(pos_click): menu.submenu = "dificultad"
                elif menu.btn_ayuda.rect.collidepoint(pos_click): menu.submenu = "instrucciones"
                elif menu.btn_salir.rect.collidepoint(pos_click): self._stop_context()
            
            elif menu.submenu == "dificultad":
                if menu.btn_volver.rect.collidepoint(pos_click): menu.submenu = "principal"
                elif menu.btn_facil.rect.collidepoint(pos_click): 
                    self.modo = "normal"; self.cargar_nivel("facil", 0)
                elif menu.btn_medio.rect.collidepoint(pos_click): 
                    self.modo = "normal"; self.cargar_nivel("medio", 0)
                elif menu.btn_dificil.rect.collidepoint(pos_click): 
                    self.modo = "normal"; self.cargar_nivel("dificil", 0)
                elif menu.btn_reloj.rect.collidepoint(pos_click): 
                    self.modo = "contrareloj"; self.tiempo = 180.0; self.ganados = 0; self.agotado = False; self.cargar_random()
            
            elif menu.submenu == "instrucciones":
                if menu.btn_volver.rect.collidepoint(pos_click): menu.submenu = "principal"

    def cargar_random(self):
        d = random.choice(list(MAPAS.keys()))
        i = random.randint(0, len(MAPAS[d])-1)
        self.cargar_nivel(d, i)

    def logica_juego(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE: self.estado = "MENU"
            elif self.agotado:
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE): self.estado = "MENU"
            elif evento.key == pygame.K_r: self.cargar_nivel(self.dificultad, self.indice_niv)
            elif evento.key == pygame.K_z: self.deshacer()
            elif self.completado and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.modo == "contrareloj":
                    self.ganados += 1; self.cargar_random()
                else: self.cargar_nivel(self.dificultad, self.indice_niv+1)
            elif not self.completado:
                moves = {
                    pygame.K_UP: (-1,0,"arriba"), pygame.K_w: (-1,0,"arriba"),
                    pygame.K_DOWN: (1,0,"abajo"), pygame.K_s: (1,0,"abajo"),
                    pygame.K_LEFT: (0,-1,"izquierda"), pygame.K_a: (0,-1,"izquierda"),
                    pygame.K_RIGHT: (0,1,"derecha"), pygame.K_d: (0,1,"derecha")
                }
                if evento.key in moves:
                    self.mover(moves[evento.key])

    def mover(self, datos):
        df, dc, dir_n = datos
        self.player.dir = dir_n
        estado = {'p': (self.player.f, self.player.c), 'c': [(ca.f, ca.c) for ca in self.cajas]}
        
        nf, nc = self.player.f + df, self.player.c + dc
        if self.tab.es_muro(nf, nc): return
        
        caja = next((c for c in self.cajas if c.f == nf and c.c == nc), None)
        if caja:
            tf, tc = nf + df, nc + dc
            if self.tab.es_muro(tf, tc) or any(c.f == tf and c.c == tc for c in self.cajas): return
            caja.f, caja.c = tf, tc
        
        self.player.f, self.player.c = nf, nc
        self.hist.append(estado)
        self.completado = all((ca.f, ca.c) in self.tab.metas for ca in self.cajas)
        if self.completado: self.audio.reproducir_sfx("victoria")

    def deshacer(self):
        if self.hist:
            e = self.hist.pop()
            self.player.f, self.player.c = e['p']
            for i, pos in enumerate(e['c']): self.cajas[i].f, self.cajas[i].c = pos
            self.completado = False

    def draw(self):
        self.surface.fill((35, 45, 60))
        if self.estado == "MENU":
            self.dibujar_menu()
        else:
            self.dibujar_juego()

    def dibujar_menu(self):
        m = self.menu
        
        mpos = self.escalar_mouse(pygame.mouse.get_pos())
        
        if m.submenu == "principal":
            self.dibujar_txt("SOKOBAN", 80)
            m.btn_jugar.dibujar(self.surface, mpos)
            m.btn_ayuda.dibujar(self.surface, mpos)
            m.btn_salir.dibujar(self.surface, mpos)
            
            # Dibujo personaje
            if 'derecha' in self.sprites:
                img = pygame.transform.scale(self.sprites['derecha'], (180,180))
                y = m.btn_ayuda.rect.centery - 90
                self.surface.blit(img, (m.btn_ayuda.rect.left - 200, y))
        elif m.submenu == "dificultad":
            self.dibujar_txt("SELECCIONA MODO", 60)
            m.btn_facil.dibujar(self.surface, mpos)
            m.btn_medio.dibujar(self.surface, mpos)
            m.btn_dificil.dibujar(self.surface, mpos)
            m.btn_reloj.dibujar(self.surface, mpos)
            m.btn_volver.dibujar(self.surface, mpos)
        elif m.submenu == "instrucciones":
            self.dibujar_txt("CÓMO JUGAR", 80)
            txts = ["Empuja las cajas a las metas.", "• Flechas/WASD: Mover", "• Z: Deshacer", "• R: Reiniciar", "• ESC: Menú"]
            for i, t in enumerate(txts):
                img = self.font_chica.render(t, True, (220,220,220))
                self.surface.blit(img, (self.surface.get_width()//2 - img.get_width()//2, 180 + i*40))
            m.btn_volver.dibujar(self.surface, mpos)

    def dibujar_txt(self, txt, y):
        t = self.font_grande.render(txt, True, (255, 215, 0))
        self.surface.blit(t, (self.surface.get_width()//2 - t.get_width()//2, y))

    def dibujar_juego(self):
        w = self.tab.cols * self.TAM
        h = self.tab.filas * self.TAM
        ox = (self.surface.get_width() - w) // 2
        oy = (self.surface.get_height() - h) // 2
        
        self.tab.dibujar(self.surface, self.TAM, ox, oy)
        for c in self.cajas: c.dibujar(self.surface, self.TAM, self.tab, ox, oy)
        self.player.dibujar(self.surface, self.TAM, ox, oy)
        
        if self.modo == "contrareloj":
            t = self.font_reloj.render(f"TIEMPO: {int(self.tiempo//60):02d}:{int(self.tiempo%60):02d}", True, (255,100,100))
            self.surface.blit(t, (self.surface.get_width()//2 - t.get_width()//2, 20))
        
        if self.agotado:
            self.dibujar_cartel("¡TIEMPO AGOTADO!", f"Niveles: {self.ganados}")
        elif self.completado:
            self.dibujar_cartel("¡NIVEL COMPLETADO!", "ESPACIO para continuar")

    def dibujar_cartel(self, t1, t2):
        s = pygame.Surface((400, 150), pygame.SRCALPHA)
        s.fill((0,0,0,180))
        self.surface.blit(s, (self.surface.get_width()//2 - 200, self.surface.get_height()//2 - 75))
        img1 = self.font_reloj.render(t1, True, (255,255,255))
        img2 = self.font_chica.render(t2, True, (200,200,200))
        self.surface.blit(img1, (self.surface.get_width()//2 - img1.get_width()//2, self.surface.get_height()//2 - 30))
        self.surface.blit(img2, (self.surface.get_width()//2 - img2.get_width()//2, self.surface.get_height()//2 + 20))

if __name__ == "__main__":
    MiJuego().run_preview()
    