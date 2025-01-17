import time
from typing import Dict
from helperModels.models import Room, Player

class GameManager:
    def __init__(self): #storing all active rooms
        self.rooms: Dict[str, Room] = {}

    def create_room(self, room_id: str, word: str) -> Room:
        """Create a new game room"""
        room = Room(
            id=room_id,
            word=word,
            created_at=time.time()
        )
        self.rooms[room_id] = room
        return room
    
    def join_room(self, room_id: str, username: str) -> Room:
        """Add a player to a room"""
        if room_id not in self.rooms:
            raise ValueError("Room not found")
        
        room = self.rooms[room_id]
        if username not in room.players:
            room.players[username] = Player(username=username)
        return room
        

    def make_guess(self, room_id: str, username: str, guess: str, similarity: float) -> Dict:
        """Process a player's guess"""
        room = self.rooms[room_id]
        player = room.players[username]
        player.guesses.append(guess)
        
        if guess == room.word:
            room.game_over = True
            room.winner = username
            return {"correct": True, "winner": username}
        
        return {"correct": False, "similarity": similarity}
