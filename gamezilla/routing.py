from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.conf.urls import url
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from game.consumer import RoomConsumer
from snakeAndLadder.consumer import SNLConsumer
from django.urls import re_path
application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    re_path(r'ws/room/(?P<room_no>[\w\-]+)/$',
                            RoomConsumer),
                    re_path(r'ws/SNL/(?P<room_no>[\w\-]+)/$',
                            SNLConsumer),
                ]
            )
        )
    )
})
