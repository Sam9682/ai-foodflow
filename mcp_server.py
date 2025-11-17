#!/usr/bin/env python3
"""MCP Server for FoodFlow Restaurant Management"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, create_tables
from app.services.sync_service import SyncService
from app.services.ai_bot import RestaurantAIBot
from app.models.restaurant import Restaurant, MenuItem
from app.core.logging_config import setup_logging
import base64

# Configure logging with datetime stamps
setup_logging()
logger = logging.getLogger(__name__)

# Initialize MCP Server
server = Server("foodflow")

def get_db():
    """Get database session"""
    return SessionLocal()

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available FoodFlow tools"""
    return [
        Tool(
            name="sync_to_platforms",
            description="Sync restaurant menu to delivery platforms (Uber Eats, Deliveroo, Just Eat)",
            inputSchema={
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer", "description": "Restaurant ID"},
                    "platforms": {
                        "type": "array", 
                        "items": {"type": "string", "enum": ["uber_eats", "deliveroo", "just_eat"]},
                        "description": "Platforms to sync to (optional, defaults to all)"
                    }
                },
                "required": ["restaurant_id"]
            }
        ),
        Tool(
            name="add_menu_item",
            description="Add a new menu item to restaurant",
            inputSchema={
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer", "description": "Restaurant ID"},
                    "name": {"type": "string", "description": "Item name"},
                    "description": {"type": "string", "description": "Item description"},
                    "price": {"type": "number", "description": "Item price"},
                    "category": {"type": "string", "description": "Item category"},
                    "is_available": {"type": "boolean", "description": "Item availability", "default": True}
                },
                "required": ["restaurant_id", "name", "price", "category"]
            }
        ),
        Tool(
            name="get_menu",
            description="Get current menu for a restaurant",
            inputSchema={
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer", "description": "Restaurant ID"}
                },
                "required": ["restaurant_id"]
            }
        ),
        Tool(
            name="update_menu_item",
            description="Update existing menu item",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {"type": "integer", "description": "Menu item ID"},
                    "name": {"type": "string", "description": "Item name"},
                    "description": {"type": "string", "description": "Item description"},
                    "price": {"type": "number", "description": "Item price"},
                    "category": {"type": "string", "description": "Item category"},
                    "is_available": {"type": "boolean", "description": "Item availability"}
                },
                "required": ["item_id"]
            }
        ),
        Tool(
            name="analyze_menu_image",
            description="Analyze menu image and extract items using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer", "description": "Restaurant ID"},
                    "image_data": {"type": "string", "description": "Base64 encoded image data"},
                    "message": {"type": "string", "description": "Message about the menu", "default": "Analyze this menu"}
                },
                "required": ["restaurant_id", "image_data"]
            }
        ),
        Tool(
            name="get_sync_status",
            description="Get synchronization status for restaurant platforms",
            inputSchema={
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer", "description": "Restaurant ID"}
                },
                "required": ["restaurant_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    db = get_db()
    try:
        if name == "sync_to_platforms":
            return await sync_to_platforms(db, arguments)
        elif name == "add_menu_item":
            return await add_menu_item(db, arguments)
        elif name == "get_menu":
            return await get_menu(db, arguments)
        elif name == "update_menu_item":
            return await update_menu_item(db, arguments)
        elif name == "analyze_menu_image":
            return await analyze_menu_image(db, arguments)
        elif name == "get_sync_status":
            return await get_sync_status(db, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    finally:
        db.close()

async def sync_to_platforms(db: Session, args: Dict[str, Any]) -> List[TextContent]:
    """Sync restaurant menu to delivery platforms"""
    restaurant_id = args["restaurant_id"]
    platforms = args.get("platforms")
    
    logger.info(f"Starting platform sync for restaurant {restaurant_id} to platforms: {platforms or 'all'}")
    
    sync_service = SyncService(db)
    
    if platforms:
        results = {}
        for platform in platforms:
            results[platform] = sync_service.sync_single_platform(restaurant_id, platform)
    else:
        results = sync_service.sync_all_platforms(restaurant_id)
    
    success_count = sum(1 for r in results.values() if r.get("success"))
    total_count = len(results)
    
    logger.info(f"Platform sync completed: {success_count}/{total_count} platforms successful")
    response = f"Sync completed: {success_count}/{total_count} platforms updated successfully.\n\n"
    
    for platform, result in results.items():
        status = "✅ Success" if result.get("success") else f"❌ Failed: {result.get('error')}"
        response += f"- {platform}: {status}\n"
    
    return [TextContent(type="text", text=response)]

async def add_menu_item(db: Session, args: Dict[str, Any]) -> List[TextContent]:
    """Add new menu item"""
    menu_item = MenuItem(
        restaurant_id=args["restaurant_id"],
        name=args["name"],
        description=args.get("description", ""),
        price=args["price"],
        category=args["category"],
        is_available=args.get("is_available", True)
    )
    
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    
    response = f"✅ Menu item '{menu_item.name}' added successfully (ID: {menu_item.id})"
    return [TextContent(type="text", text=response)]

async def get_menu(db: Session, args: Dict[str, Any]) -> List[TextContent]:
    """Get restaurant menu"""
    restaurant_id = args["restaurant_id"]
    
    items = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
    
    if not items:
        return [TextContent(type="text", text="No menu items found for this restaurant.")]
    
    # Group by category
    categories = {}
    for item in items:
        cat = item.category or "Other"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    response = f"Menu for Restaurant ID {restaurant_id}:\n\n"
    
    for category, items in categories.items():
        response += f"**{category}:**\n"
        for item in items:
            status = "✅" if item.is_available else "❌"
            response += f"  {status} {item.name} - €{item.price}\n"
            if item.description:
                response += f"     {item.description}\n"
        response += "\n"
    
    return [TextContent(type="text", text=response)]

async def update_menu_item(db: Session, args: Dict[str, Any]) -> List[TextContent]:
    """Update menu item"""
    item_id = args["item_id"]
    
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return [TextContent(type="text", text=f"❌ Menu item with ID {item_id} not found")]
    
    # Update fields if provided
    for field in ["name", "description", "price", "category", "is_available"]:
        if field in args:
            setattr(item, field, args[field])
    
    db.commit()
    
    response = f"✅ Menu item '{item.name}' updated successfully"
    return [TextContent(type="text", text=response)]

async def analyze_menu_image(db: Session, args: Dict[str, Any]) -> List[TextContent]:
    """Analyze menu image using AI"""
    restaurant_id = args["restaurant_id"]
    image_data = base64.b64decode(args["image_data"])
    message = args.get("message", "Analyze this menu")
    
    bot = RestaurantAIBot(db)
    result = bot.process_message(message, restaurant_id, image_data)
    
    if result.get("type") == "menu_analyzed":
        response = f"🤖 Menu Analysis Results:\n\n{result['response']}\n\n"
        
        if result.get("menu_items"):
            response += f"Found {len(result['menu_items'])} menu items:\n"
            for item in result["menu_items"]:
                response += f"- {item.get('name', 'Unknown')} - €{item.get('price', 'N/A')}\n"
            
            response += "\nUse 'add_menu_item' tool to add these items to your menu."
        
        return [TextContent(type="text", text=response)]
    else:
        return [TextContent(type="text", text=f"❌ Analysis failed: {result.get('message', 'Unknown error')}")]

async def get_sync_status(db: Session, args: Dict[str, Any]) -> List[TextContent]:
    """Get sync status for restaurant"""
    restaurant_id = args["restaurant_id"]
    
    sync_service = SyncService(db)
    status = sync_service.get_sync_status(restaurant_id)
    
    if not status:
        return [TextContent(type="text", text="No sync history found for this restaurant.")]
    
    response = f"Sync Status for Restaurant ID {restaurant_id}:\n\n"
    
    for record in status:
        status_icon = "✅" if record["status"] == "success" else "❌"
        response += f"{status_icon} {record['platform']}: {record['status']}\n"
        if record["last_sync"]:
            response += f"   Last sync: {record['last_sync']}\n"
        if record["error_message"]:
            response += f"   Error: {record['error_message']}\n"
        response += "\n"
    
    return [TextContent(type="text", text=response)]

async def main():
    """Run MCP server"""
    logger.info("Starting FoodFlow MCP Server")
    
    # Initialize database
    create_tables()
    logger.info("Database tables initialized")
    
    # Start server
    from mcp.server.stdio import stdio_server
    
    logger.info("MCP Server ready for connections")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())