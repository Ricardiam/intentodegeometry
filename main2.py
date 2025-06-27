import pygame

# Inicializando Pygame
pygame.init()

# --- Clases de Objetos del Juego ---

class ObjetoJuego:
    """Clase base simple para todos los objetos del juego."""

    def __init__(self, posicion_x, posicion_y, ancho, alto, color):
        """
        Inicializa un ObjetoJuego.

        Args:
            posicion_x (int): La coordenada X inicial del objeto.
            posicion_y (int): La coordenada Y inicial del objeto.
            ancho (int): El ancho del objeto.
            alto (int): El alto del objeto.
            color (tuple): El color RGB del objeto.
        """
        self.posicion_x = posicion_x
        self.posicion_y = posicion_y
        self.ancho = ancho
        self.alto = alto
        self.color = color
        # pygame.Rect es un objeto muy útil para manejar posiciones y colisiones.
        self.rectangulo_colision = pygame.Rect(posicion_x, posicion_y, ancho, alto)

    def actualizar_rectangulo(self):
        """Actualiza la posición del rectángulo de colisión para que coincida con la posición del objeto."""
        self.rectangulo_colision.x = self.posicion_x
        self.rectangulo_colision.y = self.posicion_y



class ObjetoMovible(ObjetoJuego):
    """Clase base para objetos que se mueven horizontalmente."""

    def __init__(self, posicion_x, posicion_y, ancho, alto, color, velocidad):
        """
        Inicializa un ObjetoMovible.

        Args:
            velocidad (int): La velocidad de movimiento horizontal del objeto.
        """
        super().__init__(posicion_x, posicion_y, ancho, alto, color)
        self.velocidad = velocidad

    def mover_horizontalmente(self):
        """Mueve el objeto horizontalmente restando su velocidad a su posición X."""
        self.posicion_x -= self.velocidad
        self.actualizar_rectangulo()


class Jugador(ObjetoJuego):
    """Clase que representa al jugador (el cuadrado que salta)."""

    def __init__(self, posicion_x, posicion_y, tamano, color, posicion_y_suelo):
        """
        Inicializa el Jugador.

        Args:
            tamano (int): El tamaño del lado del cuadrado del jugador.
            posicion_y_suelo (int): La coordenada Y que representa la altura del suelo.
        """
        super().__init__(posicion_x, posicion_y, tamano, tamano, color)
        self.posicion_y_suelo = posicion_y_suelo
        self.velocidad_y = 0
        self.gravedad = 1
        self.fuerza_salto = -15  # Negativo porque Y disminuye al subir
        self.esta_saltando = False

    def saltar(self):
        """Inicia el salto del jugador si no está ya en el aire."""
        if not self.esta_saltando:
            self.velocidad_y = self.fuerza_salto
            self.esta_saltando = True

    def actualizar(self):
        """Actualiza la física del jugador, aplicando gravedad y movimiento vertical."""
        # Aplicar gravedad: la velocidad_y aumenta, haciendo que el jugador caiga.
        self.velocidad_y = self.gravedad + self.velocidad_y
        self.posicion_y += self.velocidad_y

        # Verificar si el jugador ha tocado el suelo
        if self.posicion_y >= self.posicion_y_suelo:
            self.posicion_y = self.posicion_y_suelo  # Asegurarse de que esté exactamente en el suelo
            self.velocidad_y = 0  # Detener la caída
            self.esta_saltando = False  # Permitir un nuevo salto

        self.actualizar_rectangulo()

    def dibujar(self, pantalla):
        """Dibuja al jugador como un cuadrado."""
        pygame.draw.rect(pantalla, self.color, (self.posicion_x, self.posicion_y, self.ancho, self.alto))


