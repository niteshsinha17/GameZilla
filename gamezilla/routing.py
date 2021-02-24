from game.consumer import RoomConsumer
from snakeAndLadder.consumer import SNLConsumer
from django.urls import re_path
from ticTacToe.consumer import TACConsumer

websocket_urlpatterns = [
    re_path(r"^room/(?P<room_no>[\w\-]+)/$", RoomConsumer.as_asgi()),
    re_path(r"^SNL/(?P<room_no>[\w\-]+)/$", SNLConsumer.as_asgi()),
    re_path(r"^TAC/(?P<room_no>[\w\-]+)/$", TACConsumer.as_asgi()),
]
