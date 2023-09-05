from django.urls import re_path
from project import consumer as project_conusmer
from file import consumer as file_consumer

websocket_urlpatterns = [
    re_path(r'ws/project-noti/', project_conusmer.ProjectConsumer.as_asgi()),
    re_path(r'ws/file-noti/', file_consumer.FileConsumer.as_asgi()),
]
