from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.audit import ActionHistory
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/history")
async def get_action_history(
    action_type: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    days: int = Query(7, description="Number of days to look back"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get platform action history"""
    
    query = db.query(ActionHistory)
    
    # Filter by date
    since_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(ActionHistory.timestamp >= since_date)
    
    # Apply filters
    if action_type:
        query = query.filter(ActionHistory.action_type == action_type)
    if entity_type:
        query = query.filter(ActionHistory.entity_type == entity_type)
    if entity_id:
        query = query.filter(ActionHistory.entity_id == entity_id)
    
    # Order and limit
    records = query.order_by(ActionHistory.timestamp.desc()).limit(limit).all()
    
    return {
        "history": [{
            "id": record.id,
            "action_type": record.action_type,
            "entity_type": record.entity_type,
            "entity_id": record.entity_id,
            "user_id": record.user_id,
            "action_details": record.action_details,
            "result": record.result,
            "error_message": record.error_message,
            "timestamp": record.timestamp
        } for record in records],
        "count": len(records)
    }

@router.get("/stats")
async def get_audit_stats(
    days: int = Query(7),
    db: Session = Depends(get_db)
):
    """Get audit statistics"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Total actions
    total_actions = db.query(ActionHistory).filter(ActionHistory.timestamp >= since_date).count()
    
    # Success rate
    successful_actions = db.query(ActionHistory).filter(
        ActionHistory.timestamp >= since_date,
        ActionHistory.result == "success"
    ).count()
    
    success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
    
    return {
        "total_actions": total_actions,
        "successful_actions": successful_actions,
        "success_rate": round(success_rate, 2),
        "period_days": days
    }