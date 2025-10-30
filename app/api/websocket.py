from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ai_bot import RestaurantAIBot
import json
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.restaurant_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, restaurant_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if restaurant_id not in self.restaurant_connections:
            self.restaurant_connections[restaurant_id] = []
        self.restaurant_connections[restaurant_id].append(websocket)

    def disconnect(self, websocket: WebSocket, restaurant_id: int):
        self.active_connections.remove(websocket)
        if restaurant_id in self.restaurant_connections:
            self.restaurant_connections[restaurant_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_restaurant(self, message: str, restaurant_id: int):
        if restaurant_id in self.restaurant_connections:
            for connection in self.restaurant_connections[restaurant_id]:
                await connection.send_text(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, restaurant_id: int):
    await manager.connect(websocket, restaurant_id)
    
    # Get database session
    db = next(get_db())
    bot = RestaurantAIBot(db)
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "welcome",
            "message": "Hello! I'm your FoodFlow AI assistant. I can help you scan menus and sync to delivery platforms.",
            "suggestions": [
                "Scan my menu",
                "Sync to Uber Eats and Deliveroo",
                "Show current menu"
            ]
        }
        await manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            
            # Process with AI bot
            bot_response = bot.process_message(user_message, restaurant_id)
            
            # Send response back to client
            response_msg = {
                "type": "bot_response",
                "user_message": user_message,
                **bot_response
            }
            
            await manager.send_personal_message(json.dumps(response_msg), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, restaurant_id)
    finally:
        db.close()