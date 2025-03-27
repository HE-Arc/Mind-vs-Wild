from django.urls import re_path
from .consumers import RoomQuizConsumer

websocket_urlpatterns = [
    re_path(r'^ws/room/(?P<room_code>[0-9a-f-]{8}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{12})/$', RoomQuizConsumer.as_asgi()),
]
