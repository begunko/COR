# cor/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Админка
    path("admin/", admin.site.urls),
    # API — порядок важен: более специфичные маршруты первыми
    path("api/v1/", include("tools.urls")),  # панель инструментов
    path("api/v1/", include("users.urls")),  # авторизация
    path("api/", include("scenes.urls")),  # чанки и объекты
    # Страницы
    path("editor/", TemplateView.as_view(template_name="editor/index.html")),
    path("", TemplateView.as_view(template_name="portal/index.html")),
]

# Статика (только для разработки)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
