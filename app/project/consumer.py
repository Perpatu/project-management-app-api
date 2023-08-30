import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ProjectNotiConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            "project_noti",
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json["type"]
        notification_data = text_data_json["notification_data"]
        project = text_data_json["project"]

        if message_type == "project_add":
            await self.project_add(notification_data, project)
        elif message_type == "project_remove":
            await self.project_remove(notification_data)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "project_noti",
            self.channel_name
        )

    async def project_add(self, event):
        event["notification_data"]["project"] = event["project"]
        message = event["notification_data"]
        message_json = json.dumps(message)
        await self.send(text_data=message_json)

    async def project_remove(self, event):
        message_json = json.dumps(event["notification_data"])
        await self.send(text_data=message_json)
