from sqlalchemy.orm import Session
from app.models.audit import ActionHistory
from typing import Dict, Any, Optional
from datetime import datetime

class AuditService:
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(self, action_type: str, entity_type: str = None, entity_id: int = None, 
                   user_id: str = "system", action_details: Dict[str, Any] = None, 
                   result: str = "success", error_message: str = None):
        """Log platform action to history"""
        
        audit_record = ActionHistory(
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            action_details=action_details or {},
            result=result,
            error_message=error_message
        )
        
        self.db.add(audit_record)
        self.db.commit()
    
    def log_sync_action(self, restaurant_id: int, platform: str, result: Dict[str, Any], user_id: str = "system"):
        """Log sync action"""
        self.log_action(
            action_type="platform_sync",
            entity_type="restaurant",
            entity_id=restaurant_id,
            user_id=user_id,
            action_details={"platform": platform, "sync_data": result},
            result="success" if result.get("success") else "failed",
            error_message=result.get("error")
        )
    
    def log_menu_action(self, action: str, restaurant_id: int, item_data: Dict[str, Any] = None, user_id: str = "system"):
        """Log menu-related actions"""
        self.log_action(
            action_type=f"menu_{action}",
            entity_type="menu_item",
            entity_id=restaurant_id,
            user_id=user_id,
            action_details=item_data or {}
        )
    
    def log_config_action(self, key: str, user_id: str = "system"):
        """Log configuration changes"""
        self.log_action(
            action_type="config_update",
            entity_type="config",
            user_id=user_id,
            action_details={"config_key": key}
        )