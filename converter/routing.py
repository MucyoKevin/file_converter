"""
WebSocket URL routing for converter app
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/conversion/(?P<conversion_id>[0-9a-f-]+)/$', consumers.ConversionConsumer.as_asgi()),
]

