import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Profile
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.friend_username = self.scope['url_route']['kwargs']['username']
        # Create a unique group name for David and Jack
        self.room_group_name = f'chat_{min(self.scope["user"].username, self.friend_username)}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        print(f"--- Message Received: {text_data} ---") # Check terminal for this
        data = json.loads(text_data)
        message = data['message']

        try:
            # 1. Save to Database
            print("Saving to DB...")
            await self.save_message(
                sender=self.scope['user'],
                receiver_name=self.friend_username,
                original=message,
                translated=message, # Temporary: use original until AI is fixed
                english="Translation pending..."
            )

            # 2. Broadcast to Group
            print("Broadcasting to group...")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.scope['user'].username,
                    'english': "Translation pending..."
                }
            )
        except Exception as e:
            print(f"ERROR IN CONSUMER: {e}") # This will tell you why it's failing

    async def chat_message(self, event):
        print("--- Handler Triggered: Sending to WebSocket ---")
        
        # Extract data from the event
        message = event['message']
        sender = event['sender']
        english = event.get('english', '')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'english': english
        }))

    @database_sync_to_async
    def save_message(self, sender, receiver_name, original, translated, english):
        receiver = User.objects.get(username=receiver_name)
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            original_text=original,
            translated_text=translated,
            english_text=english
        )