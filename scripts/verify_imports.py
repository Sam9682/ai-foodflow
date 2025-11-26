#!/usr/bin/env python3
"""Verify that all imports work with the new src structure"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing imports with new src structure...")
        
        # Test core imports
        from src.app.core.database import SessionLocal, create_tables
        print("✅ Core database imports working")
        
        # Test model imports
        from src.app.models.restaurant import Restaurant, MenuItem
        print("✅ Model imports working")
        
        # Test service imports
        from src.app.services.sync_service import SyncService
        from src.app.services.ai_bot import RestaurantAIBot
        print("✅ Service imports working")
        
        # Test API imports
        from src.app.api.main import app
        print("✅ API imports working")
        
        print("\n🎉 All imports successful! The src structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)