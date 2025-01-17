
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import random
import os
import string
from words_api import get_today_word
from scorer.similarity_scorer import SimilarityScorer
from multiplayerHandler.game_manager import GameManager
from multiplayerHandler.connection_manager import ConnectionManager
from fastapi.middleware.cors import CORSMiddleware
from sys import stdout
from scorer.unknown_word_exception import UnknownWordException
from tips import TipsService
from logging.config import dictConfig
import logging
from config import LogConfig

dictConfig(LogConfig().dict())

log = logging.getLogger("contexto")

app = FastAPI()
scorer = SimilarityScorer()
tips_service = TipsService(scorer)
game_manager = GameManager()
connection_manager = ConnectionManager()


def generate_room_id(length=6):
    """Generate a random room ID of specified length"""
    # Use uppercase letters and numbers for room ID
    characters = string.ascii_uppercase + string.digits
    while True:
        # Generate a random room ID
        room_id = ''.join(random.choices(characters, k=length))
        # Check if this room ID already exists
        if room_id not in game_manager.rooms:
            return room_id


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/similarity")
async def get_similarity(guess: str):
    log.info(f"Guess: {guess}")

    today_word = get_today_word()

    if today_word == guess:
        return {
            "similarity": 100
        }

    log.info(f"Compute similarity for '{today_word}' and '{guess}'")

    try:
        similarity = scorer.get_similarity(today_word=today_word, guess=guess)
    except UnknownWordException as e:
        return {
            "unknown_word": e.word
        }

    return {
        "similarity": similarity
    }


@app.get("/tip")
async def get_tip():
    tip, similarity = tips_service.get_tip(get_today_word())
    return {
        "tip": tip,
        "similarity": similarity
    }


@app.get("/giveup")
async def get_tip():
    return {
        "word": get_today_word(),
        "similarity": 100
    }


# Regular HTTP endpoint to create a room
@app.get("/create-room")
async def create_room():
    room_id = generate_room_id() #generate a random room ID on the server
    
    word = get_today_word()
    
    room = game_manager.create_room(room_id, word)
    
    return {"room_id": room_id}



# WebSocket endpoint for game play
@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):


    if room_id not in game_manager.rooms: #checking if room id does not exist
        await websocket.close(code=1000, reason="Room does not exist.")
        return
    
    
    
    # Step 1: Connect player to room
    await connection_manager.connect(websocket, room_id, username)
    
    try:
        # Step 2: Add player to game room
        room = game_manager.join_room(room_id, username)

        #Check if game is already over when player joins
        if room.game_over:
            await websocket.send_json({
                "type": "game_over",
                "winner": room.winner,
                "word": room.word,
                "message" : "game already over"
            })
            return  # Exit if game is already over
        
        # Step 3: Announce new player to everyone in room
        await connection_manager.broadcast(room_id, json.dumps({
            "type": "join",
            "username": username,
            "players": [p.username for p in room.players.values()]
        }))
        
        # Step 4: Main game loop
        while True:
            # Wait for messages from this player
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "guess":
                try:
                    # Calculate similarity of guess
                    similarity = scorer.get_similarity(room.word, message["guess"])
                    
                    # Process the guess
                    result = game_manager.make_guess(
                        room_id, 
                        username, 
                        message["guess"], 
                        similarity
                    )
                    
                    # Broadcast result to all players
                    await connection_manager.broadcast(room_id, json.dumps({
                        "type": "guess_result",
                        "username": username,
                        "guess": message["guess"],
                        "similarity": similarity,
                        "game_over": result.get("correct", False),
                        "winner": result.get("winner")
                    }))
                    
                    # Handle the game-over scenario
                    # if result.get("correct", False):
                    #     # await websocket.send_json({
                    #     #     "type": "win",
                    #     #     "message": f"Congratulations {username}, you have won the game!",
                    #     #     "word": room.word
                    #     # })

                    #     await connection_manager.broadcast(room_id, json.dumps({
                    #         "type": "game_over",
                    #         "winner": username,
                    #         "word": room.word
                    #     }))
                
                except UnknownWordException as e:
                    await websocket.send_json({
                        "type": "error",
                        "error": "InvalidWord",
                        "message": f"'{e.word}' is not a valid word."
                    })
            
            elif message["type"] == "leave":
                # Handle user leaving the room
                await connection_manager.disconnect(room_id, username)
                if(room.players.get(username)): room.players.pop(username)  # Update the game state
                
                # Notify other players
                await connection_manager.broadcast(room_id, json.dumps({
                    "type": "leave",
                    "username": username,
                    "players": [p.username for p in room.players.values()]
                }))
                break  # Exit the loop and close the WebSocket connection for this user
    
    except WebSocketDisconnect:
        # Handle unexpected player disconnection
        await connection_manager.disconnect(room_id, username)
        if(room.players.get(username)): room.players.pop(username)  # Update the game state
        await connection_manager.broadcast(room_id, json.dumps({
            "type": "leave",
            "username": username,
            "players": [p.username for p in room.players.values()]
        }))
