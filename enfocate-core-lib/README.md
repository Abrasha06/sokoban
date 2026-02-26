# Enfócate+ Core Lib 🧠

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Pygame Version](https://img.shields.io/badge/pygame-2.6.0-green)
![Status](https://img.shields.io/badge/status-stable-success)

> **Core Library** para el desarrollo e integración de minijuegos en el ecosistema terapéutico **Enfócate+**.

---

## 📖 Descripción del Proyecto

**Enfócate+** es una plataforma de software que cuenta con juegos diseñados para la estimulación cognitiva y mejora de la concentración en personas con TDAH.

Esta librería (`enfocate-core-lib`) provee la arquitectura base, interfaces y estándares técnicos necesarios para que los 11 grupos de desarrollo de la asignatura **Objetos y Abstracción de Datos (OAD)** integren sus proyectos en el Motor Central de manera unificada.

### 🏛️ Arquitectura Técnica
El sistema implementa un patrón de **Inversión de Control (IoC)**:
1.  **El Motor (Core):** Gestiona el ciclo de vida de la aplicación, el bucle principal (Game Loop) y la ventana de renderizado.
2.  **Los Juegos (Plugins):** Son módulos pasivos que heredan de `GameBase` y reciben inyección de dependencias (Superficie y Delta Time) desde el motor.

---

## 📂 Estructura del Repositorio

El proyecto sigue el estándar **Src Layout** para garantizar la limpieza del espacio de nombres:

```text
enfocate-core-lib/
├── pyproject.toml       # Configuración de empaquetado y dependencias.
├── README.md            # Documentación oficial.
└── src/
    └── enfocate/        # Paquete importable.
        ├── __init__.py  # Exportación pública.
        ├── errors.py    # Excepciones personalizadas de validación.
        ├── interface.py # Clase Base Abstracta (Contrato de Interfaz).
        ├── metadata.py  # Clase de validación de metadatos (GameMetadata).
        └── settings.py  # Constantes globales (Resolución, Paleta de Colores).
```

---

## 🛠️ Instalación y Configuración
Para desarrollar un juego compatible, se recomienda instalar la librería en modo **editable**. Esto permite trabajar con las importaciones reales sin compilar el paquete constantemente.

### Requisitos Previos
Antes de instalar, asegúrate de tener:

- **Python 3.11+** instalado ([Descargar aquí](https://www.python.org/downloads/))
- **pip** actualizado: `python -m pip install --upgrade pip`

### Paso 1: Descargar
Clona este repositorio o descarga la carpeta en tu computadora.

```bash
git clone https://github.com/alecsoc/enfocate-core-lib.git
cd enfocate-core-lib
```

### Paso 2: Instalar en modo desarrollador
Abre la terminal en la carpeta raíz del proyecto (donde está el archivo pyproject.toml) y ejecuta:

```bash
pip install -e .
```

> ⚠️ IMPORTANTE: No olvides el punto . al final del comando. Eso le dice a Python "instala la carpeta actual".

Si todo salió bien, verás un mensaje de éxito. Ahora puedes usar `import enfocate` en cualquier archivo de tu PC.

---

## 🚀 Guía de Implementación
### 💻 Punto de Entrada (`game.py`)
Para que un juego sea compatible con el ecosistema **Enfócate+**, debe heredar de `GameBase` y proporcionar una instancia de `GameMetadata` en su constructor. Ejemplo:

```py
import pygame
from enfocate import GameBase, GameMetadata, COLORS

class MiJuego(GameBase):
    def __init__(self) -> None:
        # 1. Registro de información técnica del juego
        meta = GameMetadata(
            title="Nombre Del Juego",
            description="Breve descripción.",
            authors=["Nombre Apellido 1", "Nombre Apellido 2"],
            group_number=3
        )
        
        # 2. Inyección de metadatos al Core
        super().__init__(meta)
        
        # 3. Inicialización de estado interno
        self.puntuacion = 0

    def on_start(self):
        """Carga de recursos dinámicos (assets)."""
        pass

    def update(self, dt: float):
        """Actualización de lógica física y estados (dt = delta time)."""
        pass

    def draw(self):
        """Renderizado en la superficie inyectada por el motor."""
        self.surface.fill(COLORS["carbon_oscuro"])
```

---

## 🧪 3. ¿Cómo pruebo mi juego?
La librería incluye un entorno de ejecución independiente para que cada grupo pueda validar su lógica de forma aislada sin necesidad del Motor Central.

Para ejecutar el simulador, añada el siguiente punto de entrada al final de su archivo de juego:

```py
if __name__ == "__main__":
    # Ejecuta el mini-motor integrado bajo los estándares del Core
    MiJuego().run_preview()
```

Ejecución vía terminal:

```bash
python game.py
```

O si usa un archivo aparte `main.py`, realícelo de la siguiente manera (recomendación):

```py
from src.game import MiJuego

if __name__ == "__main__":
    # Se instancia y se corre. 
    # El Core ya sabe qué hacer porque la lógica está en la base.
    game = MiJuego()
    game.run_preview()
```

Ejecución vía terminal:

```bash
python main.py
```

**Si tu juego se abre y se mueve aquí, funcionará perfectamente en la entrega final.**

---

## 👥 Equipo de Integración

- Alejandro Capriles

- Alexandro Núñez

- Anelissa Espín

- Gabriel Garantón

- José Aguilera

- Leonardo Di Giorgio

- Luis Lameda

- Odett Sayegh

---

© 2026 Universidad de Oriente - Proyecto Académico de la cátedra Objetos y Abstracción de Datos (OAD)