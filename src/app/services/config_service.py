from sqlalchemy.orm import Session
from app.models.config import ConfigParameter
import os
from typing import Optional, Dict

class ConfigService:
    def __init__(self, db: Session):
        self.db = db
        self.api_keys = [
            "OPENAI_API_KEY",
            "UBER_EATS_CLIENT_ID",
            "UBER_EATS_CLIENT_SECRET", 
            "UBER_EATS_STORE_ID",
            "DELIVEROO_API_KEY",
            "DELIVEROO_RESTAURANT_ID",
            "JUST_EAT_API_KEY",
            "JUST_EAT_TENANT_ID"
        ]
    
    def sync_env_to_db(self):
        """Save environment variables to database if they exist"""
        for key in self.api_keys:
            env_value = os.getenv(key)
            if env_value:
                self.set_config(key, env_value)
    
    def get_config(self, key: str) -> Optional[str]:
        """Get config value from database or environment"""
        # First try environment
        env_value = os.getenv(key)
        if env_value:
            return env_value
        
        # Then try database
        config = self.db.query(ConfigParameter).filter(ConfigParameter.key == key).first()
        return config.value if config else None
    
    def set_config(self, key: str, value: str, description: str = None):
        """Set config value in database"""
        config = self.db.query(ConfigParameter).filter(ConfigParameter.key == key).first()
        
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = ConfigParameter(
                key=key,
                value=value,
                description=description or f"API credential for {key}"
            )
            self.db.add(config)
        
        self.db.commit()
    
    def get_all_api_credentials(self) -> Dict[str, str]:
        """Get all API credentials from database or environment"""
        credentials = {}
        for key in self.api_keys:
            value = self.get_config(key)
            if value:
                credentials[key] = value
        return credentials
    
    def initialize_config(self):
        """Initialize config on startup"""
        self.sync_env_to_db()