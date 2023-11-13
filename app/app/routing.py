from django.urls import re_path
from project import consumer as project_conusmer
from file import consumer as file_consumer

websocket_urlpatterns = [
    re_path(r'ws/project-noti/', project_conusmer.ProjectConsumer.as_asgi()),
    re_path(r'ws/project-manage/', project_conusmer.ProjectManageConsumer.as_asgi()),
    re_path(r'ws/file-noti/', file_consumer.FileNotiConsumer.as_asgi()),
    re_path(r'ws/file-project/', file_consumer.FileProjectConsumer.as_asgi()),
    re_path(r'ws/file-department/', file_consumer.FileDepartmentConsumer.as_asgi()),
]
