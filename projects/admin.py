# projects/admin.py
# ==============================================================================
# АДМИНКА ПРОЕКТОВ
# ==============================================================================

from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "owner",
        "worlds_count",
        "objects_count",
        "is_public",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_public", "created_at"]
    search_fields = ["name", "owner__email", "description"]
    filter_horizontal = ["members"]

    fieldsets = (
        ("Основное", {"fields": ("name", "description", "owner")}),
        (
            "Команда",
            {
                "fields": ("members",),
            },
        ),
        (
            "Статус",
            {
                "fields": ("is_public",),
            },
        ),
    )

    def worlds_count(self, obj):
        return obj.worlds.count()

    worlds_count.short_description = "Миров"

    def objects_count(self, obj):
        return obj.objects_count

    objects_count.short_description = "Объектов"
