# import app.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from msgs.consumers import MessegeRoomConsumer
from channels.auth import AuthMiddlewareStack


websocket_urlpatterns = [
    re_path(r'ws/msg/(?P<room_name>\w+)/$', MessegeRoomConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
            URLRouter(        
                    websocket_urlpatterns
            )
        )
})