"""Reminder model for deadline notifications."""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base


class Reminder(Base):
    """Model for storing deadline reminders."""
    
    __tablename__ = "reminders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    opportunity_id = Column(String, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    opportunity = relationship("Opportunity")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_reminders_scheduled', 'scheduled_time', 'sent'),
        Index('idx_reminders_user', 'user_id'),
    )
    
    def __repr__(self):
        return f"<Reminder(id={self.id}, user_id={self.user_id}, scheduled_time={self.scheduled_time}, sent={self.sent})>"
