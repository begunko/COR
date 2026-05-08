import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Пользователь COR — творец миров"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(_("email address"), unique=True, db_index=True)

    # Отображаемое имя (творческий псевдоним)
    display_name = models.CharField(
        max_length=100, blank=True, help_text="Имя, которое видят другие пользователи"
    )

    # Цвет курсора в редакторе
    cursor_color = models.CharField(
        max_length=7, default="#FF4444", help_text="HEX-цвет курсора"
    )

    # Аватар
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # Статус
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    # Роли (глобальные)
    class Role(models.TextChoices):
        USER = "user", _("Пользователь")
        MODERATOR = "moderator", _("Модератор")
        ADMIN = "admin", _("Администратор")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
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

    # Если админ области — указываем сцену или чанк
    restricted_to_scene = models.ForeignKey(
        "scenes.Scene",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Если указано — права только на эту сцену",
    )
    restricted_to_chunk = models.ForeignKey(
        "scenes.Chunk",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Если указано — права только на этот чанк",
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
