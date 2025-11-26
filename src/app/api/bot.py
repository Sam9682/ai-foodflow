from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ai_bot import RestaurantAIBot
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid

router = APIRouter(prefix="/bot", tags=["AI Bot"])

class ChatMessage(BaseModel):
    message: str
    restaurant_id: int

class AddItemsRequest(BaseModel):
    restaurant_id: int
    menu_items: List[dict]

@router.post("/chat")
async def chat_with_bot(chat: ChatMessage, db: Session = Depends(get_db)):
    """Chat with AI bot for restaurant management"""
    bot = RestaurantAIBot(db)
    response = bot.process_message(chat.message, chat.restaurant_id)
    return response

@router.post("/scan-menu")
async def scan_menu(
    restaurant_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Scan menu from uploaded image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file temporarily
    file_id = str(uuid.uuid4())
    file_path = f"/tmp/menu_{file_id}.jpg"
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        bot = RestaurantAIBot(db)
        result = bot._handle_menu_scan(file_path, restaurant_id)
        
        # Clean up temp file
        os.remove(file_path)
        
        return result
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-scanned-items")
async def add_scanned_items(request: AddItemsRequest, db: Session = Depends(get_db)):
    """Add scanned menu items to database"""
    bot = RestaurantAIBot(db)
    result = bot.add_scanned_items(request.restaurant_id, request.menu_items)
    return result

@router.post("/sync-platforms")
async def sync_platforms(chat: ChatMessage, db: Session = Depends(get_db)):
    """Sync menu to delivery platforms via bot"""
    bot = RestaurantAIBot(db)
    response = bot._handle_sync_request(chat.message, chat.restaurant_id)
    return response

@router.get("/menu/{restaurant_id}")
async def get_menu_via_bot(restaurant_id: int, db: Session = Depends(get_db)):
    """Get current menu via bot interface"""
    bot = RestaurantAIBot(db)
    response = bot._handle_show_menu(restaurant_id)
    return response