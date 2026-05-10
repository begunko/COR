# users/admin.py
# ==============================================================================
# АДМИНКА ПОЛЬЗОВАТЕЛЕЙ
# ==============================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ProjectPermission


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "username",
        "display_name",
        "role",
        "is_online",
        "last_seen",
        "is_staff",
        "date_joined",
    ]
    list_filter = [
        "role",
        "is_online",
        "is_staff",
        "is_superuser",
        "date_joined",
    ]
    search_fields = [
        "email",
        "username",
        "display_name",
    ]
    ordering = ["-date_joined"]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "COR Профиль",
            {
                "fields": (
                    "display_name",
                    "cursor_color",
                    "avatar",
                    "role",
                )
            },
        ),
        (
            "Инструменты",
            {
                "fields": ("tools_config",),
                "description": (
                    "JSON с настройками панели инструментов.<br>"
                    'Пример: {"active_toolkits": ["uuid-1", "uuid-2"], "favorites": ["uuid-3"]}'
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "COR Профиль",
            {
                "fields": (
                    "email",
                    "display_name",
                    "cursor_color",
                    "role",
                )
            },
        ),
    )


@admin.register(ProjectPermission)
class ProjectPermissionAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "permission", "granted_at"]
    list_filter = ["permission", "granted_at"]
    search_fields = ["user__email", "project__name"]
