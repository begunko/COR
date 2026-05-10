import uuid
from django.db import models


class World(models.Model):
    """Один мир внутри проекта"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="worlds",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200, default="Новый мир")

    GRID_CHOICES = [
        ("hex", "Гексагональная (COR Sota)"),
    ]
    grid_type = models.CharField(max_length=10, choices=GRID_CHOICES, default="hex")

    # Размер чанка (диаметр описанной окружности гексагона)
    chunk_size = models.FloatField(default=500.0)

    # Границы мира (опционально)
    max_chunks_horizontal = models.IntegerField(default=100)
    max_chunks_vertical = models.IntegerField(default=20)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Мир"
        verbose_name_plural = "Миры"

    def __str__(self):
        return f"{self.name}"

    def initialize_starting_chunk(self):
        """
        Создаёт центральный чанк (0,0,0) и активирует его соседей.
        Вызывается при создании мира (можно через админку).
        """
        from .chunk import (
            Chunk,
        )  # Отложенный импорт чтобы избежать циклической зависимости

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

        center_chunk.activate_neighbors()
        return center_chunk
