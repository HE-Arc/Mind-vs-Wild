from django.urls import path
from quiz.routing import websocket_urlpatterns

websocket_urlpatterns = websocket_urlpatterns  # Import from quiz.routing

urlpatterns = [
    path('ws/', websocket_urlpatterns),
]
