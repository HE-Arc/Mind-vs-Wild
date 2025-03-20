from django.urls import path
from quiz.routing import websocket_urlpatterns

websocket_urlpatterns = websocket_urlpatterns  # Import depuis quiz

urlpatterns = [
    path('ws/', websocket_urlpatterns),
]
