"""Team models for collaboration on opportunities."""
import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class Team(Base):
    """Model representing a team formed for an opportunity."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    leader_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    needed_skills = Column(String, nullable=True)  # JSON string list of skills
    max_members = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    opportunity = relationship("Opportunity")
    leader = relationship("User", foreign_keys=[leader_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    requests = relationship("TeamRequest", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    """Model representing a user's membership in a team."""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, default="member")  # 'leader', 'member'
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User")


class TeamRequest(Base):
    """Model representing a user's request to join a team."""
    __tablename__ = "team_requests"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String, default="pending")  # 'pending', 'accepted', 'rejected'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="requests")
    user = relationship("User")
