from django.shortcuts import render


def editor_view(request, mode="world", entity_id=None):
    """
    Единый редактор для всех режимов.
    Режимы:
    - 'world'      — редактор мира (по умолчанию)
    - 'asset'      — редактор ассета
    - 'tool'       — редактор инструмента
    - 'character'  — редактор персонажа (будет позже)
    """
    context = {
        "mode": mode,
        "entity_id": str(entity_id) if entity_id else "",
    }
    return render(request, "editor/index.html", context)
