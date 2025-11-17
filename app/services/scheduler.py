import schedule
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.sync_service import SyncService
from app.models.restaurant import Restaurant
import logging
from app.core.logging_config import setup_logging

# Ensure logging is configured
setup_logging()
logger = logging.getLogger(__name__)

class SyncScheduler:
    def __init__(self):
        self.is_running = False
        self.failure_counts = {}  # Track failures per restaurant/platform
        self.max_retries = 3
        self.disabled_syncs = set()  # Track disabled sync combinations
    
    def setup_schedules(self):
        # Daily sync at 2 AM
        schedule.every().day.at("02:00").do(self.daily_sync)
        
        # Weekly full sync on Sunday at 1 AM
        schedule.every().sunday.at("01:00").do(self.weekly_full_sync)
        
        # Hourly availability check
        schedule.every().hour.do(self.availability_sync)
        
        logger.info("Sync schedules configured")
    
    def daily_sync(self):
        """Daily menu and price synchronization with retry tracking"""
        logger.info("Starting daily sync")
        db = SessionLocal()
        try:
            sync_service = SyncService(db)
            restaurants = db.query(Restaurant).all()
            
            for restaurant in restaurants:
                logger.info(f"Syncing restaurant: {restaurant.name}")
                results = sync_service.sync_all_platforms(restaurant.id)
                
                for platform, result in results.items():
                    sync_key = f"{restaurant.id}_{platform}"
                    
                    if result.get("success"):
                        # Reset failure count on success
                        if sync_key in self.failure_counts:
                            del self.failure_counts[sync_key]
                        if sync_key in self.disabled_syncs:
                            self.disabled_syncs.remove(sync_key)
                            logger.info(f"Re-enabled sync for {restaurant.name} on {platform} after successful daily sync")
                        logger.info(f"Successfully synced {restaurant.name} to {platform}")
                    else:
                        logger.error(f"Failed to sync {restaurant.name} to {platform}: {result.get('error')}")
        
        except Exception as e:
            logger.error(f"Daily sync failed: {e}")
        finally:
            db.close()
    
    def weekly_full_sync(self):
        """Weekly full synchronization including restaurant info with retry tracking"""
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
                
                # Reset failure counts for successful syncs
                for platform, result in menu_results.items():
                    sync_key = f"{restaurant.id}_{platform}"
                    if result.get("success"):
                        if sync_key in self.failure_counts:
                            del self.failure_counts[sync_key]
                        if sync_key in self.disabled_syncs:
                            self.disabled_syncs.remove(sync_key)
                            logger.info(f"Re-enabled sync for {restaurant.name} on {platform} after successful weekly sync")
                
                logger.info(f"Full sync completed for {restaurant.name}")
        
        except Exception as e:
            logger.error(f"Weekly full sync failed: {e}")
        finally:
            db.close()
    
    def availability_sync(self):
        """Hourly availability status sync with retry limit"""
        logger.info("Starting availability sync")
        db = SessionLocal()
        try:
            sync_service = SyncService(db)
            restaurants = db.query(Restaurant).all()
            
            for restaurant in restaurants:
                # Check if any platforms are disabled for this restaurant
                disabled_platforms = [platform for platform in ['uber_eats', 'deliveroo', 'just_eat'] 
                                    if f"{restaurant.id}_{platform}" in self.disabled_syncs]
                
                if disabled_platforms:
                    logger.warning(f"Skipping disabled platforms for {restaurant.name}: {disabled_platforms}")
                
                # Only sync menu items (includes availability)
                results = sync_service.sync_all_platforms(restaurant.id)
                
                for platform, result in results.items():
                    sync_key = f"{restaurant.id}_{platform}"
                    
                    if sync_key in self.disabled_syncs:
                        continue  # Skip disabled sync combinations
                    
                    if result.get("success"):
                        # Reset failure count on success
                        if sync_key in self.failure_counts:
                            del self.failure_counts[sync_key]
                            logger.info(f"Availability sync recovered for {restaurant.name} on {platform}")
                    else:
                        # Track failure
                        self.failure_counts[sync_key] = self.failure_counts.get(sync_key, 0) + 1
                        failure_count = self.failure_counts[sync_key]
                        
                        logger.warning(f"Availability sync failed for {restaurant.name} on {platform} (attempt {failure_count}/{self.max_retries}): {result.get('error')}")
                        
                        # Disable sync if max retries exceeded
                        if failure_count >= self.max_retries:
                            self.disabled_syncs.add(sync_key)
                            logger.error(f"Disabling automatic sync for {restaurant.name} on {platform} after {self.max_retries} failures. Manual intervention required.")
        
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
                sync_key = f"{restaurant_id}_{platform}"
                
                # Re-enable sync if it was disabled
                if sync_key in self.disabled_syncs:
                    self.disabled_syncs.remove(sync_key)
                    self.failure_counts.pop(sync_key, None)
                    logger.info(f"Re-enabled automatic sync for restaurant {restaurant_id} on {platform}")
                
                result = sync_service.sync_single_platform(restaurant_id, platform)
                logger.info(f"Manual sync result: {result}")
                return result
            elif restaurant_id:
                # Re-enable all platforms for this restaurant
                platforms = ['uber_eats', 'deliveroo', 'just_eat']
                for platform in platforms:
                    sync_key = f"{restaurant_id}_{platform}"
                    if sync_key in self.disabled_syncs:
                        self.disabled_syncs.remove(sync_key)
                        self.failure_counts.pop(sync_key, None)
                        logger.info(f"Re-enabled automatic sync for restaurant {restaurant_id} on {platform}")
                
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
    
    def get_disabled_syncs(self):
        """Get list of disabled sync combinations"""
        disabled_list = []
        for sync_key in self.disabled_syncs:
            restaurant_id, platform = sync_key.split('_', 1)
            disabled_list.append({
                "restaurant_id": int(restaurant_id),
                "platform": platform,
                "failure_count": self.failure_counts.get(sync_key, 0)
            })
        return disabled_list
    
    def reset_sync_failures(self, restaurant_id: int = None, platform: str = None):
        """Reset failure counts and re-enable syncs"""
        if restaurant_id and platform:
            sync_key = f"{restaurant_id}_{platform}"
            self.disabled_syncs.discard(sync_key)
            self.failure_counts.pop(sync_key, None)
            logger.info(f"Reset sync failures for restaurant {restaurant_id} on {platform}")
        elif restaurant_id:
            # Reset all platforms for restaurant
            platforms = ['uber_eats', 'deliveroo', 'just_eat']
            for platform in platforms:
                sync_key = f"{restaurant_id}_{platform}"
                self.disabled_syncs.discard(sync_key)
                self.failure_counts.pop(sync_key, None)
            logger.info(f"Reset all sync failures for restaurant {restaurant_id}")
        else:
            # Reset all failures
            self.disabled_syncs.clear()
            self.failure_counts.clear()
            logger.info("Reset all sync failures")
    
    def get_sync_status(self):
        """Get current sync status including failures and disabled syncs"""
        return {
            "is_running": self.is_running,
            "failure_counts": dict(self.failure_counts),
            "disabled_syncs": list(self.disabled_syncs),
            "max_retries": self.max_retries
        }

# Global scheduler instance
scheduler = SyncScheduler()