# projects/models.py
# ==============================================================================
# ПРОЕКТ — контейнер верхнего уровня
# Один проект = одна игра. Содержит миры.
# ==============================================================================

import uuid
from django.db import models
from django.conf import settings


class Project(models.Model):
    """Контейнер верхнего уровня — проект объединяет миры и команду"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===== ОСНОВНОЕ =====
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # ===== ВЛАДЕЛЕЦ =====
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )

    # ===== УЧАСТНИКИ =====
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        blank=True,
    )

    # ===== СТАТУС =====
    is_public = models.BooleanField(
        default=False,
        help_text="Публичный проект виден всем",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    @property
    def worlds_count(self):
        """Количество миров в проекте"""
        return self.worlds.count()

    @property
    def objects_count(self):
        """Общее количество объектов во всех мирах проекта"""
        from scenes.models import WorldObject

        return WorldObject.objects.filter(world__project=self).count()
