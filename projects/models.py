import uuid
from django.db import models
from django.conf import settings


class Project(models.Model):
    """Контейнер верхнего уровня — один проект = одна игра"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Владелец
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )

    # Участники команды
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="projects", blank=True
    )

    # Настройки мира
    chunk_size = models.FloatField(default=500.0)  # размер чанка в метрах
    max_height = models.IntegerField(default=10000)  # верхняя граница
    min_depth = models.IntegerField(default=-10000)  # нижняя граница

    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name
