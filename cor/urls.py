from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "api/v1/",
        include("users.urls"),
    ),
    path(
        "editor/",
        TemplateView.as_view(template_name="editor/index.html"),
    ),
    path(
        "api/v1/",
        include("tools.urls"),
    ),
]

# Только для разработки!
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
