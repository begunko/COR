import uuid
from django.db import models


class Chunk(models.Model):
    """
    Шестигранная призма с пирамидальными крышками — базовая единица пространства COR.

    Соты соединяются гранями, образуя бесшовную 3D-сетку.
    Пирамидальные крышки обеспечивают плавные переходы по вертикали.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Привязка к миру и сцене
    world = models.ForeignKey(
        "World", on_delete=models.CASCADE, related_name="chunks", null=True, blank=True
    )
    scene = models.ForeignKey(
        "Scene", on_delete=models.SET_NULL, related_name="chunks", null=True, blank=True
    )

    # ===== ГЕКСАГОНАЛЬНЫЕ КООРДИНАТЫ =====
    grid_q = models.IntegerField(default=0)  # ось Q
    grid_r = models.IntegerField(default=0)  # ось R
    grid_s = models.IntegerField(default=0)  # ось S = -(q+r)
    grid_y = models.IntegerField(default=0)  # вертикальный слой

    # ===== МИРОВЫЕ КООРДИНАТЫ ЦЕНТРА =====
    world_x = models.FloatField(default=0.0)
    world_y = models.FloatField(default=0.0)  # центр по вертикали
    world_z = models.FloatField(default=0.0)

    # ===== ТИП ЧАНКА =====
    CHUNK_TYPE_CHOICES = [
        ("void", "Пустота — не существует"),
        ("empty", "Пустой — только ландшафт, без объектов"),
        ("full", "Полный — с объектами"),
    ]
    chunk_type = models.CharField(
        max_length=10, choices=CHUNK_TYPE_CHOICES, default="void"
    )

    # Данные объектов внутри чанка (JSON)
    data = models.JSONField(default=dict, blank=True)

    # ===== ВЕРШИНЫ СТЫКОВКИ =====
    top_vertex_x = models.FloatField(default=0.0)
    top_vertex_y = models.FloatField(default=250.0)
    top_vertex_z = models.FloatField(default=0.0)

    bottom_vertex_x = models.FloatField(default=0.0)
    bottom_vertex_y = models.FloatField(default=-250.0)
    bottom_vertex_z = models.FloatField(default=0.0)

    # ===== СТАТУС =====
    is_active = models.BooleanField(default=False)
    is_loaded = models.BooleanField(default=False)
    loaded_by = models.ManyToManyField(
        "users.User", related_name="loaded_chunks", blank=True
    )

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

    def get_neighbors(self):
        """
        Возвращает список координат 8 соседних чанков.
        6 горизонтальных + 1 верхний + 1 нижний.
        """
        hex_directions = [
            (+1, 0),
            (+1, -1),
            (0, -1),
            (-1, 0),
            (-1, +1),
            (0, +1),
        ]

        neighbors = []
        for dq, dr in hex_directions:
            neighbors.append(
                {
                    "grid_q": self.grid_q + dq,
                    "grid_r": self.grid_r + dr,
                    "grid_s": -(self.grid_q + dq + self.grid_r + dr),
                    "grid_y": self.grid_y,
                }
            )

        # Вертикальные соседи
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
        Активирует (создаёт) соседние чанки, если они не существуют.
        Возвращает список созданных чанков.
        """
        created_chunks = []

        for neighbor_coords in self.get_neighbors():
            chunk, created = Chunk.objects.get_or_create(
                world=self.world,
                grid_q=neighbor_coords["grid_q"],
                grid_r=neighbor_coords["grid_r"],
                grid_y=neighbor_coords["grid_y"],
                defaults={
                    "grid_s": neighbor_coords["grid_s"],
                    "chunk_type": "empty",
                    "is_active": False,
                },
            )
            if created:
                created_chunks.append(chunk)

        return created_chunks

    def calculate_world_position(self):
        """Вычисляет мировые координаты центра чанка на основе гексагональной сетки."""
        size = self.world.chunk_size if self.world else 500.0

        # Преобразование осевых координат (q, r) в мировые (x, z)
        x = size * (self.grid_q * 1.5)
        z = size * (self.grid_r * 1.732 + self.grid_q * 0.866)
        y = self.grid_y * size

        return (x, y, z)

    def save(self, *args, **kwargs):
        # Автоматически вычисляем s
        self.grid_s = -(self.grid_q + self.grid_r)

        # Вычисляем мировые координаты
        if not self.world_x and not self.world_z:
            x, y, z = self.calculate_world_position()
            self.world_x = x
            self.world_y = y
            self.world_z = z

        super().save(*args, **kwargs)
