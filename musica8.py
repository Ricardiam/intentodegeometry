import pygame
import random # <-- AÑADIDO: Necesario para los obstáculos aleatorios

pygame.init()
pygame.mixer.init()

# --- CLASES DEL JUEGO (Sin cambios en Jugador, Obstaculo, etc., solo en Suelo y Juego) ---

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
        # Cuando el suelo se sale completamente de la pantalla por la izquierda, se reinicia
        if self.x <= -self.ancho:
            self.x = 0

    def dibujar(self, pantalla, fondo):
        # --- MÉTODO MODIFICADO PARA EL EFECTO PARALLAX ---
        # Dibujamos dos copias del fondo, una al lado de la otra, para un bucle perfecto
        pantalla.blit(fondo, (self.x, 0))
        pantalla.blit(fondo, (self.x + self.ancho, 0))
        
        # Dibujamos el suelo visible (dos rectángulos para que parezca infinito)
        pygame.draw.rect(pantalla, self.color, (self.x, self.y, self.ancho, self.alto))
        pygame.draw.rect(pantalla, self.color, (self.x + self.ancho, self.y, self.ancho, self.alto))


class Obstaculo(ObjetoMovil):
    def __init__(self, x, y, tamaño, color, velocidad, ancho_pantalla):
        super().__init__(x, y, tamaño, tamaño, color, velocidad, ancho_pantalla)
        self.fue_superado = False

    def actualizar(self):
        self.mover()

    def dibujar(self, pantalla):
        puntos = [
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho // 2, self.y - self.alto),
        ]
        pygame.draw.polygon(pantalla, self.color, puntos)

    def obtener_rectangulo_colision(self):
        return pygame.Rect(self.x + self.ancho // 4, self.y - self.alto, self.ancho // 2, self.alto)


class Juego:
    def __init__(self):
        self.ancho_pantalla, self.alto_pantalla = 800, 600
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption("Geometry Dash Mejorado")
        self.reloj = pygame.time.Clock()

        self.fondo = pygame.transform.scale(pygame.image.load("bg.png").convert(), (self.ancho_pantalla, self.alto_pantalla))

        self.colores = {
            "BLANCO": (255, 255, 255),
            "ROJO": (255, 0, 0),
            "GRIS": (50, 50, 50),
        }

        self.velocidad_juego = 10
        self.esta_ejecutando = True

        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_normal = pygame.font.Font(None, 48)

        self.cargar_audio()
        self.inicializar_juego()

    def cargar_audio(self):
        """Carga los archivos de música y sonidos. REQUIERE win.mp3 y lose.mp3"""
        try:
            self.musica_juego = "bossfight-Vextron.mp3"
            # --- NUEVO: Sonidos específicos para ganar y perder ---
            self.sonido_win = pygame.mixer.Sound("bossfight-Vextron.mp3")
            self.sonido_lose = pygame.mixer.Sound("Castle-town.mp3")
            print("Audio cargado correctamente")
        except pygame.error as e:
            print(f"Error al cargar audio: {e}")
            print("Asegúrate de tener 'win.mp3' y 'lose.mp3' en la carpeta del juego.")
            self.musica_juego = None
            self.sonido_win = None
            self.sonido_lose = None

    def reproducir_musica_juego(self):
        if self.musica_juego:
            try:
                pygame.mixer.music.load(self.musica_juego)
                pygame.mixer.music.set_volume(0.04)
                pygame.mixer.music.play(-1)
            except pygame.error as e:
                print(f"Error al reproducir música del juego: {e}")

    # --- NUEVOS MÉTODOS DE AUDIO ---
    def reproducir_sonido_win(self):
        if self.sonido_win:
            pygame.mixer.music.stop()
            self.sonido_win.set_volume(0.2)
            self.sonido_win.play()
    
    def reproducir_sonido_lose(self):
        if self.sonido_lose:
            pygame.mixer.music.stop()
            self.sonido_lose.set_volume(0.1)
            self.sonido_lose.play()

    def detener_audio(self):
        pygame.mixer.music.stop()
        pygame.mixer.stop()

    def inicializar_juego(self):
        y_suelo = 450
        self.jugador = Jugador(100, y_suelo - 50, 50, self.colores["BLANCO"], y_suelo - 50)
        # --- MODIFICADO: El suelo ahora necesita saber el ancho de la pantalla para el bucle del fondo ---
        self.suelo = Suelo(0, y_suelo, self.ancho_pantalla, 150, self.colores["GRIS"], self.velocidad_juego, self.ancho_pantalla)
        
        self.puntuacion = 0
        self.juego_terminado = False
        self.juego_ganado = False
        
        # --- NUEVO: Estado para la pantalla de inicio ---
        self.juego_iniciado = False

        # --- MODIFICADO: Mapa de obstáculos con distancias aleatorias ---
        self.mapa_nivel_distancias = [random.randint(350, 600) for _ in range(20)]
        self.obstaculos_restantes_mapa = list(self.mapa_nivel_distancias)
        self.obstaculos_activos = []

        self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)
        self.detener_audio() # Aseguramos que no haya música de una partida anterior

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.esta_ejecutando = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                if not self.juego_iniciado:
                    # --- NUEVO: Iniciar el juego por primera vez ---
                    self.juego_iniciado = True
                    self.reproducir_musica_juego()
                elif self.juego_terminado or self.juego_ganado:
                    self.inicializar_juego()
                else:
                    self.jugador.saltar()

    def actualizar_juego(self):
        # --- MODIFICADO: El juego solo se actualiza si ha comenzado ---
        if not self.juego_iniciado or self.juego_terminado or self.juego_ganado:
            return

        self.jugador.actualizar()
        self.suelo.actualizar()

        self.distancia_para_siguiente_obstaculo -= self.velocidad_juego
        if self.distancia_para_siguiente_obstaculo <= 0:
            self.obstaculos_activos.append(Obstaculo(self.ancho_pantalla, self.suelo.y, 35, self.colores["ROJO"], self.velocidad_juego, self.ancho_pantalla))
            if self.obstaculos_restantes_mapa:
                self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)
            else:
                self.distancia_para_siguiente_obstaculo = float("inf")

        for obstaculo in self.obstaculos_activos:
            obstaculo.actualizar()

            if self.jugador.rectangulo.colliderect(obstaculo.obtener_rectangulo_colision()):
                self.juego_terminado = True
                self.reproducir_sonido_lose() # --- MODIFICADO: Usar sonido de derrota ---
                return

            if not obstaculo.fue_superado and self.jugador.x > obstaculo.x + obstaculo.ancho:
                obstaculo.fue_superado = True
                self.puntuacion += 1

                # --- MODIFICADO: Condición de victoria a 10 puntos ---
                if self.puntuacion >= 10:
                    self.juego_ganado = True
                    self.reproducir_sonido_win() # --- MODIFICADO: Usar sonido de victoria ---
                    return

        self.obstaculos_activos = [o for o in self.obstaculos_activos if o.x + o.ancho > 0]

    def dibujar_juego(self):
        # --- MODIFICADO: Ahora se pasa el fondo al método de dibujar del suelo ---
        self.suelo.dibujar(self.pantalla, self.fondo)
        
        # Solo dibujamos los elementos del juego si ha iniciado
        if self.juego_iniciado:
            self.jugador.dibujar(self.pantalla)
            for obstaculo in self.obstaculos_activos:
                obstaculo.dibujar(self.pantalla)

        texto_puntuacion = self.fuente_normal.render(f"Puntuación: {self.puntuacion}", True, self.colores["BLANCO"])
        self.pantalla.blit(texto_puntuacion, (20, 20))

        # --- LÓGICA DE DIBUJO MODIFICADA para incluir la pantalla de inicio ---
        if not self.juego_iniciado:
            texto_inicio_1 = self.fuente_grande.render("Geometry Dash", True, self.colores["BLANCO"])
            texto_inicio_2 = self.fuente_normal.render("Presiona ESPACIO para empezar", True, (200, 200, 200))
            self.pantalla.blit(texto_inicio_1, (self.ancho_pantalla // 2 - texto_inicio_1.get_width() // 2, 250))
            self.pantalla.blit(texto_inicio_2, (self.ancho_pantalla // 2 - texto_inicio_2.get_width() // 2, 330))

        elif self.juego_terminado or self.juego_ganado:
            superposicion = pygame.Surface((self.ancho_pantalla, self.alto_pantalla), pygame.SRCALPHA)
            superposicion.fill((0, 0, 0, 150)) # Negro con transparencia
            self.pantalla.blit(superposicion, (0, 0))
            
            # --- MODIFICADO: Mensaje de victoria ---
            mensaje = "WIN" if self.juego_ganado else "Game Over"
            
            texto_final = self.fuente_grande.render(mensaje, True, self.colores["BLANCO"])
            texto_reiniciar = self.fuente_normal.render("Presiona ESPACIO para reintentar", True, (200, 200, 200))
            
            self.pantalla.blit(texto_final, (self.ancho_pantalla // 2 - texto_final.get_width() // 2, 250))
            self.pantalla.blit(texto_reiniciar, (self.ancho_pantalla // 2 - texto_reiniciar.get_width() // 2, 330))


    def ejecutar_juego(self):
        while self.esta_ejecutando:
            self.manejar_eventos()
            self.actualizar_juego()
            self.dibujar_juego()
            pygame.display.flip()
            self.reloj.tick(60)
        
        self.detener_audio()
        pygame.quit()


if __name__ == "__main__":
    Juego().ejecutar_juego()