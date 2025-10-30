import openai
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant, MenuItem
from app.services.sync_service import SyncService
from app.services.config_service import ConfigService
from app.services.audit_service import AuditService
import os
import base64
from PIL import Image
import io

class RestaurantAIBot:
    def __init__(self, db: Session):
        self.db = db
        self.config_service = ConfigService(db)
        self.audit_service = AuditService(db)
        self.openai_client = openai.OpenAI(api_key=self.config_service.get_config("OPENAI_API_KEY"))
        self.sync_service = SyncService(db)
        
        self.system_prompt = """
        You are an AI assistant for FoodFlow restaurant management platform.
        Help restaurant owners manage menus and sync to Uber Eats, Deliveroo, and Just Eat.
        
        When users attach menu images, analyze them and extract menu items with names, descriptions, prices, and categories.
        When users ask to sync or dispatch, sync their menu to the requested platforms.
        
        Always be conversational and helpful. Guide users through the process step by step.
        """
    
    def process_message(self, message: str, restaurant_id: int, image_data: Optional[bytes] = None) -> Dict[str, Any]:
        """Process user message with optional image attachment"""
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add image if provided
        if image_data:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            })
        else:
            messages.append({"role": "user", "content": message})
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview" if image_data else "gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
            # Determine action based on message content
            if image_data and ("menu" in message.lower() or "scan" in message.lower()):
                return self._handle_menu_analysis(ai_response, restaurant_id, image_data)
            elif "sync" in message.lower() or "dispatch" in message.lower():
                return self._handle_sync_request(message, restaurant_id)
            elif "show" in message.lower() and "menu" in message.lower():
                return self._handle_show_menu(restaurant_id)
            else:
                return {
                    "type": "chat",
                    "response": ai_response,
                    "suggestions": [
                        "Show me my current menu",
                        "Sync to Uber Eats and Deliveroo",
                        "Upload a menu image to analyze"
                    ]
                }
                
        except Exception as e:
            return {"type": "error", "message": f"AI processing failed: {str(e)}"}
    
    def _handle_menu_analysis(self, ai_response: str, restaurant_id: int, image_data: bytes) -> Dict[str, Any]:
        """Handle menu image analysis"""
        try:
            # Try to extract structured data from AI response
            menu_items = self._extract_menu_items_from_response(ai_response)
            
            return {
                "type": "menu_analyzed",
                "response": ai_response,
                "menu_items": menu_items,
                "count": len(menu_items),
                "actions": [
                    {"text": "Add these items to my menu", "action": "add_items"},
                    {"text": "Sync to delivery platforms", "action": "sync_platforms"}
                ]
            }
        except Exception as e:
            return {
                "type": "analysis_error",
                "response": ai_response,
                "message": "Could not extract structured menu data, but here's what I found."
            }
    
    def _extract_menu_items_from_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract menu items from AI response"""
        # Simple extraction - look for patterns like "Name: X, Price: Y"
        items = []
        lines = response.split('\n')
        
        current_item = {}
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if 'name' in key:
                    if current_item:
                        items.append(current_item)
                    current_item = {'name': value}
                elif 'price' in key:
                    # Extract price number
                    price_str = ''.join(c for c in value if c.isdigit() or c == '.')
                    if price_str:
                        current_item['price'] = float(price_str)
                elif 'description' in key:
                    current_item['description'] = value
                elif 'category' in key:
                    current_item['category'] = value
        
        if current_item:
            items.append(current_item)
        
        return items
    
    def _handle_sync_request(self, message: str, restaurant_id: int) -> Dict[str, Any]:
        """Handle platform sync request"""
        platforms = []
        
        if "uber" in message.lower():
            platforms.append("uber_eats")
        if "deliveroo" in message.lower():
            platforms.append("deliveroo")
        if "just eat" in message.lower():
            platforms.append("just_eat")
        
        if not platforms:
            platforms = ["uber_eats", "deliveroo"]  # Default
        
        results = {}
        for platform in platforms:
            results[platform] = self.sync_service.sync_single_platform(restaurant_id, platform)
        
        success_count = sum(1 for r in results.values() if r.get("success"))
        
        return {
            "type": "sync_completed",
            "results": results,
            "response": f"Sync completed! {success_count}/{len(platforms)} platforms updated successfully.",
            "platforms": platforms
        }
    
    def _handle_show_menu(self, restaurant_id: int) -> Dict[str, Any]:
        """Show current menu"""
        items = self.db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
        
        menu_data = []
        for item in items:
            menu_data.append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "category": item.category,
                "available": item.is_available
            })
        
        categories = {}
        for item in menu_data:
            cat = item["category"] or "Other"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        response = f"Your menu has {len(menu_data)} items:\n\n"
        for category, items in categories.items():
            response += f"**{category}:**\n"
            for item in items:
                status = "✅" if item["available"] else "❌"
                response += f"  {status} {item['name']} - €{item['price']}\n"
            response += "\n"
        
        return {
            "type": "menu_displayed",
            "response": response,
            "menu_data": menu_data,
            "count": len(menu_data)
        }
    
    def add_menu_items(self, restaurant_id: int, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add menu items to database"""
        added_items = []
        
        try:
            for item_data in menu_items:
                if not item_data.get("name"):
                    continue
                    
                menu_item = MenuItem(
                    restaurant_id=restaurant_id,
                    name=item_data.get("name"),
                    description=item_data.get("description", ""),
                    price=float(item_data.get("price", 0)),
                    category=item_data.get("category", "Other"),
                    is_available=True
                )
                
                self.db.add(menu_item)
                added_items.append(menu_item)
            
            self.db.commit()
            
            # Log menu addition
            self.audit_service.log_menu_action(
                "add_items", 
                restaurant_id, 
                {"items_count": len(added_items), "items": [item.name for item in added_items]}
            )
            
            return {
                "type": "items_added",
                "success": True,
                "count": len(added_items),
                "response": f"Successfully added {len(added_items)} menu items to your database!"
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "type": "add_error",
                "success": False,
                "error": str(e),
                "response": "Failed to add menu items. Please try again."
            }