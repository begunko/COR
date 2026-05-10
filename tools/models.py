# tools/models.py
# ==============================================================================
# ИНСТРУМЕНТЫ И НАБОРЫ
#
# Tool    — глобальный реестр ВСЕХ возможных инструментов в системе.
#           Создаются через админку или load_all_tools.py.
#
# Toolkit — набор инструментов, сгруппированных по смыслу.
#           Например: "Базовые фигуры", "Каменные блоки", "Освещение".
#           У каждого набора есть владелец (owner), но видят все.
#           Настройки доступности:
#             - User.tools_config.active_toolkits — какие наборы видит пользователь
#             - World.default_toolkits — какие наборы доступны в конкретном мире
# ==============================================================================

import uuid
from django.db import models
from django.conf import settings


class Tool(models.Model):
    """
    Глобальный реестр всех инструментов.
    Это НЕ то, что пользователь видит на панели.
    Это — справочник возможных фигур/инструментов.
    На панель попадают через Toolkit.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===== ОСНОВНОЕ =====
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Уникальное системное имя: cube, sphere, pillar",
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Отображается на панели: 'Куб', 'Сфера', 'Колонна'",
    )
    description = models.TextField(
        blank=True,
        help_text="Описание для подсказки",
    )

    # ===== ТИП ИНСТРУМЕНТА =====
    TOOL_TYPE_CHOICES = [
        ("create_mesh", "Создать меш"),
        ("create_light", "Создать источник света"),
        ("place_asset", "Разместить ассет (готовую модель)"),
        ("transform", "Трансформация (перемещение/вращение/масштаб)"),
        ("material", "Назначить материал"),
        ("script", "Привязать скрипт"),
        ("trigger", "Создать триггер-зону"),
        ("spawn", "Точка спавна"),
        ("terrain", "Редактор ландшафта"),
        ("paint", "Кисть (раскраска объектов)"),
    ]
    tool_type = models.CharField(
        max_length=20,
        choices=TOOL_TYPE_CHOICES,
        default="create_mesh",
    )

    # ===== ПАРАМЕТРЫ ПО УМОЛЧАНИЮ (JSON) =====
    # Для create_mesh:
    #   {"geometry": "BoxGeometry", "size": 1, "color": "#ff6600", "defaultY": 0.5}
    #
    # Для групповых фигур:
    #   {"geometry": "Group", "children": [...]}
    #
    # Для create_light:
    #   {"light_type": "point", "color": "#ffffff", "intensity": 1.0, "range": 10}
    default_params = models.JSONField(
        default=dict,
        blank=True,
        help_text="Параметры инструмента по умолчанию (геометрия, материал и т.д.)",
    )

    # ===== ПОРЯДОК ОТОБРАЖЕНИЯ ВНУТРИ НАБОРА =====
    order = models.IntegerField(
        default=0,
        help_text="Порядок внутри набора (меньше = выше)",
    )

    # ===== СТАТУС =====
    is_active = models.BooleanField(
        default=True,
        help_text="Если выключен — не показывается нигде",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Инструмент (реестр)"
        verbose_name_plural = "Инструменты (реестр)"
        ordering = ["order", "tool_type", "name"]

    def __str__(self):
        return f"{self.display_name} ({self.tool_type})"


class Toolkit(models.Model):
    """
    Набор инструментов, сгруппированных по смыслу.
    Владелец (owner) — ответственный за набор, но НЕ приватный владелец.
    Все наборы видны всем (команда общая).
    Пользователь выбирает, какие наборы ему показывать, через User.tools_config.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===== ВЛАДЕЛЕЦ =====
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="toolkits",
        help_text="Кто создал/управляет набором",
    )

    # ===== НАЗВАНИЕ И ИКОНКА =====
    name = models.CharField(
        max_length=200,
        help_text="Название набора: 'Базовые фигуры', 'Каменные блоки'",
    )
    icon = models.CharField(
        max_length=10,
        default="📦",
        help_text="Эмодзи или символ для кнопки набора",
    )
    description = models.TextField(
        blank=True,
        help_text="Описание набора",
    )

    # ===== ИНСТРУМЕНТЫ В НАБОРЕ =====
    tools = models.ManyToManyField(
        Tool,
        blank=True,
        related_name="toolkits",
        help_text="Инструменты, входящие в набор",
    )

    # ===== ПОРЯДОК НА ПАНЕЛИ =====
    order = models.IntegerField(
        default=0,
        help_text="Порядок отображения на панели (меньше = левее/выше)",
    )

    # ===== СТАТУС =====
    is_active = models.BooleanField(
        default=True,
        help_text="Если выключен — набор скрыт у всех",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Набор инструментов"
        verbose_name_plural = "Наборы инструментов"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.icon} {self.name}"

    def get_tools_ordered(self):
        """Возвращает инструменты набора в правильном порядке."""
        return self.tools.all().order_by("order", "name")
