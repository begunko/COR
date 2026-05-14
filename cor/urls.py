# cor/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Портал (главная) — должен быть ПЕРВЫМ
    path("", TemplateView.as_view(template_name="portal/index.html"), name="portal"),
    # Мониторинг
    path("monitoring/", include("monitoring.urls")),
    # Админка Django
    path("admin/", admin.site.urls),
    # API
    path("api/v1/", include("tools.urls")),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("assets.urls")),
    path("api/", include("scenes.urls")),
    # Редактор
    # ЕДИНЫЙ РЕДАКТОР
    path("editor/", include("editor.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
