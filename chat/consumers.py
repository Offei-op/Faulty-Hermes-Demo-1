import json
import os
import asyncio
from google import genai
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Profile
from django.contrib.auth.models import User

# Initialize Gemini Client
client = genai.Client(api_key='AIzaSyCQuMNkuIRW4eqCcddd17sVX8kawasAUtU')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.friend_username = self.scope['url_route']['kwargs']['username']
        # Group name is the sorted usernames joined
        self.room_group_name = f'chat_{"".join(sorted([self.scope["user"].username, self.friend_username]))}'
        print(f"DEBUG: {self.scope['user'].username} CONNECTING to group: {self.room_group_name}")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f"DEBUG: {self.scope['user'].username} DISCONNECTED from group: {self.room_group_name}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']
        print(f"DEBUG: {sender.username} RECEIVED message: '{message}' for group: {self.room_group_name}")

        try:
            # Fetch recipient's language
            target_lang = await self.get_receiver_language(self.friend_username)
            print(f"DEBUG: Target language for {self.friend_username} is {target_lang}")

            # AI Translation Wrapper
            def perform_translation(text, lang):
                # Translate to target language
                t_prompt = f"Translate the following to {lang}. Output ONLY the raw translation.\n\n{text}"
                t_response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=t_prompt
                )
                trans_text = t_response.text.strip()

                # Translate to English for shadow bubble
                if lang == 'en':
                    eng_text = trans_text
                else:
                    e_prompt = f"Translate the following to English. Output ONLY the raw translation.\n\n{text}"
                    e_response = client.models.generate_content(
                        model="gemini-3-flash-preview",
                        contents=e_prompt
                    )
                    eng_text = e_response.text.strip()
                
                return trans_text, eng_text

            # Execute AI call in thread
            translated, english = await asyncio.to_thread(perform_translation, message, target_lang)
            print(f"DEBUG: Success! Translated: '{translated}' | English: '{english}'")

        except Exception as e:
            print(f"[AI ERROR] {e}")
            translated = message
            english = "[Translation Error]"

        # 1. Save to Database
        await self.save_message(
            sender=sender,
            receiver_name=self.friend_username,
            original=message,
            translated=translated,
            english=english
        )

        # 2. Broadcast to Group
        print(f"DEBUG: Sending BROADCAST to group {self.room_group_name}...")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'translated': translated,
                'sender': sender.username,
                'english': english
            }
        )

    async def chat_message(self, event):
        print(f"DEBUG: {self.scope['user'].username} chat_message HANDLER triggered!")
        # Extract data from the event
        message = event['message']
        translated = event['translated']
        sender = event['sender']
        english = event['english']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'translated': translated,
            'sender': sender,
            'english': english
        }))

    @database_sync_to_async
    def get_receiver_language(self, username):
        try:
            receiver = User.objects.get(username=username)
            profile, created = Profile.objects.get_or_create(user=receiver)
            return profile.target_language
        except Exception:
            return 'en'

    @database_sync_to_async
    def save_message(self, sender, receiver_name, original, translated, english):
        try:
            receiver = User.objects.get(username=receiver_name)
            return Message.objects.create(
                sender=sender,
                receiver=receiver,
                original_text=original,
                translated_text=translated,
                english_text=english
            )
        except Exception as e:
            print(f"Error saving message: {e}")
