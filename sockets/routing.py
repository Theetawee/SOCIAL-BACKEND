from django.urls import path
from sockets.consumers import Notifications

websocket_urlpatterns = [
    path("", Notifications.as_asgi()),
]
