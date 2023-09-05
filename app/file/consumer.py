import json
from channels.generic.websocket import AsyncWebsocketConsumer


class FileConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "queue_group",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "queue_group",
            self.channel_name
        )

    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        message = text_data_json

        if message_type == 'queue_add':
            await self.queue_add(message)
        elif message_type == 'file_delete':
            await self.file_delete(message)

    async def queue_add(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))

    async def file_delete(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))
