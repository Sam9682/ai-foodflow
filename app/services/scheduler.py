import schedule
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.sync_service import SyncService
from app.models.restaurant import Restaurant
import logging

logger = logging.getLogger(__name__)

class SyncScheduler:
    def __init__(self):
        self.is_running = False
    
    def setup_schedules(self):
        # Daily sync at 2 AM
        schedule.every().day.at("02:00").do(self.daily_sync)
        
        # Weekly full sync on Sunday at 1 AM
        schedule.every().sunday.at("01:00").do(self.weekly_full_sync)
        
        # Hourly availability check
        schedule.every().hour.do(self.availability_sync)
        
        logger.info("Sync schedules configured")
    
    def daily_sync(self):
        """Daily menu and price synchronization"""
        logger.info("Starting daily sync")
        db = SessionLocal()
        try:
            sync_service = SyncService(db)
            restaurants = db.query(Restaurant).all()
            
            for restaurant in restaurants:
                logger.info(f"Syncing restaurant: {restaurant.name}")
                results = sync_service.sync_all_platforms(restaurant.id)
                
                for platform, result in results.items():
                    if result.get("success"):
                        logger.info(f"Successfully synced {restaurant.name} to {platform}")
                    else:
                        logger.error(f"Failed to sync {restaurant.name} to {platform}: {result.get('error')}")
        
        except Exception as e:
            logger.error(f"Daily sync failed: {e}")
        finally:
            db.close()
    
    def weekly_full_sync(self):
        """Weekly full synchronization including restaurant info"""
        logger.info("Starting weekly full sync")
        db = SessionLocal()
        try:
            sync_service = SyncService(db)
            restaurants = db.query(Restaurant).all()
            
            for restaurant in restaurants:
                logger.info(f"Full sync for restaurant: {restaurant.name}")
                
                # Sync restaurant information
                info_results = sync_service.update_restaurant_info(restaurant.id)
                
                # Sync menu items
                menu_results = sync_service.sync_all_platforms(restaurant.id)
                
                logger.info(f"Full sync completed for {restaurant.name}")
        
        except Exception as e:
            logger.error(f"Weekly full sync failed: {e}")
        finally:
            db.close()
    
    def availability_sync(self):
        """Hourly availability status sync"""
        logger.info("Starting availability sync")
        db = SessionLocal()
        try:
            sync_service = SyncService(db)
            restaurants = db.query(Restaurant).all()
            
            for restaurant in restaurants:
                # Only sync menu items (includes availability)
                results = sync_service.sync_all_platforms(restaurant.id)
                
                for platform, result in results.items():
                    if not result.get("success"):
                        logger.warning(f"Availability sync failed for {restaurant.name} on {platform}")
        
        except Exception as e:
            logger.error(f"Availability sync failed: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start the scheduler"""
        self.is_running = True
        self.setup_schedules()
        logger.info("Scheduler started")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        logger.info("Scheduler stopped")
    
    def run_manual_sync(self, restaurant_id: int = None, platform: str = None):
        """Manually trigger sync"""
        db = SessionLocal()
        try:
            sync_service = SyncService(db)
            
            if restaurant_id and platform:
                result = sync_service.sync_single_platform(restaurant_id, platform)
                logger.info(f"Manual sync result: {result}")
                return result
            elif restaurant_id:
                result = sync_service.sync_all_platforms(restaurant_id)
                logger.info(f"Manual sync result: {result}")
                return result
            else:
                # Sync all restaurants
                restaurants = db.query(Restaurant).all()
                results = {}
                for restaurant in restaurants:
                    results[restaurant.id] = sync_service.sync_all_platforms(restaurant.id)
                return results
        
        except Exception as e:
            logger.error(f"Manual sync failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

# Global scheduler instance
scheduler = SyncScheduler()