"""Intelligence models for Strategic AI Scout and Squad Architect."""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
import uuid

from database import Base

class HistoricalProject(Base):
    """Stores data about past winning projects from various hackathons."""
    __tablename__ = "historical_projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_id = Column(String(255), unique=True) # Source platform project ID
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    domain = Column(String(100), nullable=False, index=True) # e.g., devpost.com
    event_name = Column(String(255), nullable=False)
    winning_prize = Column(String(255))
    tech_stack = Column(JSON, default=[]) # List of technologies used
    tags = Column(JSON, default=[])
    submission_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class ScoutAnalysis(Base):
    """Stores strategic analysis for a specific hackathon."""
    __tablename__ = "scout_analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id = Column(String(36), ForeignKey("opportunities.id"), unique=True)
    
    winning_criteria = Column(Text) # AI summary of what judges look for
    suggested_tech_stack = Column(JSON) # Recommended stacks based on history
    track_difficulty = Column(JSON) # AI rating of different track competitiveness
    strategic_advice = Column(Text) # "Secret Sauce" advice
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    opportunity = relationship("Opportunity")

class SquadBlueprint(Base):
    """Stores the AI-generated sprint roadmap for a team."""
    __tablename__ = "squad_blueprints"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True)
    
    roadmap = Column(JSON) # Step-by-step 48hr guide
    suggested_skeleton = Column(Text) # Boilerplate suggestion
    role_assignments = Column(JSON) # Who does what based on skills
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team")

class PitchBlueprint(Base):
    """Stores AI-generated pitch assets for a team."""
    __tablename__ = "pitch_blueprints"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True)
    
    elevator_pitch = Column(Text)
    demo_script = Column(Text)
    slide_blueprint = Column(JSON) # List of slide objects {title, content, visual_tip}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    team = relationship("Team")

class AuditReport(Base):
    """Stores AI Judge audit results for a draft submission."""
    __tablename__ = "audit_reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True)
    
    winning_probability = Column(Float) # 0 to 1
    red_flags = Column(JSON) # List of critical issues
    improvements = Column(JSON) # Suggested fixes
    judge_persona_feedback = Column(Text)
    
    audited_at = Column(DateTime, default=datetime.utcnow)
    team = relationship("Team")
