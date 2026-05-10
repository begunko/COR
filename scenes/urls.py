# scenes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("api/chunk/<uuid:chunk_id>/save/", views.save_chunk, name="save_chunk"),
    path("api/chunk/<uuid:chunk_id>/load/", views.load_chunk, name="load_chunk"),
    path("api/v1/worlds/", views.user_worlds, name="user_worlds"),
]
