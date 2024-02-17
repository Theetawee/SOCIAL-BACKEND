# your_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class Notifications(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Send a greeting message when the connection is established
        await self.send(text_data=json.dumps({"message": "Hello, World!"}))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Process any received data if needed

        # Send a response back to the client
        await self.send(text_data=json.dumps({"message": "Received your message!"}))
