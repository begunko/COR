from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/chunk/(?P<chunk_id>[^/]+)/$",
        consumers.ChunkConsumer.as_asgi(),
    ),
]
