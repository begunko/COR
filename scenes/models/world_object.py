# scenes/models/world_object.py
# ==============================================================================
# WORLD OBJECT — объект в мировом пространстве
#
# Ключевой принцип: объект НЕ знает о чанке.
# Принадлежность к чанку вычисляется через chunk_q, chunk_r, chunk_y.
# Эти поля обновляются автоматически при сохранении, если изменились position_x/y/z.
# ==============================================================================

import uuid
from django.db import models


class WorldObject(models.Model):
    """Объект в мировом пространстве. Существует сам по себе."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===== ПРИВЯЗКА К МИРУ =====
    world = models.ForeignKey(
        "World",
        on_delete=models.CASCADE,
        related_name="world_objects",  # ← ИСПРАВЛЕНО: не "objects"
        help_text="Мир, в котором находится объект",
    )

    # ===== ВРЕМЕННЫЙ ID КЛИЕНТА =====
    client_id = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        db_index=True,
        help_text="Временный ID от клиента (не уникальный)",
    )

    # ===== ИМЯ И ТИП =====
    name = models.CharField(max_length=200, default="Объект")

    object_type = models.CharField(
        max_length=30,
        choices=[
            ("mesh", "Меш (геометрия)"),
            ("group", "Группа объектов"),
            ("light", "Источник света"),
            ("spawn", "Точка спавна"),
            ("trigger", "Триггер-зона"),
            ("empty", "Пустой (только трансформация)"),
        ],
        default="mesh",
    )

    # ===== АБСОЛЮТНЫЕ КООРДИНАТЫ =====
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    position_z = models.FloatField(default=0.0)

    # ===== ПОВОРОТ (в градусах) =====
    rotation_x = models.FloatField(default=0.0)
    rotation_y = models.FloatField(default=0.0)
    rotation_z = models.FloatField(default=0.0)

    # ===== МАСШТАБ =====
    scale_x = models.FloatField(default=1.0)
    scale_y = models.FloatField(default=1.0)
    scale_z = models.FloatField(default=1.0)

    # ===== ВЫЧИСЛЯЕМЫЕ КООРДИНАТЫ СОТЫ =====
    chunk_q = models.IntegerField(default=0, db_index=True)
    chunk_r = models.IntegerField(default=0, db_index=True)
    chunk_y = models.IntegerField(default=0, db_index=True)

    # ===== BOUNDING RADIUS =====
    bounding_radius = models.FloatField(
        default=1.0,
        help_text="Радиус описанной сферы для пространственных запросов",
    )

    # ===== ВСЁ ОСТАЛЬНОЕ — JSONB =====
    properties = models.JSONField(
        default=dict,
        blank=True,
        help_text="Геометрия, материал, теги, скрипты и прочие свойства",
    )

    # ===== СЛУЖЕБНОЕ =====
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_objects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Объект мира"
        verbose_name_plural = "Объекты мира"
        indexes = [
            models.Index(fields=["world", "chunk_q", "chunk_r", "chunk_y"]),
            models.Index(fields=["object_type"]),
            models.Index(fields=["world", "position_x", "position_y", "position_z"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.object_type}) @ ({self.position_x:.1f}, {self.position_y:.1f}, {self.position_z:.1f})"

    def calculate_chunk_coords(self):
        """Вычисляет (chunk_q, chunk_r, chunk_y) на основе мировых координат."""
        if not self.world:
            return (0, 0, 0)

        size = self.world.chunk_size
        if size <= 0:
            size = 500.0

        x = self.position_x
        z = self.position_z
        y = self.position_y

        q = x / (size * 1.5)
        r = (z - size * q * 0.866) / (size * 1.732)

        q_rounded = round(q)
        r_rounded = round(r)
        y_layer = round(y / size)

        return (int(q_rounded), int(r_rounded), int(y_layer))

    def save(self, *args, **kwargs):
        if self.world:
            q, r, y = self.calculate_chunk_coords()
            self.chunk_q = q
            self.chunk_r = r
            self.chunk_y = y

        if not self.bounding_radius or self.bounding_radius == 1.0:
            self.bounding_radius = self._calculate_bounding_radius()

        super().save(*args, **kwargs)

    def _calculate_bounding_radius(self):
        sx = abs(self.scale_x)
        sy = abs(self.scale_y)
        sz = abs(self.scale_z)
        max_scale = max(sx, sy, sz)
        return max_scale * 1.5

    def get_tags(self):
        return self.properties.get("tags", [])

    def has_tag(self, tag):
        return tag in self.get_tags()

    def add_tag(self, tag):
        tags = self.get_tags()
        if tag not in tags:
            tags.append(tag)
            self.properties["tags"] = tags
            self.save(update_fields=["properties"])

    def remove_tag(self, tag):
        tags = self.get_tags()
        if tag in tags:
            tags.remove(tag)
            self.properties["tags"] = tags
            self.save(update_fields=["properties"])
