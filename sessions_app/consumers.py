import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PrivateSessionChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for private session real-time chat."""

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.group_name = f"private_session_chat_{self.session_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_message(self, event):
        """Receives broadcast from views.send_chat_message and forwards to WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "data": event["data"],
        }))
