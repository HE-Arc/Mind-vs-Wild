from django.urls import path
from .consumers import RoomQuizConsumer

urlpatterns = [
    path("quiz/", RoomQuizConsumer.as_asgi()),
]

