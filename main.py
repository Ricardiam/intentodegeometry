import pygame
import abc

# Inicializando pygame
pygame.init()

# Clase base para objetos del juego
class GameObject(abc.ABC):
    """Clase abstracta base para todos los objetos del juego"""
    
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
    
    def update_rect(self):
        """Actualiza el rectángulo de colisión"""
        self.rect.x = self.x
        self.rect.y = self.y
    
    @abc.abstractmethod
    def update(self, *args):
        """Método abstracto para actualizar el objeto"""
        pass
    
    @abc.abstractmethod
    def draw(self, screen):
        """Método abstracto para dibujar el objeto"""
        pass

# Clase para objetos físicos que se mueven horizontalmente
class MovableObject(GameObject):
    """Clase base para objetos que se mueven horizontalmente"""
    
    def __init__(self, x, y, width, height, color, speed):
        super().__init__(x, y, width, height, color)
        self.speed = speed
    
    def move_horizontal(self):
        """Mueve el objeto horizontalmente"""
        self.x -= self.speed
        self.update_rect()

# Clase del jugador
class Player(GameObject):
    """Clase que representa al jugador"""
    
    def __init__(self, x, y, size, color, ground_y):
        super().__init__(x, y, size, size, color)
        self.ground_y = ground_y
        self.velocity_y = 0
        self.gravity = 1
        self.jump_force = -15
        self.is_jumping = False
    
    def jump(self):
        """Hace que el jugador salte"""
        if not self.is_jumping:
            self.velocity_y = self.jump_force
            self.is_jumping = True
    
    def update(self):
        """Actualiza la física del jugador"""
        # Aplicar gravedad
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        
        # Verificar si está en el suelo
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.velocity_y = 0
            self.is_jumping = False
        
        self.update_rect()
    
    def draw(self, screen):
        """Dibuja al jugador como un cuadrado"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Clase del suelo
class Ground(MovableObject):
    """Clase que representa el suelo del juego"""
    
    def __init__(self, x, y, width, height, color, speed, screen_width):
        super().__init__(x, y, width, height, color, speed)
        self.screen_width = screen_width
    
    def update(self):
        """Actualiza la posición del suelo"""
        self.move_horizontal()
        
        # Si el suelo sale de la pantalla, reiniciar posición
        if self.x <= -self.screen_width:
            self.x = 0
            self.update_rect()
    
    def draw(self, screen):
        """Dibuja el suelo (dos rectángulos para continuidad)"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.color, (self.x + self.width, self.y, self.width, self.height))

# Clase base para obstáculos
class Obstacle(MovableObject):
    """Clase base para obstáculos"""
    
    def __init__(self, x, y, size, color, speed, screen_width):
        super().__init__(x, y, size, size, color, speed)
        self.screen_width = screen_width
    
    def update(self):
        """Actualiza la posición del obstáculo"""
        self.move_horizontal()
        
        # Si el obstáculo sale de la pantalla, reiniciar posición
        if self.x < -self.width:
            self.x = self.screen_width + 50
            self.update_rect()

# Clase para obstáculos triangulares
class TriangleObstacle(Obstacle):
    """Obstáculo en forma de triángulo"""
    
    def __init__(self, x, y, size, color, speed, screen_width):
        super().__init__(x, y, size, color, speed, screen_width)
        # Ajustar rectángulo de colisión para el triángulo
        self.rect = pygame.Rect(x, y - size, size, size)
        self.passed = False  # LÍNEA AÑADIDA: Flag para saber si ya pasó el obstáculo
    
    def update_rect(self):
        """Actualiza el rectángulo de colisión del triángulo"""
        self.rect.x = self.x
        self.rect.y = self.y - self.height
    
    def update(self):
        """Actualiza la posición del obstáculo"""
        self.move_horizontal()
        
        # Si el obstáculo sale de la pantalla, reiniciar posición
        if self.x < -self.width:
            self.x = self.screen_width + 50
            self.passed = False  # LÍNEA AÑADIDA: Resetear flag cuando reaparece
            self.update_rect()
    
    def draw(self, screen):
        """Dibuja el obstáculo como un triángulo"""
        vertex_1 = (self.x, self.y)
        vertex_2 = (self.x + self.width, self.y)
        vertex_3 = (self.x + self.width // 2, self.y - self.height)
        pygame.draw.polygon(screen, self.color, [vertex_1, vertex_2, vertex_3])

# Clase para la interfaz de usuario
class UI:
    """Clase para manejar la interfaz de usuario"""
    
    def __init__(self, screen_size):
        self.screen_width, self.screen_height = screen_size
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 48)  # LÍNEA MODIFICADA: Fuente para el score
        
        # Textos predefinidos
        self.game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        self.restart_text = self.small_font.render("Presiona SPACE para reiniciar", True, (255, 255, 255))
    
    def draw_game_over(self, screen):
        """Dibuja la pantalla de game over"""
        # Crear superficie semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Centrar textos
        game_over_rect = self.game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        restart_rect = self.restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
        
        screen.blit(self.game_over_text, game_over_rect)
        screen.blit(self.restart_text, restart_rect)
    
    def draw_score(self, screen, score):  # LÍNEA AÑADIDA: Método para dibujar el score
        """Dibuja el puntaje en la parte superior izquierda"""
        score_text = self.score_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

