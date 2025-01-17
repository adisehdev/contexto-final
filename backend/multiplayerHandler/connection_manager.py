from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # Store active WebSocket connections
        # Format: {room_id: {username: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][username] = websocket

    async def disconnect(self, room_id: str, username: str):
        """Remove a WebSocket connection"""
        if room_id in self.active_connections:
            self.active_connections[room_id].pop(username, None)

    async def broadcast(self, room_id: str, message: str):
        """Send a message to all players in a room"""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id].values():
                await connection.send_text(message)