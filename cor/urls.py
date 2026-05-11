# cor/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # API — ВАЖНЫЙ ПОРЯДОК!
    path("api/v1/", include("tools.urls")),  # ← должно быть
    path("api/v1/", include("users.urls")),  # ← должно быть
    path("api/v1/", include("assets.urls")),  # ← ДОБАВИТЬ! (если нет)
    path("api/", include("scenes.urls")),  # ← должно быть
    # Редакторы
    path("editor/", TemplateView.as_view(template_name="editor/index.html")),
    path(
        "editor/asset/<uuid:asset_id>/",
        TemplateView.as_view(template_name="editor/entity_editor.html"),
    ),
    path(
        "editor/tool/<uuid:tool_id>/",
        TemplateView.as_view(template_name="editor/entity_editor.html"),
    ),
    # Портал
    path("", TemplateView.as_view(template_name="portal/index.html")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
