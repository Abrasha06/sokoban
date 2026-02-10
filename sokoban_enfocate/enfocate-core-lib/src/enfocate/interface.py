import pygame
from abc import ABC, abstractmethod
from typing import List, final
from .metadata import GameMetadata
from .settings import SCREEN_SIZE, FPS, COLORS

class GameBase(ABC):
    """
    Clase base para la librería de Enfócate+. 
    Gestiona el ciclo de vida y la inyección de dependencias del motor.
    """

    def __init__(self, metadata: GameMetadata) -> None:
        """
        Inicializa el juego con sus metadatos obligatorios.

        Args:
            metadata (GameMetadata): Instancia validada con la información 
                                     del juego (título, autores, grupo).
        
        Example:
            >>> meta = GameMetadata("Mi Juego", "Desc...", ["Autor"], 1)
            >>> super().__init__(meta)
        """
        self.metadata = metadata
        self._running: bool = False
        self._surface: pygame.Surface | None = None

    # --- MÉTODOS ABSTRACTOS (OBLIGATORIOS A HEREDAR) ---

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Ejecuta la lógica del juego por frame.

        Parameters
        ----------
        dt
            Delta time (segundos transcurridos desde el último frame).
            Úsalo para multiplicar velocidades (ej. x += vel * dt).
        """
        pass

    @abstractmethod
    def draw(self) -> None:
        """
        Renderiza los elementos en pantalla.
        
        Notes
        -----
        Se usa `self.surface` para dibujar. No se debe utilizar `pygame.display.update()`;
        el motor ya se encarga de eso.
        """
        pass
    
    # --- HOOKS (OPCIONALES) ---

    def on_start(self) -> None:
        """Se ejecuta una única vez al iniciar el juego (carga de recursos)."""
        pass

    def on_stop(self) -> None:
        """Se ejecuta al cerrar el juego o volver al menú (limpieza)."""
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """
        Procesa eventos crudos de Pygame (teclado, mouse).

        Parameters
        ----------
        events
            Lista de eventos capturados en el frame actual.
        """
        pass

    # --- MÉTODOS DEL MOTOR (FINAL) ---
    
    @final
    def _inject_context(self, surface: pygame.Surface) -> None:
        """Inyecta la dependencia de pantalla e inicia el estado (NO TOCAR)."""
        if self._running:
            raise RuntimeError("El juego ya está en ejecución.")
        self._surface = surface
        self._running = True
        self.on_start()

    @final
    def _stop_context(self) -> None:
        """Detiene el estado del juego (NO TOCAR)."""
        self._running = False
        self.on_stop()

    @property
    def surface(self) -> pygame.Surface:
        """La superficie de dibujo proporcionada por el motor."""
        if self._surface is None:
            raise RuntimeError("Surface no disponible. ¿Olvidaste llamar a super().start()?")
        return self._surface
    
    # --- RUNNER INDEPENDIENTE ---

    def run_preview(self) -> None:
            """Simulador de Motor para pruebas unitarias de integración."""
            pygame.init()
            screen = pygame.display.set_mode(SCREEN_SIZE)
            pygame.display.set_caption(f"OAD-Runner: {self.metadata.title}")
            clock = pygame.time.Clock()
            
            self._inject_context(screen)

            try:
                while self._running:
                    events = pygame.event.get()
                    for event in events:
                        if event.type == pygame.QUIT:
                            self._stop_context()
                            break

                    if self._running:
                        self.handle_events(events)

                    if self._running:
                        dt = clock.tick(FPS) / 1000.0
                        self.update(dt)

                    if self._running:
                        screen.fill(COLORS.get("carbon_oscuro", (35, 35, 40)))
                        self.draw()
                        pygame.display.flip()
            finally:
                if self._running:
                    self._stop_context()
                pygame.quit()