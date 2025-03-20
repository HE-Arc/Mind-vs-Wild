from django.urls import path
from .consumers import QuizConsumer

urlpatterns = [
    path("quiz/", QuizConsumer.as_asgi()),
]

