from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ActionHistory(Base):
    __tablename__ = "action_history"
    
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String(100), nullable=False)  # sync, menu_update, config_change, etc.
    entity_type = Column(String(50))  # restaurant, menu_item, config, etc.
    entity_id = Column(Integer)
    user_id = Column(String(100))  # user identifier or 'system'
    action_details = Column(JSON)  # detailed action data
    result = Column(String(20))  # success, failed, partial
    error_message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)