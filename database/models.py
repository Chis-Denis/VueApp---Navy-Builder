from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class UserRole(str, enum.Enum):
    REGULAR = "regular"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.REGULAR)
    is_monitored = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    logs = relationship("ActivityLog", back_populates="user")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # CREATE, READ, UPDATE, DELETE
    entity_type = Column(String)  # Type of entity affected
    entity_id = Column(Integer)  # ID of affected entity
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="logs") 