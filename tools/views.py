# tools/views.py
# ==============================================================================
# API: НАБОРЫ ИНСТРУМЕНТОВ ДЛЯ ПАНЕЛИ РЕДАКТОРА
# ==============================================================================

import json  # ← ДОБАВИТЬ
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt  # ← ДОБАВИТЬ
from .models import Tool, Toolkit  # ← ДОБАВИТЬ Tool


@require_GET
def get_toolbar(request, world_id=None):
    """
    Возвращает наборы инструментов.
    - Для гостя: все активные наборы
    - Для пользователя: его персональные + наборы мира
    """
    user = request.user

    # ==========================================================================
    # СОБИРАЕМ НАБОРЫ
    # ==========================================================================

    toolkit_ids = set()

    # 1. Персональные наборы (только для залогиненных)
    if user.is_authenticated and hasattr(user, "tools_config"):
        user_toolkit_ids = user.tools_config.get("active_toolkits", [])
        toolkit_ids.update(user_toolkit_ids)

    # 2. Наборы мира
    if world_id:
        try:
            from scenes.models import World

            world = World.objects.get(id=world_id)
            world_toolkit_ids = world.default_toolkits or []
            toolkit_ids.update(world_toolkit_ids)
        except Exception:
            pass

    # 3. Если ничего не настроено — отдаём ВСЕ активные наборы
    if not toolkit_ids:
        toolkits = Toolkit.objects.filter(is_active=True).order_by("order", "name")
    else:
        toolkits = Toolkit.objects.filter(
            id__in=toolkit_ids,
            is_active=True,
        ).order_by("order", "name")

    # ==========================================================================
    # ФОРМИРУЕМ ОТВЕТ
    # ==========================================================================

    result = []
    for toolkit in toolkits:
        tools_list = []
        for tool in toolkit.tools.filter(is_active=True).order_by("order", "name"):
            tools_list.append(
                {
                    "id": str(tool.id),
                    "name": tool.name,
                    "display_name": tool.display_name,
                    "tool_type": tool.tool_type,
                    "default_params": tool.default_params,
                    "order": tool.order,
                }
            )

        result.append(
            {
                "id": str(toolkit.id),
                "name": toolkit.name,
                "icon": toolkit.icon,
                "description": toolkit.description,
                "order": toolkit.order,
                "tools": tools_list,
            }
        )

    return JsonResponse(
        {
            "toolkits": result,
        }
    )


@csrf_exempt
def tool_detail(request, tool_id):
    """Получить или обновить Tool (для редактора)"""
    try:
        tool = Tool.objects.get(id=tool_id)
    except Tool.DoesNotExist:
        return JsonResponse({"error": "Tool not found"}, status=404)

    if request.method == "GET":
        # Оборачиваем default_params в children для совместимости
        params = tool.default_params or {}
        if params.get("geometry") == "Group" and "children" in params:
            children = params["children"]
        elif params.get("geometry"):
            # Простой объект — заворачиваем в массив из одного элемента
            children = [params]
        else:
            children = []

        return JsonResponse({
            "id": str(tool.id),
            "name": tool.name,
            "display_name": tool.display_name,
            "default_params": tool.default_params,
            "children": children,  # ← добавляем это поле
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        tool.default_params = data.get("default_params", tool.default_params)
        tool.save(update_fields=["default_params"])

        return JsonResponse({"status": "ok", "id": str(tool.id)})

    return JsonResponse({"error": "Method not allowed"}, status=405)
