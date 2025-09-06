import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # ✅ normal message
        if "message" in data:
            message = data["message"]

            user = self.scope["user"]
            if not user.is_authenticated:
                user = await database_sync_to_async(User.objects.first)()

            msg_obj = await self.save_message(user, self.room_name, message)

            # single tick
            await self.send(text_data=json.dumps({
                "status": "saved",
                "message_id": msg_obj.id,
                "message": msg_obj.content,
                "username": user.username
            }))

            # group broadcast
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_id": msg_obj.id,
                    "message": msg_obj.content,
                    "username": user.username
                }
            )

        # ✅ read receipt
        elif "read_message_id" in data:
            message_id = data["read_message_id"]
            await self.mark_read(message_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "read_receipt",
                    "message_id": message_id
                }
            )

        # ✅ search
        elif "search" in data:
            query = data["search"]
            results = await self.search_messages(query, self.room_name)

            await self.send(text_data=json.dumps({
                "status": "search_results",
                "query": query,
                "results": results
            }))

        # ✅ edit message
        elif "edit_message_id" in data:
            msg_id = data["edit_message_id"]
            new_content = data["new_content"]
            updated_msg = await self.edit_message(msg_id, new_content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_edited",
                    "message_id": updated_msg.id,
                    "new_content": updated_msg.content
                }
            )

        # ✅ delete message
        elif "delete_message_id" in data:
            msg_id = data["delete_message_id"]
            deleted_msg = await self.delete_message(msg_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_deleted",
                    "message_id": deleted_msg.id
                }
            )

    # 🔹 EVENTS
    async def chat_message(self, event):
        await self.mark_delivered(event["message_id"])
        await self.send(text_data=json.dumps({
            "status": "delivered",
            "message_id": event["message_id"],
            "message": event["message"],
            "username": event["username"]
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            "status": "read",
            "message_id": event["message_id"]
        }))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            "status": "edited",
            "message_id": event["message_id"],
            "new_content": event["new_content"]
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            "status": "deleted",
            "message_id": event["message_id"]
        }))

    # 🔹 HELPERS
    @database_sync_to_async
    def save_message(self, user, room, content):
        return Message.objects.create(user=user, room=room, content=content)

    @database_sync_to_async
    def mark_delivered(self, message_id):
        msg = Message.objects.get(id=message_id)
        msg.message_deliver = True
        msg.save()
        return msg

    @database_sync_to_async
    def mark_read(self, message_id):
        msg = Message.objects.get(id=message_id)
        msg.message_read = True
        msg.save()
        return msg

    @database_sync_to_async
    def search_messages(self, query, room):
        msgs = Message.objects.filter(
            room=room, content__icontains=query
        ).order_by("-timestamp")[:20]
        return [
            {
                "id": msg.id,
                "username": msg.user.username,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "delivered": msg.message_deliver,
                "read": msg.message_read,
            }
            for msg in msgs
        ]

    @database_sync_to_async
    def edit_message(self, message_id, new_content):
        msg = Message.objects.get(id=message_id)
        msg.content = new_content
        msg.save()
        return msg

    @database_sync_to_async
    def delete_message(self, message_id):
        msg = Message.objects.get(id=message_id)
        msg.is_deleted = True
        msg.content = "[deleted]"
        msg.save()
        return msg
