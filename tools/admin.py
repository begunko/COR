# tools/admin.py
# ==============================================================================
# АДМИНКА ДЛЯ ИНСТРУМЕНТОВ, НАБОРОВ И КАТЕГОРИЙ
# ==============================================================================

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tool, Toolkit

# ==============================================================================
# INLINE ДЛЯ ПОДКАТЕГОРИЙ (в карточке Category)
# ==============================================================================


class SubcategoryInline(admin.TabularInline):
    model = Category
    fk_name = "parent"
    extra = 1
    verbose_name = "Подкатегория"
    verbose_name_plural = "Подкатегории"
    fields = ["name", "icon", "path", "order", "is_active"]


# ==============================================================================
# INLINE ДЛЯ ИНСТРУМЕНТОВ (в карточке Category)
# ==============================================================================


class ToolInlineForCategory(admin.TabularInline):
    model = Tool.categories.through
    extra = 1
    verbose_name = "Инструмент"
    verbose_name_plural = "Инструменты в категории"


# ==============================================================================
# CATEGORY ADMIN
# ==============================================================================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "hierarchical_name",
        "path",
        "level",
        "tools_count",
        "order",
        "is_active",
    ]
    list_filter = ["level", "is_active", "parent"]
    search_fields = ["name", "path", "description"]
    list_editable = ["order", "is_active"]

    fieldsets = (
        ("Основное", {"fields": ("name", "icon", "description")}),
        (
            "Иерархия",
            {
                "fields": ("parent", "path", "level"),
                "description": (
                    "path задаётся автоматически, но можно указать вручную.<br>"
                    "level: 0 = корень, 1 = подкатегория, 2 = под-подкатегория."
                ),
            },
        ),
        ("Порядок и статус", {"fields": ("order", "is_active")}),
    )

    inlines = [SubcategoryInline, ToolInlineForCategory]

    def hierarchical_name(self, obj):
        indent = "— " * obj.level
        return f"{indent}{obj.icon} {obj.name}"

    hierarchical_name.short_description = "Категория"

    def save_model(self, request, obj, form, change):
        """Автоматически вычисляет path и level при сохранении"""
        if obj.parent:
            obj.level = obj.parent.level + 1
            obj.path = f"{obj.parent.path}/{obj.name.lower().replace(' ', '_')}"
        else:
            obj.level = 0
            obj.path = obj.name.lower().replace(" ", "_")
        super().save_model(request, obj, form, change)


# ==============================================================================
# INLINE ДЛЯ НАБОРОВ (в карточке Tool)
# ==============================================================================


class ToolkitInline(admin.TabularInline):
    model = Toolkit.tools.through
    extra = 1
    verbose_name = "Набор"
    verbose_name_plural = "Наборы, в которые входит инструмент"


# ==============================================================================
# TOOL ADMIN
# ==============================================================================


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "name",
        "tool_type",
        "primary_category",
        "used_in_toolkits",
        "order",
        "is_active",
        "open_editor",
    ]
    list_filter = ["tool_type", "is_active", "primary_category", "categories"]
    search_fields = ["name", "display_name", "description"]
    list_editable = ["order", "is_active", "primary_category"]
    filter_horizontal = ["categories"]

    fieldsets = (
        ("Основное", {"fields": ("name", "display_name", "description", "tool_type")}),
        (
            "Категории",
            {
                "fields": ("primary_category", "categories"),
                "description": (
                    "primary_category — основная категория.<br>"
                    "categories — все категории, к которым относится инструмент."
                ),
            },
        ),
        (
            "Параметры по умолчанию",
            {
                "fields": ("default_params",),
                "description": (
                    "JSON с параметрами инструмента.<br><br>"
                    "<b>Для create_mesh (простая фигура):</b><br>"
                    '{"geometry": "BoxGeometry", "size": 1, "color": "#ff6600", "defaultY": 0.5}<br><br>'
                    "<b>Для create_mesh (групповая фигура):</b><br>"
                    '{"geometry": "Group", "children": [{"name": "ствол", "geometry": "CylinderGeometry", ...}]}<br><br>'
                    "<b>Для create_light:</b><br>"
                    '{"light_type": "point", "color": "#ffffff", "intensity": 1.0, "range": 10}'
                ),
            },
        ),
        ("Порядок и статус", {"fields": ("order", "is_active")}),
    )

    inlines = [ToolkitInline]

    def used_in_toolkits(self, obj):
        """Показывает, в скольких наборах используется инструмент"""
        count = obj.toolkits.count()
        if count == 0:
            return "—"
        toolkit_names = ", ".join(t.name for t in obj.toolkits.all()[:3])
        if count > 3:
            toolkit_names += f" + ещё {count - 3}"
        return toolkit_names

    used_in_toolkits.short_description = "Входит в наборы"

    def open_editor(self, obj):
        """Кнопка для открытия 3D-редактора"""
        url = f"/editor/tool/{obj.id}/"
        return format_html(
            '<a href="{}" target="_blank" style="background: #ff6600; color: white; '
            'padding: 5px 15px; border-radius: 5px; text-decoration: none;">🎨 3D-Редактор</a>',
            url,
        )

    open_editor.short_description = ""


# ==============================================================================
# INLINE ДЛЯ ИНСТРУМЕНТОВ (в карточке Toolkit)
# ==============================================================================


class ToolInlineForToolkit(admin.TabularInline):
    model = Toolkit.tools.through
    extra = 1
    verbose_name = "Инструмент"
    verbose_name_plural = "Инструменты в наборе"


# ==============================================================================
# TOOLKIT ADMIN
# ==============================================================================


@admin.register(Toolkit)
class ToolkitAdmin(admin.ModelAdmin):
    list_display = [
        "icon",
        "name",
        "owner",
        "tools_count",
        "order",
        "is_active",
    ]
    list_filter = ["is_active", "owner"]
    search_fields = ["name", "description", "owner__email"]
    list_editable = ["order", "is_active"]
    filter_horizontal = ["tools"]

    fieldsets = (
        ("Основное", {"fields": ("name", "icon", "description", "owner")}),
        (
            "Инструменты",
            {
                "fields": ("tools",),
                "description": "Выберите инструменты, которые будут в этом наборе.",
            },
        ),
        ("Порядок и статус", {"fields": ("order", "is_active")}),
    )

    inlines = [ToolInlineForToolkit]

    def tools_count(self, obj):
        return obj.tools.count()

    tools_count.short_description = "Инструментов"
