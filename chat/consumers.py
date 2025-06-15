from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Chat, Message
from accounts.utils import update_last_seen  # 👈 додаємо імпорт

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        self.user = self.scope["user"]
        chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
        participants = await database_sync_to_async(lambda: list(chat.participants.all()))()
        if self.user.is_anonymous or self.user not in participants:
            await self.close()
            return

        # 👇 оновити статус
        await self.update_last_seen()

        # Join room group
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 👇 оновити статус при виході
        await self.update_last_seen()

        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if self.user.is_anonymous:
            return

        # 👇 оновити статус при активності
        await self.update_last_seen()

        text_data_json = json.loads(text_data)
        message_text = text_data_json.get('message')

        if message_text:
            message = await self.create_message(self.user, message_text)

            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': message.text,
                    'username': self.user.username,
                    'user_id': self.user.id,
                }
            )

    @database_sync_to_async
    def create_message(self, user, message_text):
        chat = Chat.objects.get(id=self.chat_id)
        return Message.objects.create(chat=chat, sender=user, text=message_text)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # 👇 метод оновлення last_seen
    async def update_last_seen(self):
        from asgiref.sync import sync_to_async
        await sync_to_async(update_last_seen)(self.user)
