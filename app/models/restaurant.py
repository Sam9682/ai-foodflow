from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    cuisine_type = Column(String(100))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    opening_hours = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(100))
    is_available = Column(Boolean, default=True)
    image_url = Column(String(500))
    allergens = Column(JSON)
    nutritional_info = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PlatformSync(Base):
    __tablename__ = "platform_syncs"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, nullable=False)
    platform = Column(String(50), nullable=False)  # uber_eats, deliveroo, just_eat
    platform_restaurant_id = Column(String(255))
    last_sync = Column(DateTime(timezone=True))
    sync_status = Column(String(20), default="pending")  # pending, success, failed
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())