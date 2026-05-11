# assets/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "children_count",
        "has_animation",
        "tags_list",
        "created_by",
        "is_active",
        "open_editor",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Основное", {"fields": ("name", "description", "created_by")}),
        (
            "Данные ассета",
            {
                "fields": ("data",),
                "description": "JSON с описанием всех дочерних элементов",
            },
        ),
        (
            "Анимация",
            {
                "fields": ("animation",),
                "description": "Типы: rotate, flicker, sway, blink, path",
            },
        ),
        ("Метаданные", {"fields": ("tags", "thumbnail")}),
        ("Статус", {"fields": ("is_active", "created_at", "updated_at")}),
    )

    def children_count(self, obj):
        return obj.children_count

    children_count.short_description = "Элементов"

    def has_animation(self, obj):
        return "✅" if obj.has_animation else "—"

    has_animation.short_description = "Аним."

    def tags_list(self, obj):
        return ", ".join(obj.tags[:5]) if obj.tags else "—"

    tags_list.short_description = "Теги"

    def open_editor(self, obj):
        url = f"/editor/asset/{obj.id}/"
        return format_html(
            '<a href="{}" target="_blank" style="background: #ff6600; color: white; '
            'padding: 5px 15px; border-radius: 5px; text-decoration: none;">🎨 Редактировать</a>',
            url,
        )

    open_editor.short_description = ""
