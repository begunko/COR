from django.contrib import admin
from .models import World, Scene, Chunk, ChunkVertex, WorldObject, WorldLighting


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "project",
        "grid_type",
        "chunk_size",
    ]


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "world",
        "order",
    ]


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "scene",
        "grid_x",
        "grid_y",
        "grid_z",
        "chunk_type",
        "is_loaded",
    ]
    list_filter = [
        "chunk_type",
        "is_loaded",
    ]


@admin.register(ChunkVertex)
class ChunkVertexAdmin(admin.ModelAdmin):
    list_display = [
        "world_x",
        "world_y",
        "world_z",
        "height",
    ]


@admin.register(WorldObject)
class WorldObjectAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "object_type",
        "chunk",
        "position_x",
        "position_y",
        "position_z",
    ]


@admin.register(WorldLighting)
class WorldLightingAdmin(admin.ModelAdmin):
    list_display = [
        "world",
        "sun_enabled",
        "sun_intensity",
        "ambient_intensity",
    ]
