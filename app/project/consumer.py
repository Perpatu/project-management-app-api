import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ProjectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "project_group",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "project_group",
            self.channel_name
        )

    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        message = text_data_json

        if message_type == 'project_add':
            await self.project_add(message)
        elif message_type == 'project_delete':
            await self.project_delete(message)

    async def project_add(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))

    async def project_delete(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))
