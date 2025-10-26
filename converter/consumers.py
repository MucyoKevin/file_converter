"""
WebSocket consumers for real-time conversion progress updates
"""
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ConversionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time conversion progress updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.conversion_id = self.scope['url_route']['kwargs'].get('conversion_id')
        self.room_group_name = f'conversion_{self.conversion_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            pass
    
    async def conversion_progress(self, event):
        """
        Receive conversion progress from room group and send to WebSocket
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'conversion_id': event['conversion_id'],
            'progress': event['progress'],
            'status': event['status'],
            'error': event.get('error')
        }))

