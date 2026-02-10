from .errors import GameConfigError

class GameMetadata:
    """Contenedor de metadatos del juego con validación automática."""
    def __init__(self, title: str, description: str, authors: list[str], group_number: int):
        self._validate(title, description, authors, group_number)
        self._title = title
        self._description = description
        self._authors = authors
        self._group_number = group_number

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def authors(self) -> list[str]:
        return self._authors.copy()

    @property
    def group_number(self) -> int:
        return self._group_number

    def _validate(self, title, description, authors, group_number) -> None:
        """Verifica tipos y contenido de los datos antes de la asignación."""
            
        if not isinstance(title, str) or not title.strip():
            raise GameConfigError("Metadata: 'title' debe ser un texto no vacío.")
        if not isinstance(description, str) or not description.strip():
            raise GameConfigError("Metadata: 'description' debe ser un texto no vacío.")
        if not isinstance(authors, list) or not authors:
            raise GameConfigError("Metadata: 'authors' debe ser una lista con al menos un nombre.")
        if not all(isinstance(a, str) and a.strip() for a in authors):
            raise GameConfigError("Metadata: Todos los autores deben ser textos no vacíos.")
        if not isinstance(group_number, int) or group_number < 1:
            raise GameConfigError("Metadata: 'group_number' debe ser un número entero positivo.")