from django.urls import path
from . import views

urlpatterns = [
    path("toolbar/", views.get_toolbar, name="toolbar"),
    path("toolbar/world/<uuid:world_id>/", views.get_toolbar, name="world_toolbar"),
]
