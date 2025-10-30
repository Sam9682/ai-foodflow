from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ai_bot import RestaurantAIBot
from pydantic import BaseModel
from typing import Optional, List, Dict
import json

router = APIRouter(prefix="/chat", tags=["AI Chat"])

class ChatMessage(BaseModel):
    message: str
    restaurant_id: int

class AddItemsRequest(BaseModel):
    restaurant_id: int
    menu_items: List[dict]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, restaurant_id: int):
        await websocket.accept()
        self.active_connections[restaurant_id] = websocket

    def disconnect(self, restaurant_id: int):
        if restaurant_id in self.active_connections:
            del self.active_connections[restaurant_id]

    async def send_message(self, message: dict, restaurant_id: int):
        if restaurant_id in self.active_connections:
            await self.active_connections[restaurant_id].send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/ws/{restaurant_id}")
async def websocket_endpoint(websocket: WebSocket, restaurant_id: int):
    await manager.connect(websocket, restaurant_id)
    
    db = next(get_db())
    bot = RestaurantAIBot(db)
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "welcome",
            "message": "Hello! I'm your FoodFlow AI assistant. I can help you manage your menu and sync to delivery platforms. You can attach menu images for analysis.",
            "suggestions": [
                "Show me my current menu",
                "Sync to Uber Eats and Deliveroo",
                "I have a menu image to analyze"
            ]
        }
        await manager.send_message(welcome_msg, restaurant_id)
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            
            # Process with AI bot
            bot_response = bot.process_message(user_message, restaurant_id)
            
            # Send response back
            response_msg = {
                "user_message": user_message,
                **bot_response
            }
            
            await manager.send_message(response_msg, restaurant_id)
            
    except WebSocketDisconnect:
        manager.disconnect(restaurant_id)
    finally:
        db.close()

@router.post("/message")
async def send_message(chat: ChatMessage, db: Session = Depends(get_db)):
    """Send text message to AI bot"""
    bot = RestaurantAIBot(db)
    response = bot.process_message(chat.message, chat.restaurant_id)
    return response

@router.post("/message-with-image")
async def send_message_with_image(
    message: str = Form(...),
    restaurant_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Send message with attached image to AI bot"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_data = await file.read()
        bot = RestaurantAIBot(db)
        response = bot.process_message(message, restaurant_id, image_data)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-items")
async def add_menu_items(request: AddItemsRequest, db: Session = Depends(get_db)):
    """Add analyzed menu items to database"""
    bot = RestaurantAIBot(db)
    result = bot.add_menu_items(request.restaurant_id, request.menu_items)
    return result

@router.get("/menu/{restaurant_id}")
async def get_current_menu(restaurant_id: int, db: Session = Depends(get_db)):
    """Get current menu via chat interface"""
    bot = RestaurantAIBot(db)
    response = bot._handle_show_menu(restaurant_id)
    return response