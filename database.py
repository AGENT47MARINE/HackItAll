"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import config

# Create database engine
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and seed initial data."""
    # Import all models here to ensure they are registered with Base metadata
    from models.user import User, Profile, ContentView
    from models.opportunity import Opportunity
    from models.tracking import TrackedOpportunity, ParticipationHistory
    from models.reminder import Reminder
    from models.gamification import UserXP, XPTransaction, Achievement, UserAchievement
    from models.team import Team, TeamMember, TeamRequest
    from models.intelligence import HistoricalProject, ScoutAnalysis, SquadBlueprint, PitchBlueprint, AuditReport
    
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed achievements
    from sqlalchemy.orm import Session
    from services.gamification_service import GamificationService
    
    db = Session(bind=engine)
    try:
        service = GamificationService(db)
        service.seed_achievements()
    finally:
        db.close()
