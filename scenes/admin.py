from django.contrib import admin
from django.utils.html import format_html
from .models import World, Scene, Chunk, ChunkVertex, WorldObject, WorldLighting


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "project",
        "grid_type",
        "chunk_size",
        "created_at",
        "open_editor",
    ]
    actions = ["initialize_world"]

    def open_editor(self, obj):
        """Кнопка для открытия мира в редакторе"""
        first_chunk = obj.chunks.filter(is_active=True).first()
        if first_chunk:
            url = f"/editor/?world_id={obj.id}&chunk_id={first_chunk.id}"
            return format_html(
                '<a href="{}" target="_blank" style="background: #ff6600; color: white; padding: 5px 15px; border-radius: 5px; text-decoration: none;">▶ Открыть</a>',
                url,
            )
        return "Нет чанков"

    open_editor.short_description = "Редактор"

    def initialize_world(self, request, queryset):
        """Создаёт стартовый чанк и соседей для выбранных миров"""
        for world in queryset:
            world.initialize_starting_chunk()
        self.message_user(request, "Стартовый чанк и соседи созданы")

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
        "open_in_editor",
    ]
    list_filter = ["chunk_type", "is_active", "world"]
    actions = ["activate_neighbors_action"]

    def open_in_editor(self, obj):
        """Кнопка для открытия чанка в редакторе"""
        url = f"/editor/?chunk_id={obj.id}&world_id={obj.world.id if obj.world else ''}"
        return format_html(
            '<a href="{}" target="_blank" style="background: #ff6600; color: white; padding: 3px 12px; border-radius: 5px; text-decoration: none;">▶</a>',
            url,
        )

    open_in_editor.short_description = ""

    def activate_neighbors_action(self, request, queryset):
        total = 0
        for chunk in queryset:
            created = chunk.activate_neighbors()
            total += len(created)
        self.message_user(request, f"Создано {total} соседних чанков")

    activate_neighbors_action.short_description = (
        "🔷 Активировать соседние чанки (соты)"
    )


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ["name", "world", "order"]


@admin.register(ChunkVertex)
class ChunkVertexAdmin(admin.ModelAdmin):
    list_display = ["world_x", "world_y", "world_z", "height"]


@admin.register(WorldObject)
class WorldObjectAdmin(admin.ModelAdmin):
    list_display = ["name", "object_type", "chunk"]


@admin.register(WorldLighting)
class WorldLightingAdmin(admin.ModelAdmin):
    list_display = ["world", "sun_enabled", "sun_intensity", "ambient_intensity"]
