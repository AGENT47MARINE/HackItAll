"""Tracking database models for saved opportunities and participation history."""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
import uuid

from database import Base


class TrackedOpportunity(Base):
    """TrackedOpportunity model for opportunities saved by users."""
    
    __tablename__ = "tracked_opportunities"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True)
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_expired = Column(Boolean, default=False, nullable=False)
    
    # Add composite index for efficient queries
    __table_args__ = (
        Index('idx_tracked_user_expired', 'user_id', 'is_expired'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.saved_at is None:
            self.saved_at = datetime.utcnow()
        if self.is_expired is None:
            self.is_expired = False
    
    def __repr__(self):
        return f"<TrackedOpportunity(user_id={self.user_id}, opportunity_id={self.opportunity_id}, is_expired={self.is_expired})>"


class ParticipationHistory(Base):
    """ParticipationHistory model for tracking user participation in opportunities."""
    
    __tablename__ = "participation_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)  # applied, accepted, rejected, completed
    current_round = Column(String(36), default="1", nullable=True) # e.g., "1", "2", "Final"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Add relationship to opportunity for efficient JOIN queries
    opportunity = relationship("Opportunity", lazy="select")
    
    # Add index for efficient user queries
    __table_args__ = (
        Index('idx_participation_user', 'user_id'),
        Index('idx_participation_user_opportunity', 'user_id', 'opportunity_id'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<ParticipationHistory(id={self.id}, user_id={self.user_id}, opportunity_id={self.opportunity_id}, status={self.status})>"
