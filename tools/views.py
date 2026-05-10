# tools/views.py
# ==============================================================================
# API: НАБОРЫ ИНСТРУМЕНТОВ ДЛЯ ПАНЕЛИ РЕДАКТОРА
# ==============================================================================

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Toolkit


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
