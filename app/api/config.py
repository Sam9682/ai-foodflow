from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.config_service import ConfigService
from app.services.audit_service import AuditService
from pydantic import BaseModel
from typing import Dict, Optional

router = APIRouter(prefix="/config", tags=["Configuration"])

class ConfigUpdate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

@router.get("/credentials")
async def get_api_credentials(db: Session = Depends(get_db)):
    """Get all API credentials (masked for security)"""
    config_service = ConfigService(db)
    credentials = config_service.get_all_api_credentials()
    
    # Mask sensitive values
    masked_credentials = {}
    for key, value in credentials.items():
        if value:
            masked_credentials[key] = f"{value[:4]}***{value[-4:]}" if len(value) > 8 else "***"
        else:
            masked_credentials[key] = None
    
    return {"credentials": masked_credentials}

@router.post("/credentials")
async def update_credential(config: ConfigUpdate, db: Session = Depends(get_db)):
    """Update API credential"""
    config_service = ConfigService(db)
    
    if config.key not in config_service.api_keys:
        raise HTTPException(status_code=400, detail="Invalid credential key")
    
    config_service.set_config(config.key, config.value, config.description)
    
    # Log config change
    audit_service = AuditService(db)
    audit_service.log_config_action(config.key)
    
    return {"message": f"Credential {config.key} updated successfully"}

@router.get("/status")
async def get_config_status(db: Session = Depends(get_db)):
    """Get configuration status"""
    config_service = ConfigService(db)
    credentials = config_service.get_all_api_credentials()
    
    status = {}
    for key in config_service.api_keys:
        status[key] = bool(credentials.get(key))
    
    return {"status": status, "configured_count": sum(status.values())}