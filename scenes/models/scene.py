import uuid
from django.db import models


class Scene(models.Model):
    """
    Логическая группа объектов — "внутреннее убранство", "поляна", "алтарь".
    Может охватывать несколько чанков.
    Не является географической единицей.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    world = models.ForeignKey("World", on_delete=models.CASCADE, related_name="scenes")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Порядок для отображения в списке
    order = models.IntegerField(default=0)

    # Флаг активности
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Сцена (логическая группа)"
        verbose_name_plural = "Сцены (логические группы)"
        ordering = ["order", "name"]

    def __str__(self):
        return f"🎬 {self.name}"
