from django.urls import re_path

from .consumers import ChatConsumer

ws_patterns = [
    re_path('ws/chat/(?P<id>[0-9a-f-]+)/$'  , ChatConsumer.as_asgi()),
]