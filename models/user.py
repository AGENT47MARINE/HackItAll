"""User and Profile database models."""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database import Base


class User(Base):
    """User model for authentication and basic user information."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to profile
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Profile(Base):
    """Profile model for user preferences and personalization data."""
    
    __tablename__ = "profiles"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    interests = Column(Text, nullable=False, default="[]")  # JSON array stored as text
    skills = Column(Text, nullable=False, default="[]")  # JSON array stored as text
    education_level = Column(String(50), nullable=False)
    notification_email = Column(Boolean, default=True, nullable=False)
    notification_sms = Column(Boolean, default=False, nullable=False)
    low_bandwidth_mode = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="profile")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.interests is None:
            self.interests = "[]"
        if self.skills is None:
            self.skills = "[]"
        if self.notification_email is None:
            self.notification_email = True
        if self.notification_sms is None:
            self.notification_sms = False
        if self.low_bandwidth_mode is None:
            self.low_bandwidth_mode = False
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, education_level={self.education_level})>"
