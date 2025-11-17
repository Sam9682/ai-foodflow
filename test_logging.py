#!/usr/bin/env python3
"""Test script to demonstrate datetime logging functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.logging_config import setup_logging
import logging

# Setup logging with datetime stamps
setup_logging()

# Get loggers for different modules
main_logger = logging.getLogger('app.api.main')
sync_logger = logging.getLogger('app.services.sync_service')
scheduler_logger = logging.getLogger('app.services.scheduler')
ai_logger = logging.getLogger('app.services.ai_bot')
mcp_logger = logging.getLogger('mcp_server')

def test_logging():
    """Test logging with datetime stamps"""
    print("Testing FoodFlow logging with datetime stamps:\n")
    
    main_logger.info("FastAPI application starting up")
    main_logger.info("Database initialized and configuration synced")
    
    sync_logger.info("Starting daily sync")
    sync_logger.info("Syncing restaurant: Le Bouzou")
    sync_logger.info("Successfully synced Le Bouzou to uber_eats")
    sync_logger.error("Failed to sync Le Bouzou to deliveroo: Authentication failed")
    
    scheduler_logger.info("Sync schedules configured")
    scheduler_logger.info("Scheduler started")
    scheduler_logger.info("Starting availability sync")
    
    ai_logger.info("Processing message for restaurant 1: Show me my current menu...")
    ai_logger.info("Sending request to OpenAI API with model: gpt-3.5-turbo")
    ai_logger.info("Successfully received response from OpenAI API")
    
    mcp_logger.info("Starting FoodFlow MCP Server")
    mcp_logger.info("Database tables initialized")
    mcp_logger.info("MCP Server ready for connections")
    mcp_logger.info("Starting platform sync for restaurant 1 to platforms: ['uber_eats', 'deliveroo']")
    mcp_logger.info("Platform sync completed: 1/2 platforms successful")
    
    print("\nAll log messages now include datetime stamps!")

if __name__ == "__main__":
    test_logging()