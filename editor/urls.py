from django.urls import path
from . import views

urlpatterns = [
    # Без параметров — редактор мира
    path("", views.editor_view, name="editor"),
    # С параметрами — редактор сущности
    path("<str:mode>/<uuid:entity_id>/", views.editor_view, name="editor_entity"),
]
