# scenes/models/__init__.py
# ==============================================================================
# МОДЕЛИ ПРИЛОЖЕНИЯ SCENES
#
# После рефакторинга осталось 3 модели:
#   World        — мир (содержит чанки, объекты, настройки освещения)
#   Chunk        — гексагональная сота (география, статус, вершины стыковки)
#   WorldObject  — объект в абсолютных координатах (не привязан к чанку)
#
# Удалены:
#   Scene         — сцена = тег в WorldObject.properties.tags
#   WorldLighting — освещение встроено в World.lighting (JSON)
#   ChunkVertex    — отложено до реализации визуализации сот
# ==============================================================================

from .world import World
from .chunk import Chunk
from .world_object import WorldObject

__all__ = [
    "World",
    "Chunk",
    "WorldObject",
]
