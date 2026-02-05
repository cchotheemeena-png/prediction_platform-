import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameRound

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("game_updates", self.channel_name)
        await self.accept()
        await self.send_round_update()

    async def send_round_update(self):
        round_data = await self.get_current_round()
        await self.send(text_data=json.dumps(round_data))

    @database_sync_to_async
    def get_current_round(self):
        round_obj = GameRound.objects.filter(status__in=['active', 'locked']).first()
        if round_obj:
            return {
                'round_id': round_obj.id,
                'status': round_obj.status,
                'seconds_remaining': round_obj.seconds_remaining
            }
        return {}
