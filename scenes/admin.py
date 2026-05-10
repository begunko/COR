# scenes/admin.py
# ==============================================================================
# АДМИНКА ДЛЯ МИРОВ, ЧАНКОВ И ОБЪЕКТОВ
# ==============================================================================

from django.contrib import admin
from django.utils.html import format_html
from .models import World, Chunk, WorldObject


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "project",
        "chunk_size",
        "chunks_count",
        "objects_count",
        "created_at",
        "open_editor",
    ]
    list_filter = ["project", "created_at"]
    search_fields = ["name", "project__name"]
    actions = ["initialize_world"]

    fieldsets = (
        ("Основное", {"fields": ("name", "project", "chunk_size")}),
        (
            "Границы мира",
            {
                "fields": ("max_chunks_horizontal", "max_chunks_vertical"),
                "classes": ("collapse",),
            },
        ),
        (
            "Инструменты мира",
            {
                "fields": ("default_toolkits",),
                "description": "Список UUID наборов инструментов, доступных в этом мире. Объединяется с персональными наборами пользователя.",
            },
        ),
        (
            "Освещение",
            {
                "fields": ("lighting",),
                "description": "JSON с настройками освещения: ambient, sun, fog",
            },
        ),
    )

    def chunks_count(self, obj):
        return obj.chunks.filter(is_active=True).count()

    chunks_count.short_description = "Активных чанков"

    def objects_count(self, obj):
        return obj.world_objects.count()

    objects_count.short_description = "Объектов"

    def open_editor(self, obj):
        """Кнопка для открытия мира в редакторе — переходит в центральный чанк (0,0,0)"""
        center_chunk = obj.chunks.filter(
            is_active=True,
            grid_q=0,
            grid_r=0,
            grid_y=0,
        ).first()

        if center_chunk:
            url = f"/editor/?world_id={obj.id}&chunk_id={center_chunk.id}"
            return format_html(
                '<a href="{}" target="_blank" style="background: #ff6600; color: white; '
                'padding: 5px 15px; border-radius: 5px; text-decoration: none;">▶ Открыть</a>',
                url,
            )
        return "Нет центрального чанка"

    open_editor.short_description = "Редактор"

    def initialize_world(self, request, queryset):
        """Создаёт стартовый чанк и активирует соседей для выбранных миров"""
        for world in queryset:
            world.initialize_starting_chunk()
        self.message_user(
            request, "Центральный чанк и 18 соседей (сфера) созданы и активированы"
        )

    initialize_world.short_description = "🌐 Инициализировать мир (создать чанки)"


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = [
        "grid_q",
        "grid_r",
        "grid_y",
        "world",
        "chunk_type",
        "is_active",
        "is_loaded",
        "objects_in_chunk",
        "open_in_editor",
    ]
    list_filter = ["chunk_type", "is_active", "is_loaded", "world"]
    search_fields = ["world__name"]
    actions = ["activate_chunk_with_neighbors", "deactivate_chunk"]

    fieldsets = (
        ("Координаты", {"fields": ("world", "grid_q", "grid_r", "grid_s", "grid_y")}),
        (
            "Мировые координаты центра",
            {
                "fields": ("world_x", "world_y", "world_z"),
                "classes": ("collapse",),
            },
        ),
        ("Тип и статус", {"fields": ("chunk_type", "is_active", "is_loaded")}),
        (
            "Вершины стыковки",
            {
                "fields": (
                    ("top_vertex_x", "top_vertex_y", "top_vertex_z"),
                    ("bottom_vertex_x", "bottom_vertex_y", "bottom_vertex_z"),
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def objects_in_chunk(self, obj):
        """Считает объекты в чанке через WorldObject"""
        if not obj.world:
            return 0
        return WorldObject.objects.filter(
            world=obj.world,
            chunk_q=obj.grid_q,
            chunk_r=obj.grid_r,
            chunk_y=obj.grid_y,
        ).count()

    objects_in_chunk.short_description = "Объектов"

    def open_in_editor(self, obj):
        """Кнопка для открытия чанка в редакторе"""
        world_id = obj.world.id if obj.world else ""
        url = f"/editor/?world_id={world_id}&chunk_id={obj.id}"
        return format_html(
            '<a href="{}" target="_blank" style="background: #ff6600; color: white; '
            'padding: 3px 12px; border-radius: 5px; text-decoration: none;">▶</a>',
            url,
        )

    open_in_editor.short_description = ""

    def activate_chunk_with_neighbors(self, request, queryset):
        """Активирует выбранные чанки И их соседей"""
        total_activated = 0
        for chunk in queryset:
            chunk.is_active = True
            chunk.save(update_fields=["is_active"])
            total_activated += 1

            # Активируем соседей
            neighbors = chunk.activate_neighbors()
            total_activated += len(neighbors)

        self.message_user(
            request, f"Активировано чанков: {total_activated} (включая соседей)"
        )

    activate_chunk_with_neighbors.short_description = "🔷 Активировать чанк + соседей"

    def deactivate_chunk(self, request, queryset):
        """Деактивирует выбранные чанки"""
        count = queryset.update(is_active=False, is_loaded=False)
        self.message_user(request, f"Деактивировано чанков: {count}")

    deactivate_chunk.short_description = "🔲 Деактивировать чанк"


@admin.register(WorldObject)
class WorldObjectAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "object_type",
        "world",
        "chunk_coords_display",
        "position_display",
        "created_by",
        "updated_at",
    ]
    list_filter = ["object_type", "world", "created_at"]
    search_fields = ["name", "world__name", "properties"]
    readonly_fields = ["chunk_q", "chunk_r", "chunk_y", "bounding_radius"]

    fieldsets = (
        ("Основное", {"fields": ("world", "name", "object_type", "created_by")}),
        (
            "Трансформация",
            {
                "fields": (
                    ("position_x", "position_y", "position_z"),
                    ("rotation_x", "rotation_y", "rotation_z"),
                    ("scale_x", "scale_y", "scale_z"),
                )
            },
        ),
        (
            "Вычисляемые координаты соты",
            {
                "fields": ("chunk_q", "chunk_r", "chunk_y", "bounding_radius"),
                "classes": ("collapse",),
            },
        ),
        (
            "Свойства (JSON)",
            {
                "fields": ("properties",),
                "description": "Геометрия, материал, теги, скрипты. Пример: "
                '{"geometry": {"type": "BoxGeometry", "params": [1,1,1]}, '
                '"material": {"color": "#ff6600"}, "tags": ["сцена-костёр"]}',
            },
        ),
    )

    def chunk_coords_display(self, obj):
        return f"({obj.chunk_q}, {obj.chunk_r}, {obj.chunk_y})"

    chunk_coords_display.short_description = "Сота"

    def position_display(self, obj):
        return f"({obj.position_x:.1f}, {obj.position_y:.1f}, {obj.position_z:.1f})"

    position_display.short_description = "Позиция"