class Suelo(ObjetoMovible):
    """Clase que representa el suelo del juego, que se mueve y se repite."""

    def __init__(self, posicion_x, posicion_y, ancho, alto, color, velocidad, ancho_pantalla):
        """
        Inicializa el Suelo.

        Args:
            ancho_pantalla (int): El ancho total de la pantalla del juego.
        """
        super().__init__(posicion_x, posicion_y, ancho, alto, color, velocidad)
        self.ancho_pantalla = ancho_pantalla

    def actualizar(self):
        """Actualiza la posición del suelo y lo reinicia si sale de la pantalla."""
        self.mover_horizontalmente()

        # Si el suelo se ha movido completamente fuera de la pantalla por la izquierda,
        # lo reseteamos a la posición inicial (0) para crear un efecto de continuidad.
        if self.posicion_x <= -self.ancho_pantalla:
            self.posicion_x = 0
            self.actualizar_rectangulo()

    def dibujar(self, pantalla):
        """
        Dibuja el suelo. Se dibujan dos rectángulos para crear una ilusión de suelo continuo
        mientras uno se mueve fuera de la pantalla y el otro entra.
        """
        pygame.draw.rect(pantalla, self.color, (self.posicion_x, self.posicion_y, self.ancho, self.alto))
        # Dibujar una segunda parte del suelo justo después de la primera
        pygame.draw.rect(
            pantalla, self.color, (self.posicion_x + self.ancho, self.posicion_y, self.ancho, self.alto)
        )


