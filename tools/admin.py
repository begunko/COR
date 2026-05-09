from django.contrib import admin
from .models import Tool, UserToolProfile, WorldToolProfile


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "tool_type",
        "order",
        "available_for_all",
        "is_active",
    ]
    list_filter = ["tool_type", "available_for_all", "is_active"]
    search_fields = ["name", "display_name"]
    list_editable = ["order", "available_for_all", "is_active"]

    fieldsets = (
        ("Основное", {"fields": ("name", "display_name", "description", "tool_type")}),
        ("Параметры", {"fields": ("default_params",)}),
        ("Отображение", {"fields": ("icon_svg", "icon_class", "order")}),
        ("Доступ", {"fields": ("available_for_all", "is_active")}),
    )


@admin.register(UserToolProfile)
class UserToolProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
    filter_horizontal = ["tools"]
    search_fields = ["user__email", "user__display_name"]


@admin.register(WorldToolProfile)
class WorldToolProfileAdmin(admin.ModelAdmin):
    list_display = ["world", "mode", "created_at"]
    list_filter = ["mode"]
    filter_horizontal = ["tools"]
