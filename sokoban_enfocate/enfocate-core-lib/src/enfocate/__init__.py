"""
Core Library para Enfócate+.
"""
from .metadata import GameMetadata
from .interface import GameBase
from .settings import COLORS, SCREEN_SIZE, FPS
from .errors import GameConfigError, GameResourcesError

__all__ = [
    "GameBase", "GameMetadata", 
    "COLORS", "SCREEN_SIZE", "FPS", 
    "GameConfigError", "GameResourcesError"
]