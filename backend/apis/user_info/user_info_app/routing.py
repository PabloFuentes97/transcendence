from django.urls import path
from user_info_app import consumers

websocket_urlpatterns = [
    path('ws/login/', consumers.LoginConsumer.as_asgi()),
]
