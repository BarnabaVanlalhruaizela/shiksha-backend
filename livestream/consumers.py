from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

from livestream.services.session_state import get_session_state, set_session_state
from .models import LiveSession


class LiveSessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.group_name = f"session_{self.session_id}"

        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # 🔥 GET STATE FROM REDIS
        state = await database_sync_to_async(get_session_state)(self.session_id)

        # 🔥 FALLBACK TO DB
        if not state:
            session = await database_sync_to_async(
                LiveSession.objects.get
            )(id=self.session_id)

            state = {
                "status": session.computed_status(),  # ✅ FIXED
                "teacher_left_at": (
                    session.teacher_left_at.isoformat()
                    if session.teacher_left_at else None
                ),
            }

            # save to Redis
            await database_sync_to_async(set_session_state)(session)

        # 🔥 SEND INITIAL STATE
        await self.send(text_data=json.dumps({
            "type": "initial_state",
            "data": state
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def session_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "session_update",
            "data": event["data"]
        }))
