from pydantic import BaseModel
from typing import Dict, List, Optional

class Player(BaseModel): #Player class
    username: str
    score: int = 0
    guesses: List[str] = []  # Store player's guesses



class Room(BaseModel): #Room class
    id: str               # Unique room identifier
    word: str            # Word to guess
    players: Dict[str, Player] = {}  # All players in room
    game_over: bool = False
    winner: Optional[str] = None
    created_at: float    # Timestamp when room was created