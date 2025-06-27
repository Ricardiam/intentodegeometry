import pygame

pygame.init()
pygame.mixer.init()

# ----------------------------- Cargar imágenes de fondo -----------------------------
FONDO_NIVEL_1 = pygame.transform.scale(pygame.image.load("bg.png"), (800, 600))
FONDO_NIVEL_2 = pygame.transform.scale(pygame.image.load("nivel2.jpeg"), (800, 600))


# ----------------------------- Clases base -----------------------------

class ObjetoJuego:
    def __init__(self, x, y, ancho, alto, color):
        self.x, self.y, self.ancho, self.alto, self.color = x, y, ancho, alto, color
        self.rectangulo = pygame.Rect(x, y, ancho, alto)

    def actualizar_rectangulo(self):
        self.rectangulo.x, self.rectangulo.y = self.x, self.y

class Jugador(ObjetoJuego):
    def __init__(self, x, y, tamaño, color, y_suelo):
        super().__init__(x, y, tamaño, tamaño, color)
        self.y_suelo_original = y_suelo
        self.y_suelo = y_suelo
        self.velocidad_y = 0
        self.esta_saltando = False

    def saltar(self):
        if not self.esta_saltando:
            self.velocidad_y = -15
            self.esta_saltando = True

    def actualizar(self, plataformas_activas=None):
        self.velocidad_y += 1
        self.y += self.velocidad_y

        if plataformas_activas:
            for plataforma in plataformas_activas:
                if (self.velocidad_y >= 0 and 
                    self.rectangulo.colliderect(plataforma.rect) and 
                    self.y < plataforma.rect.y):
                    self.y = plataforma.rect.y - self.alto
                    self.velocidad_y = 0
                    self.esta_saltando = False
                    self.actualizar_rectangulo()
                    return

        if self.y >= self.y_suelo_original:
            self.y = self.y_suelo_original
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

class PlataformaMovil:
    def __init__(self, x, y, ancho, alto, color, velocidad):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = color
        self.velocidad = velocidad

    def actualizar(self):
        self.rect.x -= self.velocidad

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)


# ----------------------------- Clase Menu -----------------------------

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


# ----------------------------- Clase principal -----------------------------

