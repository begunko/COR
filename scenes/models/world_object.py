import uuid
from django.db import models


class WorldObject(models.Model):
    """Объект внутри чанка"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chunk = models.ForeignKey(
        "Chunk", on_delete=models.CASCADE, related_name="world_objects"
    )
    client_id = models.CharField(max_length=150, null=True, blank=True, unique=True, db_index=True)

    name = models.CharField(max_length=200)
    object_type = models.CharField(
        max_length=30,
        choices=[
            ("mesh", "Меш"),
            ("light", "Источник света"),
            ("spawn", "Точка спавна"),
            ("trigger", "Триггер-зона"),
            ("empty", "Пустой (только трансформация)"),
        ],
        default="mesh",
    )

    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    position_z = models.FloatField(default=0.0)

    rotation_x = models.FloatField(default=0.0)
    rotation_y = models.FloatField(default=0.0)
    rotation_z = models.FloatField(default=0.0)

    scale_x = models.FloatField(default=1.0)
    scale_y = models.FloatField(default=1.0)
    scale_z = models.FloatField(default=1.0)

    mesh_asset_id = models.UUIDField(null=True, blank=True)
    material_asset_id = models.UUIDField(null=True, blank=True)

    properties = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    scene = models.ForeignKey(
        "Scene",
        on_delete=models.SET_NULL,
        related_name="world_objects",
        null=True,
        blank=True,
        help_text="Логическая группа, к которой относится объект",
    )

    class Meta:
        verbose_name = "Объект мира"
        verbose_name_plural = "Объекты мира"

    def __str__(self):
        return f"{self.name} ({self.object_type})"
