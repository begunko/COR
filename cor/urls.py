# cor/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Мониторинг — ДО админки, чтобы перехватить /admin/monitoring/
    path("", include("monitoring.urls")),
    # Админка Django
    path("admin/", admin.site.urls),
    # API
    path("api/v1/", include("tools.urls")),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("assets.urls")),
    path("api/", include("scenes.urls")),
    # Портал (главная)
    path("", TemplateView.as_view(template_name="portal/index.html")),
    # Редактор
    path("editor/", TemplateView.as_view(template_name="editor/index.html")),
    path(
        "editor/asset/<uuid:asset_id>/",
        TemplateView.as_view(template_name="editor/entity_editor.html"),
    ),
    path(
        "editor/tool/<uuid:tool_id>/",
        TemplateView.as_view(template_name="editor/entity_editor.html"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
