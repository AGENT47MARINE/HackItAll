"""Opportunity database model."""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Index, Integer
import uuid

from database import Base


class Opportunity(Base):
    """Opportunity model for hackathons, scholarships, internships, and skill programs."""
    
    __tablename__ = "opportunities"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # hackathon, scholarship, internship, skill_program
    deadline = Column(DateTime, nullable=False, index=True)
    application_link = Column(String(500), nullable=False)
    image_url = Column(String(1000), nullable=True)  # Store scraped og:image
    tags = Column(Text, nullable=False, default="[]")  # JSON array stored as text
    required_skills = Column(Text, nullable=True, default="[]")  # JSON array stored as text
    eligibility = Column(String(50), nullable=True)  # education level eligibility
    location = Column(String(255), nullable=True)
    location_type = Column(String(50), nullable=False, default="Online", index=True)  # Online, In-Person, Hybrid
    source_url = Column(String(1000), nullable=True, unique=True)  # Used for dedup during scraping
    status = Column(String(20), default="active", nullable=False, index=True)  # active, archived
    tracked_count = Column(Integer, default=0, nullable=False, index=True) # Used for Trending Algorithm
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Add composite indexes for common queries
    __table_args__ = (
        Index('idx_opportunities_type', 'type'),
        Index('idx_opportunities_deadline', 'deadline'),
        Index('idx_opportunities_status', 'status'),
        Index('idx_opportunities_type_status', 'type', 'status'),
        Index('idx_opportunities_deadline_status', 'deadline', 'status'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.tags is None:
            self.tags = "[]"
        if self.required_skills is None:
            self.required_skills = "[]"
        if self.status is None:
            self.status = "active"
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, title={self.title}, type={self.type}, status={self.status})>"
