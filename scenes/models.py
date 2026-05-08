import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class World(models.Model):
    """Один мир внутри проекта"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="worlds",
    )
    name = models.CharField(max_length=200)

    # Настройки сетки
    GRID_CHOICES = [
        ("hex", "Гексагональная"),
        ("square", "Квадратная (запасной вариант)"),
    ]
    grid_type = models.CharField(
        max_length=10,
        choices=GRID_CHOICES,
        default="hex",
    )

    # Размеры
    chunk_size = models.FloatField(default=500.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Мир"
        verbose_name_plural = "Миры"

    def __str__(self):
        return f"{self.name} (Проект: {self.project.name})"


class Scene(models.Model):
    """Логическая группа чанков — уровень, локация"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    world = models.ForeignKey(
        World,
        on_delete=models.CASCADE,
        related_name="scenes",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сцена"
        verbose_name_plural = "Сцены"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} (Мир: {self.world.name})"


class Chunk(models.Model):
    """Техническая единица пространства — шестигранная призма"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    scene = models.ForeignKey(
        Scene,
        on_delete=models.CASCADE,
        related_name="chunks",
    )

    # Координаты в сетке
    grid_x = models.IntegerField()
    grid_z = models.IntegerField()
    grid_y = models.IntegerField(default=0)  # слой (вертикаль)

    # Мировые координаты центра чанка
    world_x = models.FloatField(default=0.0)
    world_y = models.FloatField(default=0.0)
    world_z = models.FloatField(default=0.0)

    CHUNK_TYPE_CHOICES = [
        ("void", "Пустота"),
        ("empty", "Пустой (только ландшафт)"),
        ("full", "Полный (с объектами)"),
    ]
    chunk_type = models.CharField(
        max_length=10, choices=CHUNK_TYPE_CHOICES, default="void"
    )

    # Данные чанка (JSON — объекты внутри)
    data = models.JSONField(default=dict, blank=True)

    # Статус загрузки (для real-time синхронизации)
    is_loaded = models.BooleanField(default=False)
    loaded_by = models.ManyToManyField(
        "users.User",
        related_name="loaded_chunks",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Чанк"
        verbose_name_plural = "Чанки"
        unique_together = [("scene", "grid_x", "grid_y", "grid_z")]
        indexes = [
            models.Index(fields=["scene", "grid_x", "grid_y", "grid_z"]),
            models.Index(fields=["world_x", "world_y", "world_z"]),
        ]

    def __str__(self):
        return f"Чанк ({self.grid_x}, {self.grid_y}, {self.grid_z})"

    def get_hex_center(self):
        """Вычисляет центр шестигранника в мировых координатах"""
        # Упрощённая формула для гексагональной сетки
        size = self.scene.world.chunk_size
        x = size * (self.grid_x * 1.5)
        z = size * (self.grid_z * 1.732 + (self.grid_x % 2) * 0.866)
        return (x, self.world_y, z)


class ChunkVertex(models.Model):
    """Точка схождения пирамид нескольких чанков"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    world = models.ForeignKey(
        World,
        on_delete=models.CASCADE,
        related_name="vertices",
    )

    # Мировые координаты
    world_x = models.FloatField()
    world_y = models.FloatField()
    world_z = models.FloatField()

    # Высота ландшафта в этой точке
    height = models.FloatField(default=0.0)

    # Материал (позже свяжем с assets.Material)
    material_id = models.UUIDField(null=True, blank=True)

    # Связанные чанки
    chunks = models.ManyToManyField(Chunk, related_name="vertices")

    class Meta:
        verbose_name = "Вершина стыковки"
        verbose_name_plural = "Вершины стыковки"
        indexes = [
            models.Index(fields=["world_x", "world_y", "world_z"]),
        ]

    def __str__(self):
        return f"Вершина ({self.world_x:.1f}, {self.world_y:.1f}, {self.world_z:.1f})"


class WorldObject(models.Model):
    """Объект внутри чанка"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    chunk = models.ForeignKey(
        Chunk,
        on_delete=models.CASCADE,
        related_name="world_objects",
    )

    name = models.CharField(max_length=200)
    object_type = models.CharField(
        max_length=30,
        choices=[
            ("mesh", "Меш"),
            ("light", "Источник света"),
            ("spawn", "Точка спавна"),
            ("trigger", "Триггер-зона"),
            ("empty", "Пустой (только трансформация)"),
        ],
        default="mesh",
    )

    # Трансформация (относительно центра чанка)
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    position_z = models.FloatField(default=0.0)

    rotation_x = models.FloatField(default=0.0)
    rotation_y = models.FloatField(default=0.0)
    rotation_z = models.FloatField(default=0.0)

    scale_x = models.FloatField(default=1.0)
    scale_y = models.FloatField(default=1.0)
    scale_z = models.FloatField(default=1.0)

    # Ссылки на ассеты (пока UUID, потом будут ForeignKey)
    mesh_asset_id = models.UUIDField(null=True, blank=True)
    material_asset_id = models.UUIDField(null=True, blank=True)

    # Дополнительные свойства
    properties = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Объект мира"
        verbose_name_plural = "Объекты мира"

    def __str__(self):
        return f"{self.name} ({self.object_type})"

    def get_world_position(self):
        """Абсолютная позиция в мире"""
        chunk_center = self.chunk.get_hex_center()
        return (
            chunk_center[0] + self.position_x,
            chunk_center[1] + self.position_y,
            chunk_center[2] + self.position_z,
        )
