from django.urls import path
from .views import login_api, register_api, get_user

urlpatterns = [
    path('login/', login_api, name='login_api'),
    path('register/', register_api, name='register_api'),
    path('get/', get_user, name='get_user'),
]
