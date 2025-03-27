from django.urls import re_path
from .consumers import RoomQuizConsumer

websocket_urlpatterns = [
    re_path(r'^ws/room/(?P<room_id>\d+)/$', RoomQuizConsumer.as_asgi()),
]
