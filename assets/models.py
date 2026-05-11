# assets/models.py
# ==============================================================================
# АССЕТ — составной объект из геометрических примитивов
#
# Хранит полное описание объекта в JSON (без FK на Tool).
# Создаётся в микроредакторе, используется в сценах и мирах.
# ==============================================================================

import uuid
from django.db import models
from django.conf import settings


class Asset(models.Model):
    """
    Составной объект, собранный из простых геометрий.
    Все данные хранятся в JSON — независимо от Tool.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===== ОСНОВНОЕ =====
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # ===== ДАННЫЕ ОБЪЕКТА =====
    # JSON с полным описанием:
    # {
    #   "children": [
    #     {
    #       "name": "ствол",
    #       "geometry": "CylinderGeometry",
    #       "params": {"radiusTop": 0.15, "radiusBottom": 0.25, "height": 2.5},
    #       "color": "#5D4037",
    #       "position": [0, 1.25, 0],
    #       "rotation": [0, 0, 0],
    #       "scale": [1, 1, 1],
    #       "material": {"roughness": 0.9, "metalness": 0.0}
    #     },
    #     ...
    #   ],
    #   "animation": null или объект анимации
    # }
    data = models.JSONField(default=dict, blank=True)

    # ===== АНИМАЦИЯ (опционально) =====
    # {
    #   "type": "rotate" | "flicker" | "sway" | "blink" | "path",
    #   "target": "self" | "child:имя",
    #   "params": {...}
    # }
    animation = models.JSONField(default=dict, blank=True)

    # ===== МЕТАДАННЫЕ =====
    tags = models.JSONField(default=list, blank=True, help_text="Теги для поиска")

    thumbnail = models.ImageField(
        upload_to="assets/thumbnails/",
        blank=True,
        null=True,
        help_text="Превьюшка ассета",
    )

    # ===== ВЛАДЕЛЕЦ =====
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assets",
    )

    # ===== СТАТУС =====
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ассет"
        verbose_name_plural = "Ассеты"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"📦 {self.name}"

    @property
    def children_count(self):
        """Количество дочерних элементов в ассете"""
        children = self.data.get("children", [])
        return len(children)

    @property
    def has_animation(self):
        """Есть ли анимация у ассета"""
        return bool(self.animation and self.animation.get("type"))