class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Geometry Dash")
        self.reloj = pygame.time.Clock()
        self.nivel_actual = 1

        self.colores = {
            "AZUL": (0, 168, 232),
            "BLANCO": (255, 255, 255),
            "ROJO": (255, 0, 0),
            "VERDE": (61, 133, 0),
        }

        self.velocidad_juego = 10
        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_normal = pygame.font.Font(None, 48)

        self.mapa_nivel_1_distancias = [600] * 20

        self.menu = Menu(self.pantalla, self.fuente_grande, self.fuente_normal, self.colores)

        self.esta_ejecutando = True
        self.en_menu = True

        self.fondo = FONDO_NIVEL_1

        self.cargar_audio()

    def cargar_audio(self):
        self.musica_juego = "bossfight-Vextron.mp3"
        self.sonido_win = pygame.mixer.Sound("win.mp3")
        self.sonido_lose = pygame.mixer.Sound("lose.mp3")

    def reproducir_musica_juego(self):
        pygame.mixer.music.load(self.musica_juego)
        pygame.mixer.music.set_volume(0.04)
        pygame.mixer.music.play(-1)

    def reproducir_sonido_game_over(self):
        pygame.mixer.music.stop()
        self.sonido_lose.set_volume(0.1)
        self.sonido_lose.play()

    def reproducir_sonido_victoria(self):
        pygame.mixer.music.stop()
        self.sonido_win.set_volume(0.1)
        self.sonido_win.play()

    def detener_audio(self):
        pygame.mixer.music.stop()

    def inicializar_juego(self):
        y_suelo = 450
        self.jugador = Jugador(100, y_suelo - 50, 50, self.colores["BLANCO"], y_suelo - 50)
        self.suelo = Suelo(0, y_suelo, 800, 150, self.colores["VERDE"], self.velocidad_juego, 800)

        self.puntuacion = 0
        self.juego_terminado = False
        self.juego_ganado = False

        self.obstaculos_restantes_mapa = list(
            self.mapa_nivel_1_distancias if self.nivel_actual == 1 else [600] * 50
        )
        self.obstaculos_activos = []
        self.plataformas_activas = []
        self.contador_plataforma = 0
        self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)

        self.fondo = FONDO_NIVEL_1 if self.nivel_actual == 1 else FONDO_NIVEL_2

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

        # Actualizar jugador con plataformas si es nivel 2
        plataformas_para_colision = self.plataformas_activas if self.nivel_actual == 2 else None
        self.jugador.actualizar(plataformas_para_colision)

        # Actualizar suelo
        self.suelo.actualizar()

        # Generar obstáculos
        self.distancia_para_siguiente_obstaculo -= self.velocidad_juego
        if self.distancia_para_siguiente_obstaculo <= 0:
            self.obstaculos_activos.append(
                Obstaculo(800, self.suelo.y, 35, self.colores["ROJO"], self.velocidad_juego, 800)
            )
            if self.obstaculos_restantes_mapa:
                self.distancia_para_siguiente_obstaculo = self.obstaculos_restantes_mapa.pop(0)
            else:
                self.distancia_para_siguiente_obstaculo = float("inf")

        # Actualizar obstáculos y verificar colisiones
        for obstaculo in self.obstaculos_activos:
            obstaculo.actualizar()
            if self.jugador.rectangulo.colliderect(obstaculo.obtener_rectangulo_colision()):
                self.juego_terminado = True
                # Reproducir sonido de game over
                self.reproducir_sonido_game_over()
                return
            if not obstaculo.fue_superado and self.jugador.x > obstaculo.x + obstaculo.ancho:
                obstaculo.fue_superado = True
                self.puntuacion += 1

        # Verificar cambio de nivel
        if self.puntuacion == 10 and self.nivel_actual == 1:
            self.nivel_actual = 2
            self.inicializar_juego()
            return

        # Verificar victoria
        if self.puntuacion >= 20 and self.nivel_actual == 2:
            self.juego_ganado = True
            self.reproducir_sonido_victoria()
            return

        # Limpiar obstáculos fuera de pantalla
        self.obstaculos_activos = [o for o in self.obstaculos_activos if o.x + o.ancho > 0]

        # ------- Lógica de plataformas para nivel 2 -------
        if self.nivel_actual == 2:
            # Actualizar plataformas existentes
            for plataforma in self.plataformas_activas:
                plataforma.actualizar()
            
            # Eliminar plataformas que salieron de pantalla
            self.plataformas_activas = [p for p in self.plataformas_activas if p.rect.right > 0]

            # Generar nuevas plataformas cada cierto tiempo
            self.contador_plataforma += 1
            if self.contador_plataforma >= 180:  # Cada 3 segundos aprox (60 FPS * 3)
                self.contador_plataforma = 0
                # Alternar altura de plataformas (más bajas para ser alcanzables)
                y_plataforma = 350 if len(self.plataformas_activas) % 2 == 0 else 320
                nueva_plataforma = PlataformaMovil(800, y_plataforma, 180, 25, self.colores["AZUL"], self.velocidad_juego)
                self.plataformas_activas.append(nueva_plataforma)

    def dibujar_juego(self):
        self.pantalla.blit(self.fondo, (0, 0))
        
        # Dibujar suelo
        self.suelo.dibujar(self.pantalla)
        
        # Dibujar plataformas (nivel 2)
        for plataforma in self.plataformas_activas:
            plataforma.dibujar(self.pantalla)
        
        # Dibujar obstáculos
        for obstaculo in self.obstaculos_activos:
            obstaculo.dibujar(self.pantalla)
        
        # Dibujar jugador
        self.jugador.dibujar(self.pantalla)

        # UI
        texto_puntuacion = self.fuente_normal.render(f"Puntuación: {self.puntuacion}", True, self.colores["BLANCO"])
        texto_nivel = self.fuente_normal.render(f"Nivel: {self.nivel_actual}", True, self.colores["BLANCO"])
        self.pantalla.blit(texto_puntuacion, (20, 20))
        self.pantalla.blit(texto_nivel, (20, 60))

        # Pantalla de fin de juego
        if self.juego_terminado or self.juego_ganado:
            superposicion = pygame.Surface((800, 600))
            superposicion.set_alpha(150)
            superposicion.fill((0, 0, 0))
            self.pantalla.blit(superposicion, (0, 0))
            
            mensaje = "¡FELICIDADES!" if self.juego_ganado else "Game Over"
            color_mensaje = (0, 255, 0) if self.juego_ganado else (255, 0, 0)
            
            texto_final = self.fuente_grande.render(mensaje, True, color_mensaje)
            texto_puntuacion_final = self.fuente_normal.render(f"Puntuación final: {self.puntuacion}", True, (255, 255, 255))
            texto_reiniciar = self.fuente_normal.render("Presione SPACE para reiniciar", True, (200, 200, 200))
            
            self.pantalla.blit(texto_final, (400 - texto_final.get_width() // 2, 200))
            self.pantalla.blit(texto_puntuacion_final, (400 - texto_puntuacion_final.get_width() // 2, 280))
            self.pantalla.blit(texto_reiniciar, (400 - texto_reiniciar.get_width() // 2, 330))
    


    def ejecutar_juego(self):
        while self.esta_ejecutando:
            if self.en_menu:
                eventos = pygame.event.get()
                accion = self.menu.manejar_eventos(eventos)
                if accion == "INICIAR_JUEGO":
                    self.inicializar_juego()
                    self.en_menu = False
                elif accion == "SALIR":
                    self.esta_ejecutando = False
                else:
                    mouse_pos = pygame.mouse.get_pos()
                    self.menu.dibujar(self.fondo, mouse_pos)
                    pygame.display.flip()
                    self.reloj.tick(60)
            else:
                self.manejar_eventos()
                self.actualizar_juego()
                self.dibujar_juego()
                pygame.display.flip()
                self.reloj.tick(60)

        self.detener_audio()
        pygame.quit()


if __name__ == "__main__":
    Juego().ejecutar_juego()