class Obstaculo(ObjetoMovible):
    """Clase para los obstáculos del juego (triángulos o cuadrados)."""

    def __init__(self, posicion_x, posicion_y, tamano, color, velocidad, ancho_pantalla, forma="triangulo"):
        """
        Inicializa un Obstáculo.

        Args:
            tamano (int): El tamaño (lado) del obstáculo.
            forma (str): La forma del obstáculo ("triangulo" o cualquier otra para cuadrado).
        """
        super().__init__(posicion_x, posicion_y, tamano, tamano, color, velocidad)
        self.ancho_pantalla = ancho_pantalla
        self.forma = forma
        self.superado = False  # Indica si el jugador ya pasó este obstáculo
        self.actualizar_rectangulo() # Asegurarse de que el rectángulo se inicialice correctamente

    def actualizar_rectangulo(self):
        """
        Actualiza el rectángulo de colisión del obstáculo.
        Para un triángulo, el 'rect' debe estar en la base para la colisión.
        """
        self.rectangulo_colision.x = self.posicion_x
        if self.forma == "triangulo":
            # Para un triángulo, la parte superior del triángulo (self.y - self.alto) es su punto más alto,
            # pero queremos que la colisión se detecte desde su base en el suelo.
            # Suponiendo que 'self.y' es la base del triángulo y 'self.alto' es la altura del mismo.
            # El rectángulo de colisión para el triángulo se ajusta para su base.
            self.rectangulo_colision.y = self.posicion_y - self.alto
        else:
            self.rectangulo_colision.y = self.posicion_y

    def actualizar(self):
        """Actualiza la posición del obstáculo y lo reinicia si sale de la pantalla."""
        self.mover_horizontalmente()

        # Si el obstáculo se mueve completamente fuera de la pantalla,
        # lo reposicionamos al extremo derecho para que aparezca de nuevo.
        if self.posicion_x < -self.ancho:
            self.posicion_x = self.ancho_pantalla + 50  # Un poco fuera para que no aparezca de golpe
            self.superado = False  # Se marca como no superado para el nuevo ciclo
            self.actualizar_rectangulo()

    def dibujar(self, pantalla):
        """Dibuja el obstáculo según su forma (triángulo o cuadrado)."""
        if self.forma == "triangulo":
            # Define los vértices del triángulo
            vertice_1 = (self.posicion_x, self.posicion_y)  # Base izquierda
            vertice_2 = (self.posicion_x + self.ancho, self.posicion_y)  # Base derecha
            vertice_3 = (self.posicion_x + self.ancho // 2, self.posicion_y - self.alto)  # Vértice superior
            pygame.draw.polygon(pantalla, self.color, [vertice_1, vertice_2, vertice_3])
        else:
            pygame.draw.rect(pantalla, self.color, self.rectangulo_colision)


class InterfazUsuario:
    """Clase para manejar la interfaz de usuario (texto de puntaje, Game Over, etc.)."""

    def __init__(self, tamano_pantalla):
        """
        Inicializa la InterfazUsuario.

        Args:
            tamano_pantalla (tuple): Una tupla (ancho, alto) de la pantalla.
        """
        self.ancho_pantalla, self.alto_pantalla = tamano_pantalla
        # Cargar fuentes para diferentes tamaños de texto
        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_pequena = pygame.font.Font(None, 36)
        self.fuente_puntaje = pygame.font.Font(None, 48)

        # Renderizar los textos una vez para optimizar (True para anti-aliasing)
        self.texto_fin_juego = self.fuente_grande.render("FIN DEL JUEGO", True, (255, 0, 0))
        self.texto_ganar = self.fuente_grande.render("¡GANASTE!", True, (0, 255, 0))
        self.texto_reiniciar = self.fuente_pequena.render(
            "Presiona ESPACIO para reiniciar", True, (255, 255, 255)
        )

    def dibujar_fin_juego(self, pantalla):
        """Dibuja la pantalla de "FIN DEL JUEGO" con un overlay semitransparente."""
        # Crea una superficie semitransparente para oscurecer el fondo
        superposicion = pygame.Surface((self.ancho_pantalla, self.alto_pantalla))
        superposicion.set_alpha(128)  # Establece la transparencia (0-255)
        superposicion.fill((0, 0, 0))  # Rellena con negro
        pantalla.blit(superposicion, (0, 0)) # Dibuja el overlay en la pantalla

        # Obtiene los rectángulos de los textos para centrarlos
        rect_fin_juego = self.texto_fin_juego.get_rect(
            center=(self.ancho_pantalla // 2, self.alto_pantalla // 2 - 50)
        )
        rect_reiniciar = self.texto_reiniciar.get_rect(
            center=(self.ancho_pantalla // 2, self.alto_pantalla // 2 + 50)
        )

        # Dibuja los textos en la pantalla
        pantalla.blit(self.texto_fin_juego, rect_fin_juego)
        pantalla.blit(self.texto_reiniciar, rect_reiniciar)

    def dibujar_puntaje(self, pantalla, puntaje):
        """Dibuja el puntaje actual en la parte superior izquierda de la pantalla."""
        texto_puntaje = self.fuente_puntaje.render(f"Puntaje: {puntaje}", True, (255, 255, 255))
        pantalla.blit(texto_puntaje, (20, 20))

    def dibujar_ganar(self, pantalla):
        """Dibuja la pantalla de "¡GANASTE!" con un overlay semitransparente."""
        # Similar a la pantalla de Game Over
        superposicion = pygame.Surface((self.ancho_pantalla, self.alto_pantalla))
        superposicion.set_alpha(128)
        superposicion.fill((0, 0, 0))
        pantalla.blit(superposicion, (0, 0))

        rect_ganar = self.texto_ganar.get_rect(
            center=(self.ancho_pantalla // 2, self.alto_pantalla // 2 - 50)
        )
        rect_reiniciar = self.texto_reiniciar.get_rect(
            center=(self.ancho_pantalla // 2, self.alto_pantalla // 2 + 50)
        )

        pantalla.blit(self.texto_ganar, rect_ganar)
        pantalla.blit(self.texto_reiniciar, rect_reiniciar)


# --- Clase Principal del Juego ---

class Juego:
    """Clase principal que maneja toda la lógica y el estado del juego."""

    def __init__(self):
        """Inicializa la configuración principal del juego."""
        self.tamano_pantalla = (800, 600)
        self.pantalla = pygame.display.set_mode(self.tamano_pantalla)
        pygame.display.set_caption("Geometry Dash") # Establece el título de la ventana
        self.reloj = pygame.time.Clock() # Ayuda a controlar la velocidad de fotogramas

        # Definición de colores útiles en el juego
        self.COLORES = {
            "NEGRO": (0, 0, 0),
            "BLANCO": (255, 255, 255),
            "ROJO": (255, 0, 0),
            "AZUL_CLARO": (73, 115, 255),
            "GRIS_OSCURO": (50, 50, 50),
        }

        self.velocidad_juego = 10
        self.juego_terminado = False # Bandera para saber si el juego ha terminado (Game Over)
        self.juego_ganado = False    # Bandera para saber si el jugador ha ganado
        self.ejecutando = True       # Bandera principal del bucle del juego
        self.puntaje = 0

        self.inicializar_objetos_juego()
        self.interfaz_usuario = InterfazUsuario(self.tamano_pantalla)

    def inicializar_objetos_juego(self):
        """Inicializa o reinicializa todos los objetos que participan en el juego."""
        altura_suelo = 150
        posicion_y_suelo = self.tamano_pantalla[1] - altura_suelo

        tamano_jugador = 50
        # La posición Y del jugador es la del suelo menos su tamaño para que esté "sobre" el suelo
        posicion_y_jugador_suelo = posicion_y_suelo - tamano_jugador
        self.jugador = Jugador(
            100, posicion_y_jugador_suelo, tamano_jugador, self.COLORES["BLANCO"], posicion_y_jugador_suelo
        )

        self.suelo = Suelo(
            0,
            posicion_y_suelo,
            self.tamano_pantalla[0], # El ancho del suelo es el de la pantalla
            altura_suelo,
            self.COLORES["GRIS_OSCURO"],
            self.velocidad_juego,
            self.tamano_pantalla[0],
        )

        tamano_obstaculo = 35
        self.obstaculo = Obstaculo(
            self.tamano_pantalla[0] + 50, # Iniciar el obstáculo un poco fuera de la pantalla
            posicion_y_suelo, # La base del obstáculo está en la posición Y del suelo
            tamano_obstaculo,
            self.COLORES["ROJO"],
            self.velocidad_juego,
            self.tamano_pantalla[0],
            forma="triangulo", # Podemos especificar la forma aquí
        )

    def manejar_eventos(self):
        """Maneja todos los eventos de entrada del usuario, como cerrar la ventana o presionar teclas."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False # Si el usuario cierra la ventana, se detiene el juego

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    # Si el juego no ha terminado ni se ha ganado, el espacio hace que el jugador salte.
                    # Si el juego ha terminado o se ha ganado, el espacio lo reinicia.
                    if not self.juego_terminado and not self.juego_ganado:
                        self.jugador.saltar()
                    elif self.juego_terminado or self.juego_ganado:
                        self.reiniciar_juego()

    def reiniciar_juego(self):
        """Restablece el estado del juego a sus valores iniciales para empezar una nueva partida."""
        self.juego_terminado = False
        self.juego_ganado = False
        self.puntaje = 0
        self.inicializar_objetos_juego() # Reinicializa las posiciones de los objetos

    def actualizar_logica_juego(self):
        """Actualiza el estado de todos los objetos del juego y la lógica de colisiones/puntaje."""
        if not self.juego_terminado and not self.juego_ganado:
            self.jugador.actualizar()
            self.suelo.actualizar()
            self.obstaculo.actualizar()

            # Lógica para incrementar el puntaje cuando el jugador pasa un obstáculo
            if (
                not self.obstaculo.superado # Solo si el obstáculo no ha sido superado antes
                and self.jugador.posicion_x > self.obstaculo.posicion_x + self.obstaculo.ancho
            ):
                self.obstaculo.superado = True # Marca el obstáculo como superado
                self.puntaje += 1

                if self.puntaje >= 10: # Condición de victoria
                    self.juego_ganado = True

            # Detección de colisiones entre el jugador y el obstáculo
            if self.jugador.rectangulo_colision.colliderect(self.obstaculo.rectangulo_colision):
                self.juego_terminado = True # Si hay colisión, el juego termina

    def dibujar_todo(self):
        """Dibuja todos los elementos gráficos en la pantalla en cada fotograma."""
        self.pantalla.fill(self.COLORES["AZUL_CLARO"]) # Rellena el fondo con el color del cielo

        # Dibuja los objetos del juego
        self.jugador.dibujar(self.pantalla)
        self.suelo.dibujar(self.pantalla)
        self.obstaculo.dibujar(self.pantalla)

        # Dibuja el puntaje
        self.interfaz_usuario.dibujar_puntaje(self.pantalla, self.puntaje)

        # Si el juego ha terminado o se ha ganado, dibuja las pantallas correspondientes
        if self.juego_terminado:
            self.interfaz_usuario.dibujar_fin_juego(self.pantalla)
        elif self.juego_ganado:
            self.interfaz_usuario.dibujar_ganar(self.pantalla)

    def ejecutar(self):
        """Bucle principal del juego. Aquí se gestiona el flujo de eventos, actualizaciones y dibujos."""
        while self.ejecutando:
            self.manejar_eventos()        # Procesa las entradas del usuario
            self.actualizar_logica_juego() # Actualiza el estado del juego
            self.dibujar_todo()            # Dibuja los elementos en pantalla

            pygame.display.flip()       # Actualiza la pantalla completa para mostrar los cambios
            self.reloj.tick(60)         # Limita la velocidad de fotogramas a 60 FPS

        pygame.quit() # Cuando el bucle termina, cierra Pygame
        print("Juego cerrado exitosamente")


# Ejecutar el juego si el script se ejecuta directamente
if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()