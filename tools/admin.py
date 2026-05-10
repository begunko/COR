# tools/admin.py
# ==============================================================================
# АДМИНКА ДЛЯ ИНСТРУМЕНТОВ И НАБОРОВ
# ==============================================================================

from django.contrib import admin
from .models import Tool, Toolkit


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "name",
        "tool_type",
        "order",
        "is_active",
        "used_in_toolkits",
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
            },
        ),
        ("Порядок и статус", {"fields": ("order", "is_active")}),
    )

    def tools_count(self, obj):
        return obj.tools.count()

    tools_count.short_description = "Инструментов"
