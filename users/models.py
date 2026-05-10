# users/models.py
# ==============================================================================
# ПОЛЬЗОВАТЕЛИ И ПРАВА
# ==============================================================================

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Пользователь COR — творец миров"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(_("email address"), unique=True, db_index=True)

    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Имя, которое видят другие пользователи",
    )

    cursor_color = models.CharField(
        max_length=7,
        default="#FF4444",
        help_text="HEX-цвет курсора в редакторе",
    )

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Role(models.TextChoices):
        USER = "user", _("Пользователь")
        MODERATOR = "moderator", _("Модератор")
        ADMIN = "admin", _("Администратор")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )

    # Настройки инструментов
    tools_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Настройки инструментов: активные наборы, избранное",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.display_name or self.username

    def get_full_name(self):
        return self.display_name or self.username

    def get_short_name(self):
        return self.display_name or self.username.split("@")[0]

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    def get_active_toolkits(self):
        return self.tools_config.get("active_toolkits", [])

    def get_favorites(self):
        return self.tools_config.get("favorites", [])


class ProjectPermission(models.Model):
    """Права пользователя на конкретный проект"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="project_permissions"
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="permissions"
    )

    class PermissionLevel(models.TextChoices):
        VIEWER = "viewer", _("Зритель — только смотреть")
        EDITOR = "editor", _("Редактор — двигать объекты")
        DESIGNER = "designer", _("Дизайнер — создавать сцены и чанки")
        ADMIN = "admin", _("Администратор — управлять участниками")
        OWNER = "owner", _("Владелец — полный контроль")

    permission = models.CharField(
        max_length=20,
        choices=PermissionLevel.choices,
        default=PermissionLevel.EDITOR,
    )

    granted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="granted_permissions"
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("разрешение проекта")
        verbose_name_plural = _("разрешения проектов")
        unique_together = [("user", "project")]

    def __str__(self):
        return f"{self.user} → {self.project}: {self.permission}"
