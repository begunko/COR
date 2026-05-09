import uuid
from django.db import models
from django.conf import settings


class Tool(models.Model):
    """Доступный инструмент в системе"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Название инструмента
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200, help_text="Отображается на панели")
    description = models.TextField(blank=True)

    # Тип инструмента
    TOOL_TYPE_CHOICES = [
        ("create_mesh", "Создать меш (куб, сфера, цилиндр)"),
        ("create_light", "Создать источник света"),
        ("transform", "Инструмент перемещения/вращения/масштаба"),
        ("material", "Назначить материал"),
        ("script", "Привязать скрипт"),
        ("trigger", "Создать триггер-зону"),
        ("spawn", "Точка спавна"),
        ("terrain", "Редактор ландшафта"),
        ("paint", "Кисть (раскраска объектов)"),
    ]
    tool_type = models.CharField(max_length=20, choices=TOOL_TYPE_CHOICES)

    # Параметры инструмента (JSON — зависит от типа)
    # Например для create_mesh: {"mesh_type": "cube", "default_size": 1}
    default_params = models.JSONField(default=dict, blank=True)

    # Иконка (можно хранить SVG или путь к файлу)
    icon_svg = models.TextField(blank=True, help_text="SVG-иконка для панели")
    icon_class = models.CharField(
        max_length=100, blank=True, help_text="CSS-класс для иконки"
    )

    # Порядок на панели
    order = models.IntegerField(default=0)

    # Для кого доступен по умолчанию
    available_for_all = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Инструмент"
        verbose_name_plural = "Инструменты"
        ordering = ["order", "tool_type", "name"]

    def __str__(self):
        return f"{self.display_name} ({self.tool_type})"


class UserToolProfile(models.Model):
    """Набор инструментов конкретного пользователя"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tool_profile"
    )

    # Активные инструменты пользователя
    tools = models.ManyToManyField(Tool, blank=True, related_name="users")

    # Компоновка панели (JSON — пользователь может перетаскивать инструменты)
    # {"layout": [{"tool_id": "uuid", "position": 0}, ...]}
    layout = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профиль инструментов пользователя"
        verbose_name_plural = "Профили инструментов пользователей"

    def __str__(self):
        return f"Инструменты: {self.user}"


class WorldToolProfile(models.Model):
    """Набор инструментов для конкретного мира (переопределяет пользовательский)"""

    world = models.OneToOneField(
        "scenes.World", on_delete=models.CASCADE, related_name="tool_profile"
    )

    tools = models.ManyToManyField(Tool, blank=True, related_name="worlds")

    # Режим: заменять пользовательские инструменты или дополнять
    MODE_CHOICES = [
        ("override", "Заменить инструменты пользователя"),
        ("extend", "Добавить к инструментам пользователя"),
    ]
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="extend")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Инструменты мира"
        verbose_name_plural = "Инструменты миров"

    def __str__(self):
        return f"Инструменты мира: {self.world.name}"