# Clase principal del juego
class Game:
    """Clase principal que maneja todo el juego"""
    
    def __init__(self):
        # Configuración de la pantalla
        self.screen_size = (800, 600)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Geometry Hash")
        self.clock = pygame.time.Clock()
        
        # Colores
        self.COLORS = {
            'BLACK': (0, 0, 0),
            'WHITE': (255, 255, 255),
            'RED': (255, 0, 0),
            'BLUE_LIGHT': (73, 115, 255),
            'DARK_GRAY': (50, 50, 50)
        }
        
        # Configuración del juego
        self.game_speed = 5
        self.game_over = False
        self.running = True
        self.score = 0  # LÍNEA AÑADIDA: Variable para el puntaje
        
        # Inicializar objetos
        self.init_game_objects()
        
        # UI
        self.ui = UI(self.screen_size)
    
    def init_game_objects(self):
        """Inicializa todos los objetos del juego"""
        # Configuración del suelo
        ground_height = 150
        ground_y = self.screen_size[1] - ground_height
        
        # Crear jugador
        player_size = 50
        player_ground_y = ground_y - player_size
        self.player = Player(100, player_ground_y, player_size, self.COLORS['WHITE'], player_ground_y)
        
        # Crear suelo
        self.ground = Ground(0, ground_y, self.screen_size[0], ground_height, 
                           self.COLORS['DARK_GRAY'], self.game_speed, self.screen_size[0])
        
        # Crear obstáculo
        obstacle_size = 35
        self.obstacle = TriangleObstacle(self.screen_size[0] + 50, ground_y, obstacle_size, 
                                       self.COLORS['RED'], self.game_speed, self.screen_size[0])
    
    def handle_events(self):
        """Maneja todos los eventos del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over:
                        self.player.jump()
                    else:
                        self.restart_game()
    
    def restart_game(self):
        """Reinicia el juego"""
        self.game_over = False
        self.score = 0  # LÍNEA AÑADIDA: Resetear el puntaje
        self.init_game_objects()
    
    def update_game_logic(self):
        """Actualiza la lógica del juego"""
        if not self.game_over:
            # Actualizar objetos
            self.player.update()
            self.ground.update()
            self.obstacle.update()
            
            # LÍNEAS AÑADIDAS: Verificar si el jugador pasó el obstáculo
            if (not self.obstacle.passed and 
                self.player.x > self.obstacle.x + self.obstacle.width):
                self.obstacle.passed = True
                self.score += 1
            
            # Verificar colisiones
            if self.player.rect.colliderect(self.obstacle.rect):
                self.game_over = True
    
    def draw_everything(self):
        """Dibuja todos los elementos en pantalla"""
        # Fondo
        self.screen.fill(self.COLORS['BLUE_LIGHT'])
        
        # Dibujar objetos
        self.player.draw(self.screen)
        self.ground.draw(self.screen)
        self.obstacle.draw(self.screen)
        
        # LÍNEA AÑADIDA: Dibujar el puntaje
        self.ui.draw_score(self.screen, self.score)
        
        # Dibujar UI si hay game over
        if self.game_over:
            self.ui.draw_game_over(self.screen)
    
    def run(self):
        """Bucle principal del juego"""
        while self.running:
            self.handle_events()
            self.update_game_logic()
            self.draw_everything()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        print("Juego cerrado exitosamente")

# Ejecutar el juego
if __name__ == "__main__":
    game = Game()
    game.run()