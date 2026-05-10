import uuid
from django.db import models


class ChunkVertex(models.Model):
    """Точка схождения пирамид нескольких чанков"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    world = models.ForeignKey(
        "World", on_delete=models.CASCADE, related_name="vertices"
    )

    world_x = models.FloatField()
    world_y = models.FloatField()
    world_z = models.FloatField()

    height = models.FloatField(default=0.0)
    material_id = models.UUIDField(null=True, blank=True)

    chunks = models.ManyToManyField("Chunk", related_name="vertices")

    class Meta:
        verbose_name = "Вершина стыковки"
        verbose_name_plural = "Вершины стыковки"
        indexes = [
            models.Index(fields=["world_x", "world_y", "world_z"]),
        ]

    def __str__(self):
        return f"Вершина ({self.world_x:.1f}, {self.world_y:.1f}, {self.world_z:.1f})"
