# tools/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("toolbar/", views.get_toolbar, name="toolbar"),
    path("toolbar/world/<uuid:world_id>/", views.get_toolbar, name="world_toolbar"),
    path(
        "tools/<uuid:tool_id>/", views.tool_detail, name="tool_detail"
    ),  # ← ИСПРАВЛЕНО
]
