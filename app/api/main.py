from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db, create_tables
from app.models.restaurant import Restaurant, MenuItem, PlatformSync
from app.services.sync_service import SyncService
from app.services.scheduler import scheduler
from app.api.chat import router as chat_router
from app.api.config import router as config_router
from app.api.audit import router as audit_router
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FoodFlow - Restaurant Sync Platform", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Include routers
app.include_router(chat_router)
app.include_router(config_router)
app.include_router(audit_router)

# Pydantic models for API
class RestaurantCreate(BaseModel):
    name: str
    location: str
    cuisine_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    opening_hours: Optional[dict] = None

class MenuItemCreate(BaseModel):
    restaurant_id: int
    name: str
    description: Optional[str] = None
    price: float
    category: str
    is_available: bool = True
    image_url: Optional[str] = None
    allergens: Optional[list] = None
    nutritional_info: Optional[dict] = None

class SyncRequest(BaseModel):
    restaurant_id: int
    platforms: Optional[List[str]] = None

@app.on_event("startup")
async def startup_event():
    create_tables()
    
    # Initialize config from environment variables
    from app.services.config_service import ConfigService
    db = next(get_db())
    config_service = ConfigService(db)
    config_service.initialize_config()
    db.close()
    
    logger.info("Database initialized and configuration synced")

@app.get("/")
async def root():
    return {"message": "FoodFlow Restaurant Sync Platform", "status": "running"}

@app.get("/main")
async def main_dashboard():
    """Serve the main FoodFlow dashboard"""
    return FileResponse("main_ai_foodflow.html")

@app.get("/audit-page")
async def audit_page():
    """Serve the audit records page"""
    return FileResponse("audit_page.html")

@app.post("/restaurants/")
async def create_restaurant(restaurant: RestaurantCreate, db: Session = Depends(get_db)):
    db_restaurant = Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

@app.get("/restaurants/")
async def get_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()

@app.get("/restaurants/{restaurant_id}")
async def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.post("/menu-items/")
async def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    db_item = MenuItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/menu-items/{restaurant_id}")
async def get_menu_items(restaurant_id: int, db: Session = Depends(get_db)):
    return db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()

@app.put("/menu-items/{item_id}")
async def update_menu_item(item_id: int, item: MenuItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/sync/manual")
async def manual_sync(sync_request: SyncRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger manual synchronization"""
    sync_service = SyncService(db)
    
    if sync_request.platforms:
        results = {}
        for platform in sync_request.platforms:
            results[platform] = sync_service.sync_single_platform(sync_request.restaurant_id, platform)
    else:
        results = sync_service.sync_all_platforms(sync_request.restaurant_id)
    
    return {"message": "Sync initiated", "results": results}

@app.get("/sync/status/{restaurant_id}")
async def get_sync_status(restaurant_id: int, db: Session = Depends(get_db)):
    """Get synchronization status for a restaurant"""
    sync_service = SyncService(db)
    status = sync_service.get_sync_status(restaurant_id)
    return {"restaurant_id": restaurant_id, "sync_status": status}

@app.post("/sync/restaurant-info")
async def sync_restaurant_info(sync_request: SyncRequest, db: Session = Depends(get_db)):
    """Sync restaurant information to platforms"""
    sync_service = SyncService(db)
    results = sync_service.update_restaurant_info(sync_request.restaurant_id, sync_request.platforms)
    return {"message": "Restaurant info sync completed", "results": results}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.post("/scheduler/start")
async def start_scheduler(background_tasks: BackgroundTasks):
    """Start the sync scheduler"""
    background_tasks.add_task(scheduler.start)
    return {"message": "Scheduler started"}

@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the sync scheduler"""
    scheduler.stop()
    return {"message": "Scheduler stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)