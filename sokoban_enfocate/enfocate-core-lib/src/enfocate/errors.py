class GameConfigError(Exception):
    """Se lanza cuando la configuración del juego (metadata) está mal formada."""
    pass

class GameResourcesError(Exception):
    """Se lanza si el juego intenta cargar recursos que no existen."""
    pass