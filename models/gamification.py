from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
import uuid

from database import Base


class UserXP(Base):
    """Stores user's current league status, total XP, and streak."""
    
    __tablename__ = "user_xp"
    
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_xp = Column(Integer, default=0, nullable=False)
    league_tier = Column(Integer, default=1, nullable=False)  # 1=Bronze, 6=Obsidian
    streak_days = Column(Integer, default=0, nullable=False)
    last_xp_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = relationship("User", backref="xp_stats")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.total_xp is None:
            self.total_xp = 0
        if self.league_tier is None:
            self.league_tier = 1
        if self.streak_days is None:
            self.streak_days = 0
        if self.last_login_at is None:
            self.last_login_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


class XPTransaction(Base):
    """Logs individual XP gain events for audit and history."""
    
    __tablename__ = "xp_transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    xp_amount = Column(Integer, nullable=False)
    action_type = Column(String(50), nullable=False)  # track, apply, complete, scrape, view, daily_login
    reference_id = Column(String(255), nullable=True)  # ID of the opportunity, content, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class Achievement(Base):
    """Defined achievements that users can unlock."""
    
    __tablename__ = "achievements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., 'first_track'
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    icon_name = Column(String(50), nullable=False)  # reference to frontend pixel-art asset
    xp_reward = Column(Integer, default=0, nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())


class UserAchievement(Base):
    """Relationship table for users and unlocked achievements."""
    
    __tablename__ = "user_achievements"
    
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    achievement_id = Column(String(36), ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True)
    unlocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to achievement
    achievement = relationship("Achievement")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.unlocked_at is None:
            self.unlocked_at = datetime.utcnow()
