import pygame

pygame.init()
pygame.mixer.init()  # Inicializar el mixer de audio

# No hay cambios necesarios en las clases ObjetoJuego, Jugador, ObjetoMovil y Suelo
# Hacemos una pequeña mejora en Obstaculo para una colisión precisa (usaremos un rectángulo aproximado)


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
        if self.x <= -self.ancho_pantalla:
            self.x = 0

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, (self.x, self.y, self.ancho, self.alto))
        pygame.draw.rect(
            pantalla, self.color, (self.x + self.ancho, self.y, self.ancho, self.alto)
        )


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
        # Un rectángulo más estrecho para detectar colisiones
        return pygame.Rect(
            self.x + self.ancho // 4, self.y - self.alto, self.ancho // 2, self.alto
        )


class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Geometry Dash")
        self.reloj = pygame.time.Clock()

        self.colores = {
            "AZUL": (73, 115, 255),
            "BLANCO": (255, 255, 255),
            "ROJO": (255, 0, 0),
            "GRIS": (50, 50, 50),
        }

        self.velocidad_juego = 10
        self.esta_ejecutando = True

        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_normal = pygame.font.Font(None, 48)

        self.mapa_nivel_1_distancias = [420] * 20  # 20 obstáculos

        # Cargar música y sonidos
        self.cargar_audio()
        
        self.inicializar_juego()

    def cargar_audio(self):
        """Carga los archivos de música y sonidos"""
        try:
            # Cargar música de fondo del juego
            self.musica_juego = "bossfight-Vextron.mp3"
            
            # Cargar sonido de game over
            self.sonido_game_over = pygame.mixer.Sound("Castle-town.mp3")
            
            print("Audio cargado correctamente")
            
        except pygame.error as e:
            print(f"Error al cargar audio: {e}")
            print("Asegúrate de que los archivos de audio estén en la misma carpeta que el juego")
            # Crear variables vacías si no se puede cargar el audio
            self.musica_juego = None
            self.sonido_game_over = None

    def reproducir_musica_juego(self):
        """Reproduce la música de fondo del juego"""
        if self.musica_juego:
            try:
                pygame.mixer.music.load(self.musica_juego)
                pygame.mixer.music.set_volume(0.7)  # Volumen al 70%
                pygame.mixer.music.play(-1)  # Repetir indefinidamente
            except pygame.error as e:
                print(f"Error al reproducir música del juego: {e}")

    def reproducir_sonido_game_over(self):
        """Reproduce el sonido cuando se pierde"""
        if self.sonido_game_over:
            try:
                pygame.mixer.music.stop()  # Detener música de fondo
                self.sonido_game_over.set_volume(0.8)  # Volumen al 80%
                self.sonido_game_over.play()
            except pygame.error as e:
                print(f"Error al reproducir sonido de game over: {e}")

    def detener_audio(self):
        """Detiene toda la música y sonidos"""
        pygame.mixer.music.stop()
        pygame.mixer.stop()

    def inicializar_juego(self):
        y_suelo = 450
        self.jugador = Jugador(
            100, y_suelo - 50, 50, self.colores["BLANCO"], y_suelo - 50
        )
        self.suelo = Suelo(
            0, y_suelo, 800, 150, self.colores["GRIS"], self.velocidad_juego, 800
        )

        self.puntuacion = 0
        self.juego_terminado = False
        self.juego_ganado = False
        self.obstaculos_restantes_mapa = list(self.mapa_nivel_1_distancias)
        self.obstaculos_activos = []

        self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)
        
        # Reproducir música del juego al iniciar
        self.reproducir_musica_juego()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.esta_ejecutando = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                if not self.juego_terminado and not self.juego_ganado:
                    self.jugador.saltar()
                else:
                    self.inicializar_juego()

    def actualizar_juego(self):
        if self.juego_terminado or self.juego_ganado:
            return

        self.jugador.actualizar()
        self.suelo.actualizar()

        self.distancia_para_siguiente_obstaculo -= self.velocidad_juego
        if self.distancia_para_siguiente_obstaculo <= 0:
            x_nuevo = self.pantalla.get_width()
            self.obstaculos_activos.append(
                Obstaculo(
                    x_nuevo,
                    self.suelo.y,
                    35,
                    self.colores["ROJO"],
                    self.velocidad_juego,
                    800,
                )
            )
            if self.obstaculos_restantes_mapa:
                self.distancia_para_siguiente_obstaculo = (
                    self.obstaculos_restantes_mapa.pop(0)
                )
            else:
                self.distancia_para_siguiente_obstaculo = float("inf")

        for obstaculo in self.obstaculos_activos:
            obstaculo.actualizar()

            if self.jugador.rectangulo.colliderect(
                obstaculo.obtener_rectangulo_colision()
            ):
                self.juego_terminado = True
                # Reproducir sonido de game over
                self.reproducir_sonido_game_over()
                return

            if (
                not obstaculo.fue_superado
                and self.jugador.x > obstaculo.x + obstaculo.ancho
            ):
                obstaculo.fue_superado = True
                self.puntuacion += 1

                if self.puntuacion >= 20:
                    self.juego_ganado = True
                    # Detener música cuando se gana
                    self.detener_audio()
                    return

        self.obstaculos_activos = [
            o for o in self.obstaculos_activos if o.x + o.ancho > 0
        ]

    def dibujar_juego(self):
        self.pantalla.fill(self.colores["AZUL"])
        self.jugador.dibujar(self.pantalla)
        self.suelo.dibujar(self.pantalla)

        for obstaculo in self.obstaculos_activos:
            obstaculo.dibujar(self.pantalla)

        texto_puntuacion = self.fuente_normal.render(
            f"Puntuación: {self.puntuacion}", True, self.colores["BLANCO"]
        )
        self.pantalla.blit(texto_puntuacion, (20, 20))

        if self.juego_terminado or self.juego_ganado:
            superposicion = pygame.Surface((800, 600))
            superposicion.set_alpha(150)
            superposicion.fill((0, 0, 0))
            self.pantalla.blit(superposicion, (0, 0))

            if self.juego_ganado:
                mensaje = "FELICIDADES"
            else:
                mensaje = "Game Over"

            texto_final = self.fuente_grande.render(mensaje, True, (255, 255, 255))
            texto_reiniciar = self.fuente_normal.render(
                "Presione SPACE para continuar", True, (200, 200, 200)
            )

            self.pantalla.blit(texto_final, (400 - texto_final.get_width() // 2, 250))
            self.pantalla.blit(
                texto_reiniciar, (400 - texto_reiniciar.get_width() // 2, 330)
            )

    def ejecutar_juego(self):
        while self.esta_ejecutando:
            self.manejar_eventos()
            if not self.juego_terminado and not self.juego_ganado:
                self.actualizar_juego()
            self.dibujar_juego()
            pygame.display.flip()
            self.reloj.tick(60)
        
        # Detener audio antes de salir
        self.detener_audio()
        pygame.quit()


if __name__ == "__main__":
    Juego().ejecutar_juego()