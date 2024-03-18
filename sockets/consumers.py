from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification
import json
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async
import asyncio


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            notifications_count = await self.get_notifications_count(user)

            # Send a welcome message with initial data
            message = {
                "count": notifications_count,
            }
            await self.accept()
            await self.send(text_data=json.dumps(message))

            # Start a background task to periodically check for updates
            await self.periodic_check_for_updates(user)
        else:
            # If the user is not authenticated, close the connection without adding to the group or accepting
            await self.close()

    async def disconnect(self, close_code):
        # Stop the periodic task when the connection is closed
        if hasattr(self, "periodic_task") and not self.periodic_task.done():
            self.periodic_task.cancel()

        raise StopConsumer()

    async def receive(self, text_data):
        # This method should handle messages received from the WebSocket connection.
        # You can customize it based on your application's requirements.
        pass

    @database_sync_to_async
    def get_notifications_count(self, user):
        return Notification.objects.filter(to_user=user, seen=False).count()

    async def periodic_check_for_updates(self, user):
        while True:
            # Perform some task, e.g., querying the database for updates
            notifications_count = await self.get_notifications_count(user)

            # Send the update to the connected WebSocket clients
            await self.send(
                text_data=json.dumps(
                    {
                        "count": notifications_count,
                    }
                )
            )

            # Sleep for a while before the next check
            await asyncio.sleep(15)
