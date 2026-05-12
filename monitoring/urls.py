# monitoring/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("monitoring/", views.monitoring_page, name="monitoring_page"),
    path("api/monitoring/", views.monitoring_api, name="monitoring_api"),
]
