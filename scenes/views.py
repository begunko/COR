import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chunk, WorldObject, World


@csrf_exempt
def save_chunk(request, chunk_id):
    """Сохраняет объекты чанка в WorldObject (отдельные записи)"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        chunk_uuid = uuid.UUID(chunk_id)
    except ValueError:
        return JsonResponse({"error": "Invalid chunk UUID"}, status=400)

    chunk, created = Chunk.objects.get_or_create(
        id=chunk_uuid,
        defaults={"chunk_type": "full", "is_active": True},
    )

    # Привязываем чанк к миру
    world_id = data.get("world_id")
    if world_id and not chunk.world_id:
        try:
            world = World.objects.get(id=world_id)
            chunk.world = world
            chunk.save()
        except Exception as e:
            print(f"Не удалось привязать чанк к миру: {e}")

    objects_data = data.get("objects", {})
    saved_count = 0

    for obj_id, obj_data in objects_data.items():
        pos = obj_data.get("position", {})
        rot = obj_data.get("rotation", {})
        scl = obj_data.get("scale", {})

        WorldObject.objects.update_or_create(
            client_id=obj_id,
            defaults={
                "chunk": chunk,
                "name": obj_data.get("type", "object"),
                "object_type": "mesh",
                "position_x": pos.get("x", 0),
                "position_y": pos.get("y", 0),
                "position_z": pos.get("z", 0),
                "rotation_x": rot.get("x", 0),
                "rotation_y": rot.get("y", 0),
                "rotation_z": rot.get("z", 0),
                "scale_x": scl.get("x", 1),
                "scale_y": scl.get("y", 1),
                "scale_z": scl.get("z", 1),
                "properties": obj_data.get("params", {}),
            },
        )
        saved_count += 1

    chunk.data = objects_data
    chunk.chunk_type = "full"
    chunk.save()

    return JsonResponse(
        {
            "status": "ok",
            "objects_saved": saved_count,
        }
    )


def load_chunk(request, chunk_id):
    """Загружает объекты из WorldObject"""
    try:
        chunk_uuid = uuid.UUID(chunk_id)
    except ValueError:
        return JsonResponse({"objects": {}, "chunk_type": "void"})

    try:
        chunk = Chunk.objects.get(id=chunk_uuid)
    except Chunk.DoesNotExist:
        return JsonResponse({"objects": {}, "chunk_type": "void"})

    objects_qs = WorldObject.objects.filter(chunk=chunk)

    if objects_qs.exists():
        result = {}
        for obj in objects_qs:
            result[obj.client_id or str(obj.id)] = {
                "color": obj.properties.get("color", "#ff6600"),
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
                "scale": {"x": obj.scale_x, "y": obj.scale_y, "z": obj.scale_z},
                "type": obj.properties.get("geometry", "BoxGeometry"),
                "params": obj.properties,
            }
        return JsonResponse(
            {
                "chunk_id": str(chunk.id),
                "objects": result,
                "chunk_type": chunk.chunk_type,
            }
        )

    return JsonResponse(
        {
            "chunk_id": str(chunk.id),
            "objects": chunk.data if isinstance(chunk.data, dict) else {},
            "chunk_type": chunk.chunk_type,
        }
    )


def user_worlds(request):
    """Список миров"""
    worlds = World.objects.all()[:10]
    return JsonResponse(
        {
            "worlds": [
                {
                    "id": str(w.id),
                    "name": w.name,
                    "chunks_count": w.chunks.filter(is_active=True).count(),
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
