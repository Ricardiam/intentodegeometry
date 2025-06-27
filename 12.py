import pygame
import random

pygame.init()
pygame.mixer.init()

# --- CLASE MENU ALTAMENTE MEJORADA ---
class Menu:
    def __init__(self, pantalla, fuente_grande, fuente_normal, colores):
        self.pantalla = pantalla
        self.fuente_grande = fuente_grande
        self.fuente_normal = fuente_normal
        self.colores = colores
        
        ancho = self.pantalla.get_width()
        alto = self.pantalla.get_height()

        self.estado_menu = "PRINCIPAL"
        self.boton_jugar = pygame.Rect(ancho//2 - 100, 250, 200, 50)
        self.boton_instrucciones = pygame.Rect(ancho//2 - 100, 320, 200, 50)
        self.boton_salir = pygame.Rect(ancho//2 - 100, 390, 200, 50)
        self.boton_volver = pygame.Rect(ancho//2 - 100, 450, 200, 50)
        self.color_normal = (0, 100, 200)
        self.color_hover = (0, 150, 255)

    def _dibujar_boton(self, rect, texto, mouse_pos):
        color_actual = self.color_hover if rect.collidepoint(mouse_pos) else self.color_normal
        pygame.draw.rect(self.pantalla, color_actual, rect, border_radius=10)
        texto_surf = self.fuente_normal.render(texto, True, self.colores["BLANCO"])
        texto_rect = texto_surf.get_rect(center=rect.center)
        self.pantalla.blit(texto_surf, texto_rect)

    def dibujar(self, fondo, mouse_pos):
        self.pantalla.blit(fondo, (0, 0))
        if self.estado_menu == "PRINCIPAL":
            titulo = self.fuente_grande.render("Geometry Dash", True, self.colores["BLANCO"])
            self.pantalla.blit(titulo, (self.pantalla.get_width()//2 - titulo.get_width()//2, 150))
            self._dibujar_boton(self.boton_jugar, "Jugar", mouse_pos)
            self._dibujar_boton(self.boton_instrucciones, "Instrucciones", mouse_pos)
            self._dibujar_boton(self.boton_salir, "Salir", mouse_pos)
        else:
            titulo = self.fuente_grande.render("Instrucciones", True, self.colores["BLANCO"])
            self.pantalla.blit(titulo, (self.pantalla.get_width()//2 - titulo.get_width()//2, 100))
            instrucciones = [
                "¡Bienvenido a Geometry Dash!",
                "",
                "- Usa [ESPACIO] para saltar.",
                "- Nivel 1: esquiva triángulos rojos.",
                "- Nivel 2: obstáculos más rápidos y variables.",
                "- ¡Consigue 10 puntos para cada nivel!"
            ]
            for i, linea in enumerate(instrucciones):
                texto_linea = self.fuente_normal.render(linea, True, self.colores["BLANCO"])
                self.pantalla.blit(texto_linea, (self.pantalla.get_width()//2 - texto_linea.get_width()//2, 200 + i * 40))
            self._dibujar_boton(self.boton_volver, "Volver", mouse_pos)

    def manejar_eventos(self, eventos):
        for e in eventos:
            if e.type == pygame.QUIT:
                return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                pos = e.pos
                if self.estado_menu == "PRINCIPAL":
                    if self.boton_jugar.collidepoint(pos): return "INICIAR_JUEGO"
                    if self.boton_instrucciones.collidepoint(pos): self.estado_menu = "INSTRUCCIONES"
                    if self.boton_salir.collidepoint(pos): return "SALIR"
                else:
                    if self.boton_volver.collidepoint(pos): self.estado_menu = "PRINCIPAL"
        return None

# --- CLASES DE JUEGO ---
class ObjetoJuego:
    def __init__(self, x, y, ancho, alto, color):
        self.x, self.y = x, y
        self.ancho, self.alto = ancho, alto
        self.color = color
        self.rectangulo = pygame.Rect(x, y, ancho, alto)
    def actualizar_rectangulo(self):
        self.rectangulo.x, self.rectangulo.y = self.x, self.y

class Jugador(ObjetoJuego):
    def __init__(self, x, y, tamaño, color, y_suelo):
        super().__init__(x, y, tamaño, tamaño, color)
        self.y_suelo = y_suelo
        self.velocidad_y = 0
        self.esta_saltando = False
    def saltar(self):
        if not self.esta_saltando:
            self.velocidad_y = -15
            self.esta_saltando = True
    def actualizar(self):
        self.velocidad_y += 1
        self.y += self.velocidad_y
        if self.y >= self.y_suelo:
            self.y = self.y_suelo
            self.velocidad_y = 0
            self.esta_saltando = False
        self.actualizar_rectangulo()
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rectangulo)

class ObjetoMovil(ObjetoJuego):
    def __init__(self, x, y, ancho, alto, color, velocidad, ancho_pantalla):
        super().__init__(x, y, ancho, alto, color)
        self.velocidad = velocidad
        self.ancho_pantalla = ancho_pantalla
    def mover(self):
        self.x -= self.velocidad
        self.actualizar_rectangulo()

class Suelo(ObjetoMovil):
    def actualizar(self):
        self.mover()
        if self.x <= -self.ancho:
            self.x = 0
    def dibujar(self, pantalla, fondo_img):
        pantalla.blit(fondo_img, (self.x, 0))
        pantalla.blit(fondo_img, (self.x + self.ancho, 0))
        pygame.draw.rect(pantalla, self.color, (self.x, self.y, self.ancho, self.alto))
        pygame.draw.rect(pantalla, self.color, (self.x + self.ancho, self.y, self.ancho, self.alto))

class Obstaculo(ObjetoMovil):
    def __init__(self, x, y, tamaño, color, velocidad, ancho_pantalla):
        super().__init__(x, y, tamaño, tamaño, color, velocidad, ancho_pantalla)
        self.fue_superado = False
    def actualizar(self):
        self.mover()
    def dibujar(self, pantalla):
        puntos = [(self.x, self.y), (self.x + self.ancho, self.y), (self.x + self.ancho // 2, self.y - self.alto)]
        pygame.draw.polygon(pantalla, self.color, puntos)
    def obtener_rectangulo_colision(self):
        return pygame.Rect(self.x + self.ancho // 4, self.y - self.alto, self.ancho // 2, self.alto)

# --- Obstáculo Nivel 2: variable y movimiento vertical ---
class ObstaculoNivel2(Obstaculo):
    def __init__(self, x, y, velocidad, ancho_pantalla):
        tamaño = random.randint(25, 45)
        color = (255, random.randint(0, 255), 0)
        super().__init__(x, y, tamaño, color, velocidad + random.randint(0, 5), ancho_pantalla)
        self.mueve_vertical = random.choice([True, False])
        self.direccion = 1
        self.limite_superior = y - 80
        self.limite_inferior = y

    def actualizar(self):
        self.mover()
        if self.mueve_vertical:
            self.y += self.direccion * 2
            if self.y <= self.limite_superior or self.y >= self.limite_inferior:
                self.direccion *= -1
        self.actualizar_rectangulo()

# --- CLASE JUEGO PRINCIPAL ---
class Juego:
    def __init__(self):
        self.ancho_pantalla, self.alto_pantalla = 800, 600
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption("Geometry Dash + Nivel 2")
        self.reloj = pygame.time.Clock()
        self.fondo = pygame.transform.scale(pygame.image.load("bg.png").convert(), (self.ancho_pantalla, self.alto_pantalla))
        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_normal = pygame.font.Font(None, 48)
        self.colores = {"BLANCO": (255, 255, 255), "ROJO": (255, 0, 0), "GRIS": (50, 50, 50)}
        self.velocidad_juego = 10
        self.cargar_audio()
        self.estado = "MENU"
        self.menu = Menu(self.pantalla, self.fuente_grande, self.fuente_normal, self.colores)
        self.nivel_actual = 1

    def cargar_audio(self):
        try:
            self.musica_juego = "bossfight-Vextron.mp3"
            self.sonido_win = pygame.mixer.Sound("win.mp3")
            self.sonido_lose = pygame.mixer.Sound("lose.mp3")
        except pygame.error as e:
            print(f"Error al cargar audio: {e}")
            self.musica_juego = self.sonido_win = self.sonido_lose = None

    def reproducir_musica_juego(self):
        if self.musica_juego:
            pygame.mixer.music.load(self.musica_juego)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)

    def reproducir_sonido_win(self):
        if self.sonido_win:
            pygame.mixer.music.stop()
            self.sonido_win.play()

    def reproducir_sonido_lose(self):
        if self.sonido_lose:
            pygame.mixer.music.stop()
            self.sonido_lose.play()

    def inicializar_partida(self):
        y_suelo = 450
        self.jugador = Jugador(100, y_suelo - 50, 50, self.colores["BLANCO"], y_suelo - 50)
        self.suelo = Suelo(0, y_suelo, self.ancho_pantalla, 150, self.colores["GRIS"], self.velocidad_juego, self.ancho_pantalla)
        self.puntuacion = 0
        self.mapa_nivel_distancias = [random.randint(350, 600) for _ in range(20)]
        self.obstaculos_restantes_mapa = list(self.mapa_nivel_distancias)
        self.obstaculos_activos = []
        self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)
        self.reproducir_musica_juego()

    def inicializar_partida_nivel2(self):
        self.nivel_actual = 2
        y_suelo = 450
        self.jugador = Jugador(100, y_suelo - 50, 50, self.colores["BLANCO"], y_suelo - 50)
        self.suelo = Suelo(0, y_suelo, self.ancho_pantalla, 150, self.colores["GRIS"], self.velocidad_juego, self.ancho_pantalla)
        self.puntuacion = 0
        self.mapa_nivel_distancias = [random.randint(250, 500) for _ in range(30)]
        self.obstaculos_restantes_mapa = list(self.mapa_nivel_distancias)
        self.obstaculos_activos = []
        self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)
        self.reproducir_musica_juego()

    def manejar_eventos_juego(self, eventos):
        for e in eventos:
            if e.type == pygame.QUIT: return "SALIR"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: self.jugador.saltar()
        return None

    def manejar_eventos_fin_partida(self, eventos):
        for e in eventos:
            if e.type == pygame.QUIT: return "SALIR"
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN): return "VOLVER_AL_MENU"
        return None

    def actualizar_juego(self):
        self.jugador.actualizar()
        self.suelo.actualizar()

        self.distancia_para_siguiente_obstaculo -= self.velocidad_juego
        if self.distancia_para_siguiente_obstaculo <= 0:
            if self.nivel_actual == 1:
                obst = Obstaculo(self.ancho_pantalla, self.suelo.y, 35, self.colores["ROJO"], self.velocidad_juego, self.ancho_pantalla)
            else:
                obst = ObstaculoNivel2(self.ancho_pantalla, self.suelo.y, self.velocidad_juego, self.ancho_pantalla)
            self.obstaculos_activos.append(obst)
            if self.obstaculos_restantes_mapa:
                self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)
            else:
                self.distancia_para_siguiente_obstaculo = float("inf")

        for obst in self.obstaculos_activos:
            obst.actualizar()
            if self.jugador.rectangulo.colliderect(obst.obtener_rectangulo_colision()):
                self.estado = "GAME_OVER"
                self.reproducir_sonido_lose()
            if not obst.fue_superado and self.jugador.x > obst.x + obst.ancho:
                obst.fue_superado = True
                self.puntuacion += 1
                if self.puntuacion >= 10:
                    if self.nivel_actual == 1:
                        self.inicializar_partida_nivel2()
                    else:
                        self.estado = "WIN"
                        self.reproducir_sonido_win()

        self.obstaculos_activos = [o for o in self.obstaculos_activos if o.x + o.ancho > 0]

    def dibujar_juego(self):
        self.suelo.dibujar(self.pantalla, self.fondo)
        self.jugador.dibujar(self.pantalla)
        for obst in self.obstaculos_activos:
            obst.dibujar(self.pantalla)
        texto = self.fuente_normal.render(f"Nivel {self.nivel_actual} - Puntos: {self.puntuacion}", True, self.colores["BLANCO"])
        self.pantalla.blit(texto, (20, 20))

    def dibujar_pantalla_final(self, mensaje):
        self.dibujar_juego()
        overlay = pygame.Surface((self.ancho_pantalla, self.alto_pantalla), pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        self.pantalla.blit(overlay, (0,0))
        final = self.fuente_grande.render(mensaje, True, self.colores["BLANCO"])
        reiniciar = self.fuente_normal.render("Click o ESPACIO para volver al Menú", True, (200,200,200))
        self.pantalla.blit(final, (self.ancho_pantalla//2 - final.get_width()//2, 250))
        self.pantalla.blit(reiniciar, (self.ancho_pantalla//2 - reiniciar.get_width()//2, 330))

    def ejecutar_juego(self):
        corriendo = True
        while corriendo:
            eventos = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()
            if self.estado == "MENU":
                self.menu.dibujar(self.fondo, mouse_pos)
                acc = self.menu.manejar_eventos(eventos)
                if acc == "INICIAR_JUEGO":
                    self.nivel_actual = 1
                    self.inicializar_partida()
                    self.estado = "JUGANDO"
                elif acc == "SALIR":
                    corriendo = False
            elif self.estado == "JUGANDO":
                self.actualizar_juego()
                self.dibujar_juego()
                if self.manejar_eventos_juego(eventos) == "SALIR":
                    corriendo = False
            elif self.estado == "GAME_OVER":
                self.dibujar_pantalla_final("Game Over")
                acc = self.manejar_eventos_fin_partida(eventos)
                if acc == "VOLVER_AL_MENU":
                    self.estado = "MENU"
                elif acc == "SALIR":
                    corriendo = False
            elif self.estado == "WIN":
                self.dibujar_pantalla_final("¡GANASTE!")
                acc = self.manejar_eventos_fin_partida(eventos)
                if acc == "VOLVER_AL_MENU":
                    self.estado = "MENU"
                elif acc == "SALIR":
                    corriendo = False

            pygame.display.flip()
            self.reloj.tick(60)
        pygame.quit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar_juego()
