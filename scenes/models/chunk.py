# scenes/models/chunk.py
# ==============================================================================
# ЧАНК — шестигранная сота (гексагональная призма с пирамидальными крышками)
#
# Соседи:
#   6 горизонтальных (по граням гексагона)
#   + 1 верхний (стыкуется через пирамидальную крышку)
#   + 1 нижний (стыкуется через пирамидальную крышку)
#   = 8 соседей
#
# Координаты:
#   grid_q, grid_r — осевые координаты гексагона
#   grid_s = -(q + r) — вычисляется автоматически
#   grid_y — вертикальный слой (целое число, шаг = chunk_size)
#
# Мировые координаты центра чанка:
#   x = chunk_size * (q * 1.5)
#   y = y * chunk_size
#   z = chunk_size * (r * 1.732 + q * 0.866)
# ==============================================================================

import uuid
from django.db import models


class Chunk(models.Model):
    """
    Шестигранная сота — базовая единица пространства COR.
    НЕ хранит объекты внутри себя.
    Объекты (WorldObject) существуют в абсолютных координатах.
    Принадлежность объекта к чанку вычисляется через (chunk_q, chunk_r, chunk_y).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===== ПРИВЯЗКА К МИРУ =====
    world = models.ForeignKey(
        "World",
        on_delete=models.CASCADE,
        related_name="chunks",
        null=True,
        blank=True,
    )

    # ===== ГЕКСАГОНАЛЬНЫЕ КООРДИНАТЫ =====
    grid_q = models.IntegerField(default=0)  # ось Q
    grid_r = models.IntegerField(default=0)  # ось R
    grid_s = models.IntegerField(default=0)  # ось S = -(q+r), вычисляется при save()
    grid_y = models.IntegerField(default=0)  # вертикальный слой

    # ===== МИРОВЫЕ КООРДИНАТЫ ЦЕНТРА (вычисляются при save) =====
    world_x = models.FloatField(default=0.0)
    world_y = models.FloatField(default=0.0)  # центр по вертикали
    world_z = models.FloatField(default=0.0)

    # ===== ТИП ЧАНКА (существует ли он физически) =====
    CHUNK_TYPE_CHOICES = [
        ("void", "Пустота — не существует в мире"),
        ("empty", "Пустой — ландшафт есть, объектов нет"),
        ("full", "Полный — ландшафт + объекты"),
    ]
    chunk_type = models.CharField(
        max_length=10, choices=CHUNK_TYPE_CHOICES, default="void"
    )

    # ===== СТАТУС ЗАГРУЗКИ =====
    is_active = models.BooleanField(
        default=False,
        help_text="Чанк готов к редактированию / загружен в память",
    )
    is_loaded = models.BooleanField(
        default=False,
        help_text="Чанк загружен клиентом в данный момент",
    )
    loaded_by = models.ManyToManyField(
        "users.User",
        related_name="loaded_chunks",
        blank=True,
    )

    # ===== ВЕРШИНЫ СТЫКОВКИ (для визуализации сот) =====
    # Пирамидальная крышка: верхняя и нижняя вершины
    top_vertex_x = models.FloatField(default=0.0)
    top_vertex_y = models.FloatField(default=250.0)
    top_vertex_z = models.FloatField(default=0.0)

    bottom_vertex_x = models.FloatField(default=0.0)
    bottom_vertex_y = models.FloatField(default=-250.0)
    bottom_vertex_z = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Чанк (шестигранная сота)"
        verbose_name_plural = "Чанки (шестигранные соты)"
        unique_together = [("world", "grid_q", "grid_r", "grid_y")]
        indexes = [
            models.Index(fields=["world", "grid_q", "grid_r", "grid_y"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"Сота ({self.grid_q},{self.grid_r},{self.grid_y})"

    # ==========================================================================
    # СОСЕДИ
    # ==========================================================================

    def get_neighbor_coords(self):
        """
        Возвращает список координат 8 соседних чанков:
        - 6 горизонтальных (по граням гексагона)
        - 1 верхний (grid_y + 1)
        - 1 нижний (grid_y - 1)
        """
        # Направления для горизонтальных соседей в осевых координатах
        hex_directions = [
            (+1, 0),  # восток
            (+1, -1),  # северо-восток
            (0, -1),  # северо-запад
            (-1, 0),  # запад
            (-1, +1),  # юго-запад
            (0, +1),  # юго-восток
        ]

        neighbors = []

        for dq, dr in hex_directions:
            q = self.grid_q + dq
            r = self.grid_r + dr
            neighbors.append(
                {
                    "grid_q": q,
                    "grid_r": r,
                    "grid_s": -(q + r),
                    "grid_y": self.grid_y,
                }
            )

        # Верхний и нижний соседи
        neighbors.append(
            {
                "grid_q": self.grid_q,
                "grid_r": self.grid_r,
                "grid_s": self.grid_s,
                "grid_y": self.grid_y + 1,
            }
        )
        neighbors.append(
            {
                "grid_q": self.grid_q,
                "grid_r": self.grid_r,
                "grid_s": self.grid_s,
                "grid_y": self.grid_y - 1,
            }
        )

        return neighbors

    def activate_neighbors(self):
        """
        Создаёт соседние чанки (если их ещё нет) и активирует их.
        Возвращает список созданных/активированных чанков.
        """
        from .chunk import (
            Chunk,
        )  # локальный импорт во избежание циклической зависимости

        activated = []

        for coords in self.get_neighbor_coords():
            chunk, created = Chunk.objects.get_or_create(
                world=self.world,
                grid_q=coords["grid_q"],
                grid_r=coords["grid_r"],
                grid_y=coords["grid_y"],
                defaults={
                    "grid_s": coords["grid_s"],
                    "chunk_type": "empty",
                    "is_active": True,
                    "is_loaded": False,
                },
            )
            # Если чанк уже существовал, но был неактивен — активируем
            if not created and not chunk.is_active:
                chunk.is_active = True
                chunk.save(update_fields=["is_active"])

            activated.append(chunk)

        return activated

    # ==========================================================================
    # ГРАНИЦЫ ЧАНКА (Bounding Box для пространственных запросов)
    # ==========================================================================

    def get_bounds(self):
        """
        Возвращает словарь с min/max координатами чанка в мировых координатах.
        Используется для поиска объектов внутри чанка.
        """
        size = self.world.chunk_size if self.world else 500.0
        half = size / 2

        return {
            "min_x": self.world_x - half,
            "max_x": self.world_x + half,
            "min_y": self.world_y - half,
            "max_y": self.world_y + half,
            "min_z": self.world_z - half,
            "max_z": self.world_z + half,
        }

    # ==========================================================================
    # ВЫЧИСЛЕНИЕ МИРОВЫХ КООРДИНАТ
    # ==========================================================================

    def calculate_world_position(self):
        """
        Вычисляет мировые координаты центра чанка на основе гексагональной сетки.
        """
        size = self.world.chunk_size if self.world else 500.0

        # Осевые координаты (q, r) → мировые (x, z)
        x = size * (self.grid_q * 1.5)
        z = size * (self.grid_r * 1.732 + self.grid_q * 0.866)  # 1.732 ≈ √3
        y = self.grid_y * size

        return (x, y, z)

    # ==========================================================================
    # СОХРАНЕНИЕ
    # ==========================================================================

    def save(self, *args, **kwargs):
        # Автоматически вычисляем s = -(q + r)
        self.grid_s = -(self.grid_q + self.grid_r)

        # Если мировые координаты не заданы — вычисляем
        if not self.world_x and not self.world_z:
            x, y, z = self.calculate_world_position()
            self.world_x = x
            self.world_y = y
            self.world_z = z

        super().save(*args, **kwargs)
