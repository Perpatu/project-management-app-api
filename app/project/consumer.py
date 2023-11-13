import json
from channels.generic.websocket import AsyncWebsocketConsumer
from http.cookies import SimpleCookie
import urllib.parse
import uuid


def get_user_id(headers):
    cookie_header = None
    for header in headers:
        if header[0] == b'cookie':
            cookie_header = header[1]

    if cookie_header:
        cookie = SimpleCookie()
        cookie.load(cookie_header.decode('utf-8'))

        if 'user' in cookie:
            user_value = cookie['user'].value
            user_data_str = urllib.parse.unquote(user_value)
            user_data = json.loads(user_data_str)
            return user_data['id']


class ProjectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = get_user_id(self.scope['headers'])
        if user_id:
            await self.channel_layer.group_add(
                f'user_project_noti_{user_id}',
                self.channel_name
            )
            await self.accept()
            self.received_messages = set()

    async def disconnect(self, close_code):
        if hasattr(self, 'received_messages'):
            del self.received_messages

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        message = text_data_json

        if message_type == 'project_noti':
            await self.project_noti(message)

    async def project_noti(self, event):
        message = event['message']
        user_id = get_user_id(self.scope['headers'])

        if user_id:
            if message.get('message_id') not in self.received_messages:
                if 'message_id' in message:
                    self.received_messages.add(message['message_id'])
                await self.send(text_data=json.dumps({
                    'message': message,
                }))

    async def send_message(self, event):
        message = event['message']
        message_id = str(uuid.uuid4())
        message['message_id'] = message_id
        
        await self.send(text_data=json.dumps({
            'message': message,
        }))


class ProjectManageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = get_user_id(self.scope['headers'])
        if user_id:
            await self.channel_layer.group_add(
                f'project_manage_{user_id}',
                self.channel_name
            )
            await self.accept()
            self.received_messages = set()

    async def disconnect(self, close_code):
        if hasattr(self, 'received_messages'):
            del self.received_messages

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        message = text_data_json

        if message_type == 'project_manage':
            await self.project_manage(message)

    async def project_manage(self, event):
        message = event['message']
        user_id = get_user_id(self.scope['headers'])

        if user_id:
            if message.get('message_id') not in self.received_messages:
                if 'message_id' in message:
                    self.received_messages.add(message['message_id'])
            await self.send(text_data=json.dumps({
                    'message': message,
                }))

    async def send_message(self, event):
        message = event['message']        
        message_id = str(uuid.uuid4())
        message['message_id'] = message_id
        
        await self.send(text_data=json.dumps({
            'message': message,
        }))

