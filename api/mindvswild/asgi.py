import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindvswild.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

def get_application():
    from quiz.routing import websocket_urlpatterns
    
    return ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    })

application = get_application()
