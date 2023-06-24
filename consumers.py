import json

from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.staticfiles import finders

from accounts.models import User

from .models import Thread, ChatMessage


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        other_user = self.scope['url_route']['kwargs']['id']
        me = self.scope['user']

        self.thread_obj = await self.get_thread(me, other_user)

        self.chat_room = f"thread_{self.thread_obj.id}"

        await self.channel_layer.group_add(
            self.chat_room,
            self.channel_name
        )

        await self.send({
            'type': 'websocket.accept'
        })
  
    async def websocket_receive(self, event):
        data = event.get('text', None)

        if data is not None and self.scope['user'].is_authenticated:
            data = json.loads(data)

            profile_pic = await self.get_user_picture(self.scope['user'])

            if 'type' in data:
                message = {
                    'message': data.get('message'),
                    'type': 'file',
                    'user_id': str(self.scope['url_route']['kwargs']['id']),
                    'profile_pic': profile_pic
                }

                await self.channel_layer.group_send(
                    self.chat_room,
                    {
                        'type': 'chat_message',
                        'text': json.dumps(message)
                    }
                )

            else:
                message = {
                    'message': data.get('message'),
                    'user_id': str(self.scope['user'].id),
                    'profile_pic': profile_pic
                }

                await self.create_chat_message(message['message'])

                await self.channel_layer.group_send(
                    self.chat_room,
                    {
                        'type': 'chat_message',
                        'text': json.dumps(message)
                    }
                )

    async def chat_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.chat_room,
            self.channel_name
        )

    @database_sync_to_async
    def get_thread(self, user, other_id):
        return Thread.objects.get_or_new(user, other_id)[0]
    
    @database_sync_to_async
    def get_user_picture(self, user):
        u = User.objects.get(id=user.id)

        if u.is_doctor and u.profile_doctor.profile_pic:
            profile_pic = u.profile_doctor.profile_pic.url
        else:
            profile_pic = '/static/images/user.png/'

        return profile_pic

        

    @database_sync_to_async
    def create_chat_message(self, msg):
        return ChatMessage.objects.create(thread=self.thread_obj, user=self.scope['user'], message=msg)