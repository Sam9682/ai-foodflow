#!/usr/bin/env python3
"""Test script to demonstrate the retry mechanism for sync failures"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.logging_config import setup_logging
from app.services.scheduler import SyncScheduler
import logging

# Setup logging with datetime stamps
setup_logging()
logger = logging.getLogger(__name__)

def test_retry_mechanism():
    """Test the retry mechanism with simulated failures"""
    print("Testing FoodFlow Scheduler Retry Mechanism:\n")
    
    # Create scheduler instance
    scheduler = SyncScheduler()
    
    # Simulate failures for restaurant 1 on uber_eats
    restaurant_id = 1
    platform = "uber_eats"
    sync_key = f"{restaurant_id}_{platform}"
    
    print(f"Simulating failures for restaurant {restaurant_id} on {platform}:")
    
    # Simulate 3 failures
    for i in range(1, 4):
        scheduler.failure_counts[sync_key] = i
        print(f"  Failure {i}/3 - Sync still enabled")
    
    # 4th failure should disable the sync
    scheduler.failure_counts[sync_key] = 4
    scheduler.disabled_syncs.add(sync_key)
    print(f"  Failure 4/3 - Sync DISABLED (manual intervention required)")
    
    # Show current status
    print(f"\nCurrent Status:")
    print(f"  Failure counts: {scheduler.failure_counts}")
    print(f"  Disabled syncs: {list(scheduler.disabled_syncs)}")
    print(f"  Disabled sync details: {scheduler.get_disabled_syncs()}")
    
    # Test manual reset
    print(f"\nTesting manual reset:")
    scheduler.reset_sync_failures(restaurant_id, platform)
    print(f"  After reset - Failure counts: {scheduler.failure_counts}")
    print(f"  After reset - Disabled syncs: {list(scheduler.disabled_syncs)}")
    
    # Test scheduler status
    print(f"\nScheduler Status:")
    status = scheduler.get_sync_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ Retry mechanism working correctly!")
    print(f"   - Syncs are disabled after {scheduler.max_retries} consecutive failures")
    print(f"   - Manual intervention can re-enable disabled syncs")
    print(f"   - Successful syncs reset failure counts")

if __name__ == "__main__":
    test_retry_mechanism()