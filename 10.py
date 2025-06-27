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

        # Estado interno del menú: "PRINCIPAL" o "INSTRUCCIONES"
        self.estado_menu = "PRINCIPAL"

        # --- RECTS DE LOS BOTONES ---
        self.boton_jugar = pygame.Rect(ancho//2 - 100, 250, 200, 50)
        self.boton_instrucciones = pygame.Rect(ancho//2 - 100, 320, 200, 50)
        self.boton_salir = pygame.Rect(ancho//2 - 100, 390, 200, 50)
        self.boton_volver = pygame.Rect(ancho//2 - 100, 450, 200, 50)
        
        # Colores de los botones
        self.color_normal = (0, 100, 200)
        self.color_hover = (0, 150, 255)

    def _dibujar_boton(self, rect, texto, mouse_pos):
        """Función auxiliar para dibujar un botón y manejar el efecto hover."""
        color_actual = self.color_hover if rect.collidepoint(mouse_pos) else self.color_normal
        pygame.draw.rect(self.pantalla, color_actual, rect, border_radius=10)
        
        texto_surf = self.fuente_normal.render(texto, True, self.colores["BLANCO"])
        texto_rect = texto_surf.get_rect(center=rect.center)
        self.pantalla.blit(texto_surf, texto_rect)

    def dibujar(self, fondo, mouse_pos):
        """Dibuja la pantalla de menú correcta según el estado interno."""
        self.pantalla.blit(fondo, (0, 0))
        
        if self.estado_menu == "PRINCIPAL":
            # Dibujar Título
            texto_titulo = self.fuente_grande.render("Geometry Dash", True, self.colores["BLANCO"])
            self.pantalla.blit(texto_titulo, (self.pantalla.get_width()//2 - texto_titulo.get_width()//2, 150))
            
            # Dibujar Botones
            self._dibujar_boton(self.boton_jugar, "Jugar", mouse_pos)
            self._dibujar_boton(self.boton_instrucciones, "Instrucciones", mouse_pos)
            self._dibujar_boton(self.boton_salir, "Salir", mouse_pos)

        elif self.estado_menu == "INSTRUCCIONES":
            # Dibujar Título de Instrucciones
            texto_titulo = self.fuente_grande.render("Instrucciones", True, self.colores["BLANCO"])
            self.pantalla.blit(texto_titulo, (self.pantalla.get_width()//2 - texto_titulo.get_width()//2, 100))

            # Texto de las instrucciones
            instrucciones = [
                "¡Bienvenido a Geometry Dash!",
                "",
                "- Usa [ESPACIO] para saltar.",
                "- Esquiva los obstáculos triangulares.",
                "- ¡Consigue 10 puntos para ganar!",
            ]
            
            for i, linea in enumerate(instrucciones):
                texto_linea = self.fuente_normal.render(linea, True, self.colores["BLANCO"])
                self.pantalla.blit(texto_linea, (self.pantalla.get_width()//2 - texto_linea.get_width()//2, 200 + i * 40))

            # Dibujar Botón de Volver
            self._dibujar_boton(self.boton_volver, "Volver", mouse_pos)

    def manejar_eventos(self, eventos):
        """Procesa la entrada del ratón y retorna una acción si es necesario."""
        for evento in eventos:
            if evento.type == pygame.QUIT:
                return "SALIR"
            
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_pos = evento.pos
                
                if self.estado_menu == "PRINCIPAL":
                    if self.boton_jugar.collidepoint(mouse_pos):
                        return "INICIAR_JUEGO"
                    if self.boton_instrucciones.collidepoint(mouse_pos):
                        self.estado_menu = "INSTRUCCIONES" # Cambia al estado de instrucciones
                    if self.boton_salir.collidepoint(mouse_pos):
                        return "SALIR"

                elif self.estado_menu == "INSTRUCCIONES":
                    if self.boton_volver.collidepoint(mouse_pos):
                        self.estado_menu = "PRINCIPAL" # Vuelve al menú principal
        return None

# --- OTRAS CLASES (Jugador, Suelo, etc. no cambian) ---
class ObjetoJuego:
    def __init__(self, x, y, ancho, alto, color):
        self.x, self.y, self.ancho, self.alto, self.color = x, y, ancho, alto, color
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
    def dibujar(self, pantalla, fondo):
        pantalla.blit(fondo, (self.x, 0))
        pantalla.blit(fondo, (self.x + self.ancho, 0))
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

# --- CLASE JUEGO ADAPTADA AL NUEVO MENU ---
class Juego:
    def __init__(self):
        self.ancho_pantalla, self.alto_pantalla = 800, 600
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption("Geometry Dash con Menú Mejorado")
        self.reloj = pygame.time.Clock()

        # Recursos compartidos
        self.fondo = pygame.transform.scale(pygame.image.load("bg.png").convert(), (self.ancho_pantalla, self.alto_pantalla))
        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_normal = pygame.font.Font(None, 48)
        self.colores = {"BLANCO": (255, 255, 255), "ROJO": (255, 0, 0), "GRIS": (50, 50, 50)}

        self.velocidad_juego = 10
        self.cargar_audio()

        # Gestión de Estados
        self.estado = "MENU"
        self.menu = Menu(self.pantalla, self.fuente_grande, self.fuente_normal, self.colores)
        
    def cargar_audio(self):
        try:
            self.musica_juego = "bossfight-Vextron.mp3"
            self.sonido_win = pygame.mixer.Sound("bossfight-Vextron.mp3")
            self.sonido_lose = pygame.mixer.Sound("Castle-town.mp3")
        except pygame.error as e:
            print(f"Error al cargar audio: {e}")
            self.musica_juego = self.sonido_win = self.sonido_lose = None

    def reproducir_musica_juego(self):
        if self.musica_juego: pygame.mixer.music.load(self.musica_juego); pygame.mixer.music.set_volume(0.04); pygame.mixer.music.play(-1)
            
    def reproducir_sonido_win(self):
        if self.sonido_win: pygame.mixer.music.stop(); self.sonido_win.play()

    def reproducir_sonido_lose(self):
        if self.sonido_lose: pygame.mixer.music.stop(); self.sonido_lose.play()

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

    def manejar_eventos_juego(self, eventos):
        for evento in eventos:
            if evento.type == pygame.QUIT: return "SALIR"
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE: self.jugador.saltar()
        return None

    def manejar_eventos_fin_partida(self, eventos):
        for evento in eventos:
            if evento.type == pygame.QUIT: return "SALIR"
            if evento.type == pygame.KEYDOWN and (evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN): return "VOLVER_AL_MENU"
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1: return "VOLVER_AL_MENU"
        return None

    def actualizar_juego(self):
        self.jugador.actualizar()
        self.suelo.actualizar()

        self.distancia_para_siguiente_obstaculo -= self.velocidad_juego
        if self.distancia_para_siguiente_obstaculo <= 0:
            self.obstaculos_activos.append(Obstaculo(self.ancho_pantalla, self.suelo.y, 35, self.colores["ROJO"], self.velocidad_juego, self.ancho_pantalla))
            if self.obstaculos_restantes_mapa: self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)
            else: self.distancia_para_siguiente_obstaculo = float("inf")

        for obstaculo in self.obstaculos_activos:
            obstaculo.actualizar()
            if self.jugador.rectangulo.colliderect(obstaculo.obtener_rectangulo_colision()):
                self.estado = "GAME_OVER"; self.reproducir_sonido_lose()
            if not obstaculo.fue_superado and self.jugador.x > obstaculo.x + obstaculo.ancho:
                obstaculo.fue_superado = True; self.puntuacion += 1
                if self.puntuacion >= 10: self.estado = "WIN"; self.reproducir_sonido_win()

        self.obstaculos_activos = [o for o in self.obstaculos_activos if o.x + o.ancho > 0]

    def dibujar_juego(self):
        self.suelo.dibujar(self.pantalla, self.fondo)
        self.jugador.dibujar(self.pantalla)
        for obstaculo in self.obstaculos_activos: obstaculo.dibujar(self.pantalla)
        texto_puntuacion = self.fuente_normal.render(f"Puntuación: {self.puntuacion}", True, self.colores["BLANCO"])
        self.pantalla.blit(texto_puntuacion, (20, 20))

    def dibujar_pantalla_final(self, mensaje):
        self.dibujar_juego()
        superposicion = pygame.Surface((self.ancho_pantalla, self.alto_pantalla), pygame.SRCALPHA); superposicion.fill((0, 0, 0, 150))
        self.pantalla.blit(superposicion, (0, 0))
        texto_final = self.fuente_grande.render(mensaje, True, self.colores["BLANCO"])
        texto_reiniciar = self.fuente_normal.render("Click o ESPACIO para volver al Menú", True, (200, 200, 200))
        self.pantalla.blit(texto_final, (self.ancho_pantalla // 2 - texto_final.get_width() // 2, 250))
        self.pantalla.blit(texto_reiniciar, (self.ancho_pantalla // 2 - texto_reiniciar.get_width() // 2, 330))

    def ejecutar_juego(self):
        esta_ejecutando = True
        while esta_ejecutando:
            eventos = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            if self.estado == "MENU":
                self.menu.dibujar(self.fondo, mouse_pos)
                accion = self.menu.manejar_eventos(eventos)
                if accion == "INICIAR_JUEGO":
                    self.inicializar_partida(); self.estado = "JUGANDO"
                elif accion == "SALIR": esta_ejecutando = False

            elif self.estado == "JUGANDO":
                self.actualizar_juego(); self.dibujar_juego()
                if self.manejar_eventos_juego(eventos) == "SALIR": esta_ejecutando = False

            elif self.estado == "GAME_OVER":
                self.dibujar_pantalla_final("Game Over")
                accion = self.manejar_eventos_fin_partida(eventos)
                if accion == "VOLVER_AL_MENU": self.estado = "MENU"
                elif accion == "SALIR": esta_ejecutando = False
            
            elif self.estado == "WIN":
                self.dibujar_pantalla_final("WIN")
                accion = self.manejar_eventos_fin_partida(eventos)
                if accion == "VOLVER_AL_MENU": self.estado = "MENU"
                elif accion == "SALIR": esta_ejecutando = False
            
            pygame.display.flip()
            self.reloj.tick(60)

        pygame.quit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar_juego()