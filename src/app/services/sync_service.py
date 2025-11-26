from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant, MenuItem, PlatformSync
from app.services.platform_adapters import UberEatsAdapter, DeliverooAdapter, JustEatAdapter
from app.services.config_service import ConfigService
from app.services.audit_service import AuditService
from datetime import datetime
import os
import logging
from app.core.logging_config import setup_logging

# Ensure logging is configured
setup_logging()
logger = logging.getLogger(__name__)

class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.config_service = ConfigService(db)
        self.audit_service = AuditService(db)
        
        self.platforms = {
            "uber_eats": UberEatsAdapter(
                self.config_service.get_config("UBER_EATS_CLIENT_ID"),
                self.config_service.get_config("UBER_EATS_CLIENT_SECRET"),
                self.config_service.get_config("UBER_EATS_STORE_ID")
            ),
            "deliveroo": DeliverooAdapter(
                self.config_service.get_config("DELIVEROO_API_KEY"),
                self.config_service.get_config("DELIVEROO_RESTAURANT_ID")
            ),
            "just_eat": JustEatAdapter(
                self.config_service.get_config("JUST_EAT_API_KEY"),
                self.config_service.get_config("JUST_EAT_TENANT_ID")
            )
        }
    
    def sync_all_platforms(self, restaurant_id: int) -> Dict[str, Any]:
        results = {}
        menu_items = self.db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
        
        for platform_name, adapter in self.platforms.items():
            try:
                if adapter.authenticate():
                    result = adapter.sync_menu_items(menu_items)
                    self._update_sync_status(restaurant_id, platform_name, result)
                    self.audit_service.log_sync_action(restaurant_id, platform_name, result)
                    results[platform_name] = result
                else:
                    results[platform_name] = {"success": False, "error": "Authentication failed"}
            except Exception as e:
                logger.error(f"Sync failed for {platform_name}: {e}")
                results[platform_name] = {"success": False, "error": str(e)}
        
        return results
    
    def sync_single_platform(self, restaurant_id: int, platform: str) -> Dict[str, Any]:
        if platform not in self.platforms:
            return {"success": False, "error": "Platform not supported"}
        
        menu_items = self.db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
        adapter = self.platforms[platform]
        
        try:
            if adapter.authenticate():
                result = adapter.sync_menu_items(menu_items)
                self._update_sync_status(restaurant_id, platform, result)
                self.audit_service.log_sync_action(restaurant_id, platform, result)
                return result
            else:
                return {"success": False, "error": "Authentication failed"}
        except Exception as e:
            logger.error(f"Sync failed for {platform}: {e}")
            return {"success": False, "error": str(e)}
    
    def update_restaurant_info(self, restaurant_id: int, platforms: List[str] = None) -> Dict[str, Any]:
        restaurant = self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant:
            return {"success": False, "error": "Restaurant not found"}
        
        restaurant_data = {
            "name": restaurant.name,
            "location": restaurant.location,
            "cuisine_type": restaurant.cuisine_type,
            "phone": restaurant.phone,
            "email": restaurant.email,
            "address": restaurant.address,
            "opening_hours": restaurant.opening_hours
        }
        
        target_platforms = platforms or list(self.platforms.keys())
        results = {}
        
        for platform_name in target_platforms:
            if platform_name in self.platforms:
                adapter = self.platforms[platform_name]
                try:
                    if adapter.authenticate():
                        result = adapter.update_restaurant_info(restaurant_data)
                        results[platform_name] = result
                    else:
                        results[platform_name] = {"success": False, "error": "Authentication failed"}
                except Exception as e:
                    results[platform_name] = {"success": False, "error": str(e)}
        
        return results
    
    def _update_sync_status(self, restaurant_id: int, platform: str, result: Dict[str, Any]):
        sync_record = self.db.query(PlatformSync).filter(
            PlatformSync.restaurant_id == restaurant_id,
            PlatformSync.platform == platform
        ).first()
        
        if not sync_record:
            sync_record = PlatformSync(
                restaurant_id=restaurant_id,
                platform=platform
            )
            self.db.add(sync_record)
        
        sync_record.last_sync = datetime.utcnow()
        sync_record.sync_status = "success" if result.get("success") else "failed"
        sync_record.error_message = result.get("error")
        
        self.db.commit()
    
    def get_sync_status(self, restaurant_id: int) -> List[Dict[str, Any]]:
        sync_records = self.db.query(PlatformSync).filter(
            PlatformSync.restaurant_id == restaurant_id
        ).all()
        
        return [{
            "platform": record.platform,
            "last_sync": record.last_sync,
            "status": record.sync_status,
            "error_message": record.error_message
        } for record in sync_records]