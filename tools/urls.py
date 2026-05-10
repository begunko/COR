# tools/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Панель инструментов (с опциональным world_id)
    path("toolbar/", views.get_toolbar, name="toolbar"),
    path("toolbar/world/<uuid:world_id>/", views.get_toolbar, name="world_toolbar"),
]