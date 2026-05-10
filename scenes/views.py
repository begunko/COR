# scenes/views.py
# ==============================================================================
# API: СОХРАНЕНИЕ И ЗАГРУЗКА ОБЪЕКТОВ ЧАНКА
# ==============================================================================

import json
import uuid as uuid_module  # для WorldObject.id
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chunk, WorldObject, World


@csrf_exempt
def save_chunk(request, chunk_id):
    """
    Сохраняет объекты чанка.
    chunk_id уже UUID (Django распарсил из <uuid:chunk_id>)
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Получаем или создаём чанк (chunk_id уже UUID)
    chunk, chunk_created = Chunk.objects.get_or_create(
        id=chunk_id,
        defaults={
            "chunk_type": "full",
            "is_active": True,
        },
    )

    # Привязываем чанк к миру, если указан world_id
    world_id = data.get("world_id")
    world = None
    if world_id:
        try:
            world = World.objects.get(id=world_id)
            if not chunk.world_id:
                chunk.world = world
                chunk.save(update_fields=["world"])
        except World.DoesNotExist:
            return JsonResponse({"error": "World not found"}, status=404)

    if not world:
        world = chunk.world

    if not world:
        return JsonResponse({"error": "World not specified"}, status=400)

    # Сохраняем объекты
    objects_data = data.get("objects", {})
    saved_count = 0
    updated_count = 0

    for client_id, obj_data in objects_data.items():
        pos = obj_data.get("position", {})
        rot = obj_data.get("rotation", {})
        scl = obj_data.get("scale", {})
        params = obj_data.get("params", {})

        # Строим properties
        properties = {
            "geometry": {
                "type": params.get("geometry", obj_data.get("type", "BoxGeometry")),
                "params": params.get("params", []),
            },
            "material": {
                "color": obj_data.get("color", "#ff6600"),
            },
            "tags": obj_data.get("tags", []),
        }

        for key in ["wireframe", "roughness", "metalness", "opacity"]:
            if key in params:
                properties["material"][key] = params[key]

        obj, created = WorldObject.objects.update_or_create(
            world=world,
            client_id=client_id,
            defaults={
                "name": obj_data.get("type", "object"),
                "object_type": "group" if params.get("geometry") == "Group" else "mesh",
                "position_x": pos.get("x", 0),
                "position_y": pos.get("y", 0),
                "position_z": pos.get("z", 0),
                "rotation_x": rot.get("x", 0),
                "rotation_y": rot.get("y", 0),
                "rotation_z": rot.get("z", 0),
                "scale_x": scl.get("x", 1),
                "scale_y": scl.get("y", 1),
                "scale_z": scl.get("z", 1),
                "properties": properties,
            },
        )

        if created:
            saved_count += 1
        else:
            updated_count += 1

    chunk.chunk_type = "full"
    chunk.save(update_fields=["chunk_type"])

    return JsonResponse(
        {
            "status": "ok",
            "objects_saved": saved_count,
            "objects_updated": updated_count,
        }
    )


def load_chunk(request, chunk_id):
    """
    Загружает объекты чанка.
    chunk_id уже UUID (Django распарсил из <uuid:chunk_id>)
    """
    try:
        chunk = Chunk.objects.get(id=chunk_id)
    except Chunk.DoesNotExist:
        return JsonResponse({"objects": {}, "chunk_type": "void"})

    # Если у чанка нет мира — возвращаем пусто
    if not chunk.world:
        return JsonResponse(
            {
                "chunk_id": str(chunk.id),
                "chunk_type": chunk.chunk_type,
                "objects": {},
            }
        )

    objects_qs = WorldObject.objects.filter(
        world=chunk.world,
        chunk_q=chunk.grid_q,
        chunk_r=chunk.grid_r,
        chunk_y=chunk.grid_y,
    )

    result = {}
    for obj in objects_qs:
        obj_id = str(obj.id)
        props = obj.properties or {}
        geometry = props.get("geometry", {})
        material = props.get("material", {})

        result[obj_id] = {
            "client_id": obj.client_id,
            "type": geometry.get("type", "BoxGeometry"),
            "position": {
                "x": obj.position_x,
                "y": obj.position_y,
                "z": obj.position_z,
            },
            "rotation": {
                "x": obj.rotation_x,
                "y": obj.rotation_y,
                "z": obj.rotation_z,
            },
            "scale": {
                "x": obj.scale_x,
                "y": obj.scale_y,
                "z": obj.scale_z,
            },
            "color": material.get("color", "#ff6600"),
            "params": {
                "geometry": geometry.get("type", "BoxGeometry"),
                "color": material.get("color", "#ff6600"),
                **{k: v for k, v in geometry.items() if k != "type"},
                **{k: v for k, v in material.items() if k != "color"},
            },
            "tags": props.get("tags", []),
        }

    return JsonResponse(
        {
            "chunk_id": str(chunk.id),
            "chunk_type": chunk.chunk_type,
            "objects": result,
        }
    )


def user_worlds(request):
    worlds = World.objects.all()[:20]

    return JsonResponse(
        {
            "worlds": [
                {
                    "id": str(w.id),
                    "name": w.name,
                    "chunks_count": w.chunks.filter(is_active=True).count(),
                    "objects_count": w.world_objects.count(),
                    "first_chunk_id": (
                        str(w.chunks.filter(is_active=True).first().id)
                        if w.chunks.filter(is_active=True).exists()
                        else None
                    ),
                }
                for w in worlds
            ]
        }
    )
