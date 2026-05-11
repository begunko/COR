# assets/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Asset


def asset_list(request):
    """Список всех активных ассетов"""
    assets = Asset.objects.filter(is_active=True).order_by("-updated_at")[:100]

    return JsonResponse(
        {
            "assets": [
                {
                    "id": str(a.id),
                    "name": a.name,
                    "children_count": a.children_count,
                    "has_animation": a.has_animation,
                    "tags": a.tags,
                    "data": a.data,
                    "animation": a.animation,
                }
                for a in assets
            ]
        }
    )


@csrf_exempt
def asset_detail(request, asset_id):
    """Получить или обновить ассет"""
    if request.method == "GET":
        try:
            asset = Asset.objects.get(id=asset_id)
            return JsonResponse(
                {
                    "id": str(asset.id),
                    "name": asset.name,
                    "description": asset.description,
                    "data": asset.data,
                    "animation": asset.animation,
                    "tags": asset.tags,
                }
            )
        except Asset.DoesNotExist:
            return JsonResponse({"error": "Asset not found"}, status=404)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            asset = Asset(id=asset_id)

        asset.name = data.get("name", asset.name)
        asset.description = data.get("description", asset.description)
        asset.data = data.get("data", asset.data)
        asset.animation = data.get("animation", asset.animation)
        asset.tags = data.get("tags", asset.tags)
        asset.save()

        return JsonResponse(
            {
                "status": "ok",
                "id": str(asset.id),
            }
        )

    return JsonResponse({"error": "Method not allowed"}, status=405)
