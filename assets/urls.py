# assets/urls.py — должно быть ТОЧНО так:
from django.urls import path
from . import views

urlpatterns = [
    path("assets/", views.asset_list, name="asset_list"),
    path("assets/<uuid:asset_id>/", views.asset_detail, name="asset_detail"),
]
