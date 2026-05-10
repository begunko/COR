import uuid
from django.db import models


class WorldLighting(models.Model):
    """Настройки освещения для мира"""

    world = models.OneToOneField(
        "World", on_delete=models.CASCADE, related_name="lighting"
    )

    ambient_color = models.CharField(max_length=7, default="#404060")
    ambient_intensity = models.FloatField(default=0.5)

    sun_enabled = models.BooleanField(default=True)
    sun_color = models.CharField(max_length=7, default="#ffffff")
    sun_intensity = models.FloatField(default=1.0)
    sun_rotation_x = models.FloatField(default=45.0)
    sun_rotation_y = models.FloatField(default=30.0)

    fog_enabled = models.BooleanField(default=False)
    fog_color = models.CharField(max_length=7, default="#c0c0c0")
    fog_density = models.FloatField(default=0.001)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Освещение мира"
        verbose_name_plural = "Освещение миров"

    def __str__(self):
        return f"Освещение: {self.world.name}"
