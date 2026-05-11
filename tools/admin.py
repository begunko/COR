# tools/admin.py
# ==============================================================================
# АДМИНКА ДЛЯ ИНСТРУМЕНТОВ И НАБОРОВ
# ==============================================================================

from django.contrib import admin
from django.utils.html import format_html
from .models import Tool, Toolkit


# ===== INLINE: посмотреть/изменить наборы прямо в карточке инструмента =====
class ToolkitInline(admin.TabularInline):
    model = Toolkit.tools.through  # промежуточная таблица M2M
    extra = 1  # одна пустая строка для добавления
    verbose_name = "Набор"
    verbose_name_plural = "Наборы, в которые входит инструмент"


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "name",
        "tool_type",
        "order",
        "is_active",
        "used_in_toolkits",
        "open_editor",
    ]
    list_filter = ["tool_type", "is_active"]
    search_fields = ["name", "display_name", "description"]
    list_editable = ["order", "is_active"]

    fieldsets = (
        ("Основное", {"fields": ("name", "display_name", "description", "tool_type")}),
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

    # ===== ДОБАВЛЯЕМ INLINE ДЛЯ НАБОРОВ =====
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


# ===== INLINE: посмотреть/изменить инструменты прямо в карточке набора =====
class ToolInline(admin.TabularInline):
    model = Toolkit.tools.through
    extra = 1
    verbose_name = "Инструмент"
    verbose_name_plural = "Инструменты в наборе"


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

    fieldsets = (
        ("Основное", {"fields": ("name", "icon", "description", "owner")}),
        (
            "Инструменты",
            {
                "fields": ("tools",),
                "description": "Выберите инструменты, которые будут в этом наборе. "
                "Порядок отображения задаётся в самом инструменте (поле order).",
            },
        ),
        ("Порядок и статус", {"fields": ("order", "is_active")}),
    )

    # ===== ВОЗВРАЩАЕМ filter_horizontal ДЛЯ УДОБНОГО ВЫБОРА =====
    filter_horizontal = ["tools"]

    # ===== ДОБАВЛЯЕМ INLINE ДЛЯ ИНСТРУМЕНТОВ (быстрый доступ) =====
    inlines = [ToolInline]

    def tools_count(self, obj):
        return obj.tools.count()

    tools_count.short_description = "Инструментов"
