# tools/models.py
# ==============================================================================
# ИНСТРУМЕНТЫ, НАБОРЫ И КАТЕГОРИИ
#
# Tool      — глобальный реестр ВСЕХ возможных инструментов в системе.
#             Создаются через админку или load_all_tools.py.
#
# Toolkit   — набор инструментов, сгруппированных по смыслу.
#             Например: "Базовые фигуры", "Каменные блоки", "Освещение".
#             У каждого набора есть владелец (owner), но видят все.
#
# Category  — иерархическая категория для организации инструментов.
#             FK от Tool защищён — при удалении категории инструменты НЕ страдают.
#             Используется плоская модель с path вместо рекурсивных связей.
# ==============================================================================

import uuid
from django.db import models
from django.conf import settings

# ==============================================================================
# CATEGORY — категория инструментов
# ==============================================================================


class Category(models.Model):
    """
    Плоская категория с полным путём.
    Иерархия строится через path: "architecture/columns/doric"

    Связь с Tool через M2M (защищённый FK).
    При удалении категории инструменты НЕ удаляются.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===== ОСНОВНОЕ =====
    name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Отображаемое имя: 'Колонны', 'Столы', 'Деревья'",
    )

    path = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
        help_text="Полный путь: 'architecture/columns' или 'nature/trees/oak'",
    )

    level = models.IntegerField(
        default=0,
        help_text="0 = корневая категория, 1 = подкатегория, 2 = под-подкатегория",
    )

    # ===== ИЕРАРХИЯ (только для навигации в админке) =====
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # ← МЯГКОЕ удаление: дочерние не удаляются
        related_name="children",
        help_text="Родительская категория (для построения дерева в админке)",
    )

    # ===== ОТОБРАЖЕНИЕ =====
    icon = models.CharField(
        max_length=10, default="📦", help_text="Эмодзи для отображения в тулбаре"
    )

    description = models.TextField(blank=True, help_text="Описание категории")

    order = models.IntegerField(
        default=0, help_text="Порядок отображения (меньше = выше)"
    )

    # ===== СТАТУС =====
    is_active = models.BooleanField(
        default=True, help_text="Если выключена — категория скрыта"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["level", "order", "name"]
        indexes = [
            models.Index(fields=["path"]),
            models.Index(fields=["level", "order"]),
        ]

    def __str__(self):
        indent = "  " * self.level
        return f"{indent}{self.icon} {self.name}"

    @property
    def tools_count(self):
        """Количество инструментов в категории (включая подкатегории)"""
        return self.get_all_tools().count()

    def get_all_tools(self):
        """Возвращает ВСЕ инструменты в этой категории и подкатегориях"""
        from django.db.models import Q

        # Все подкатегории
        descendant_paths = Category.objects.filter(
            path__startswith=self.path
        ).values_list("id", flat=True)

        return Tool.objects.filter(
            Q(primary_category__in=descendant_paths)
            | Q(categories__in=descendant_paths)
        ).distinct()

    def get_subcategories(self):
        """Возвращает прямые подкатегории"""
        return Category.objects.filter(parent=self, is_active=True).order_by(
            "order", "name"
        )

    def get_ancestors(self):
        """Возвращает список родительских категорий (хлебные крошки)"""
        if not self.path:
            return []
        parts = self.path.split("/")
        ancestors = []
        for i in range(len(parts)):
            ancestor_path = "/".join(parts[: i + 1])
            try:
                ancestor = Category.objects.get(path=ancestor_path)
                if ancestor.id != self.id:
                    ancestors.append(ancestor)
            except Category.DoesNotExist:
                pass
        return ancestors


# ==============================================================================
# TOOL — глобальный реестр инструментов
# ==============================================================================


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
    default_params = models.JSONField(
        default=dict,
        blank=True,
        help_text="Параметры инструмента по умолчанию (геометрия, материал и т.д.)",
    )

    # ===== КАТЕГОРИИ (M2M — защищённый FK) =====
    primary_category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # ← МЯГКО: при удалении категории поле = NULL
        related_name="primary_tools",
        help_text="Основная категория для отображения",
    )

    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="tools",
        help_text="Все категории, к которым относится инструмент",
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
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Инструмент (реестр)"
        verbose_name_plural = "Инструменты (реестр)"
        ordering = ["order", "tool_type", "name"]
        indexes = [
            models.Index(fields=["order", "tool_type", "name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.tool_type})"

    @property
    def used_in_toolkits_count(self):
        """Количество наборов, в которых используется инструмент"""
        return self.toolkits.count()

    @property
    def category_list(self):
        """Список имён категорий для отображения"""
        return ", ".join(self.categories.values_list("name", flat=True)[:5]) or "—"


# ==============================================================================
# TOOLKIT — набор инструментов
# ==============================================================================


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
        on_delete=models.CASCADE,  # ← Если пользователь удалён — наборы удаляются
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

    @property
    def tools_count(self):
        return self.tools.count()
