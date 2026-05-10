# scenes/models/world.py
# ==============================================================================
# МИР — контейнер для чанков и объектов
#
# Освещение встроено прямо в мир (отдельная таблица не нужна).
# Инструменты-наборы: world.default_toolkits — список UUID Toolkit'ов,
# которые доступны всем, кто заходит в этот мир.
# ==============================================================================

import uuid
from django.db import models


class World(models.Model):
    """Один мир внутри проекта. Содержит чанки и объекты."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="worlds",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=200, default="Новый мир")

    # ===== РАЗМЕР ЧАНКА =====
    # Диаметр описанной окружности гексагона в метрах.
    # Все расчёты координат отталкиваются от этого числа.
    chunk_size = models.FloatField(
        default=500.0,
        help_text="Размер чанка в метрах (диаметр описанной окружности гексагона)",
    )

    # ===== ГРАНИЦЫ МИРА =====
    max_chunks_horizontal = models.IntegerField(
        default=100,
        help_text="Максимальное количество чанков по горизонтали от центра",
    )
    max_chunks_vertical = models.IntegerField(
        default=20,
        help_text="Максимальное количество чанков по вертикали (вверх/вниз)",
    )

    # ===== ИНСТРУМЕНТЫ МИРА =====
    # Список UUID наборов инструментов (Toolkit), доступных в этом мире.
    # Объединяется с персональными наборами пользователя.
    default_toolkits = models.JSONField(
        default=list,
        blank=True,
        help_text="Список UUID наборов инструментов, доступных в этом мире",
    )

    # ===== ОСВЕЩЕНИЕ (встроено, отдельная таблица не нужна) =====
    lighting = models.JSONField(
        default=dict,
        blank=True,
        help_text="Настройки освещения мира",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Мир"
        verbose_name_plural = "Миры"

    def __str__(self):
        return self.name

    # ==========================================================================
    # ЗНАЧЕНИЯ ОСВЕЩЕНИЯ ПО УМОЛЧАНИЮ
    # ==========================================================================

    def get_lighting(self):
        """Возвращает настройки освещения с дефолтными значениями."""
        defaults = {
            "ambient": {
                "color": "#404060",
                "intensity": 0.5,
            },
            "sun": {
                "enabled": True,
                "color": "#ffffff",
                "intensity": 1.0,
                "rotation_x": 45.0,
                "rotation_y": 30.0,
            },
            "fog": {
                "enabled": False,
                "color": "#c0c0c0",
                "density": 0.001,
            },
        }
        # Сливаем дефолты с тем, что в базе
        merged = defaults.copy()
        if self.lighting:
            for key in defaults:
                if key in self.lighting:
                    defaults[key].update(self.lighting[key])
        return defaults

    # ==========================================================================
    # ИНИЦИАЛИЗАЦИЯ МИРА
    # ==========================================================================

    def initialize_starting_chunk(self):
        """
        Создаёт центральный чанк (0,0,0) и активирует сферу из 18 соседей (первый круг).
        """
        from .chunk import Chunk

        center_chunk, created = Chunk.objects.get_or_create(
            world=self,
            grid_q=0,
            grid_r=0,
            grid_y=0,
            defaults={
                "chunk_type": "full",
                "is_active": True,
            },
        )

        # Активируем ТОЛЬКО первый круг (18 соседей)
        center_chunk.activate_neighbors()

        return center_chunk
