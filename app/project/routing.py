from django.urls import re_path
from . import consumer


websocket_urlpatterns = [
    re_path(r'ws/project-noti/', consumer.ProjectNotiConsumer.as_asgi()),
]