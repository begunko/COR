from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Tool, UserToolProfile, WorldToolProfile


@api_view(["GET"])
def get_toolbar(request, world_id=None):
    """
    Возвращает список инструментов для текущего пользователя.
    Если указан world_id — учитывает настройки мира.
    """
    user = request.user

    # Базовые инструменты пользователя
    user_tools = []
    if hasattr(user, "tool_profile"):
        if user.tool_profile.tools.exists():
            user_tools = list(user.tool_profile.tools.filter(is_active=True))

    # Если нет профиля или он пуст — берём инструменты available_for_all
    if not user_tools:
        user_tools = list(Tool.objects.filter(available_for_all=True, is_active=True))

    # Если указан мир — проверяем его настройки
    world_tools = []
    mode = "extend"
    if world_id:
        try:
            world_profile = WorldToolProfile.objects.get(world_id=world_id)
            world_tools = list(world_profile.tools.filter(is_active=True))
            mode = world_profile.mode
        except WorldToolProfile.DoesNotExist:
            pass

    if mode == "override" and world_tools:
        final_tools = world_tools
    else:
        # extend: объединяем, убираем дубликаты
        tool_ids = {t.id for t in user_tools}
        for t in world_tools:
            if t.id not in tool_ids:
                user_tools.append(t)
        final_tools = user_tools

    # Формируем ответ
    return Response(
        {
            "tools": [
                {
                    "id": str(tool.id),
                    "name": tool.name,
                    "display_name": tool.display_name,
                    "tool_type": tool.tool_type,
                    "default_params": tool.default_params,
                    "icon_svg": tool.icon_svg,
                    "icon_class": tool.icon_class,
                    "order": tool.order,
                }
                for tool in sorted(final_tools, key=lambda t: t.order)
            ]
        }
    )
