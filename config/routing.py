from channels.routing import ProtocolTypeRouter, URLRouter
# import app.routing
from django.urls import re_path
from msgs.consumers import MessegeRoomConsumer

websocket_urlpatterns = [
    re_path(r'^ws/(?P<room_name>[^/]+)/$', MessegeRoomConsumer.as_asgi()),
]
