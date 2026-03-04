"""
Migrate data from SQLite to PostgreSQL.
Run this AFTER the PostgreSQL container is up and tables are created.

Usage:
    python scripts/migrate_sqlite_to_pg.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Source: SQLite
SQLITE_URL = "sqlite:///./opportunity_platform.db"

# Target: PostgreSQL (from .env)
from dotenv import load_dotenv
load_dotenv()
PG_URL = os.getenv("DATABASE_URL")

if not PG_URL or "postgresql" not in PG_URL:
    print("ERROR: DATABASE_URL is not set to a PostgreSQL URL in .env")
    sys.exit(1)

# Import all models so metadata is populated
from database import Base
from models.user import User, Profile
from models.opportunity import Opportunity
from models.tracking import TrackedOpportunity, ParticipationHistory
from models.reminder import Reminder

# Create engines
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
pg_engine = create_engine(PG_URL)

SqliteSession = sessionmaker(bind=sqlite_engine)
PgSession = sessionmaker(bind=pg_engine)

def migrate():
    """Migrate all data from SQLite to PostgreSQL."""
    
    # 1. Create all tables in PostgreSQL
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=pg_engine)
    print("Tables created successfully.")
    
    sqlite_db = SqliteSession()
    pg_db = PgSession()
    
    try:
        # 2. Migrate Users
        users = sqlite_db.query(User).all()
        print(f"\nMigrating {len(users)} users...")
        for user in users:
            existing = pg_db.query(User).filter(User.id == user.id).first()
            if not existing:
                pg_db.merge(user)
        pg_db.commit()
        print(f"  ✅ Users migrated.")

        # 3. Migrate Profiles
        profiles = sqlite_db.query(Profile).all()
        print(f"\nMigrating {len(profiles)} profiles...")
        for p in profiles:
            existing = pg_db.query(Profile).filter(Profile.user_id == p.user_id).first()
            if not existing:
                pg_db.merge(p)
        pg_db.commit()
        print(f"  ✅ Profiles migrated.")
        
        # 4. Migrate Opportunities  
        opportunities = sqlite_db.query(Opportunity).all()
        print(f"\nMigrating {len(opportunities)} opportunities...")
        for opp in opportunities:
            existing = pg_db.query(Opportunity).filter(Opportunity.id == opp.id).first()
            if not existing:
                pg_db.merge(opp)
        pg_db.commit()
        print(f"  ✅ Opportunities migrated.")
        
        # 5. Migrate Tracked Opportunities
        trackings = sqlite_db.query(TrackedOpportunity).all()
        print(f"\nMigrating {len(trackings)} tracked opportunities...")
        for t in trackings:
            existing = pg_db.query(TrackedOpportunity).filter(
                TrackedOpportunity.user_id == t.user_id,
                TrackedOpportunity.opportunity_id == t.opportunity_id
            ).first()
            if not existing:
                pg_db.merge(t)
        pg_db.commit()
        print(f"  ✅ Tracked opportunities migrated.")

        # 6. Migrate Participation History
        participations = sqlite_db.query(ParticipationHistory).all()
        print(f"\nMigrating {len(participations)} participation records...")
        for p in participations:
            existing = pg_db.query(ParticipationHistory).filter(ParticipationHistory.id == p.id).first()
            if not existing:
                pg_db.merge(p)
        pg_db.commit()
        print(f"  ✅ Participation history migrated.")
        
        # 7. Migrate Reminders
        reminders = sqlite_db.query(Reminder).all()
        print(f"\nMigrating {len(reminders)} reminders...")
        for r in reminders:
            existing = pg_db.query(Reminder).filter(Reminder.id == r.id).first()
            if not existing:
                pg_db.merge(r)
        pg_db.commit()
        print(f"  ✅ Reminders migrated.")
        
        # 8. Summary
        pg_users = pg_db.query(User).count()
        pg_profiles = pg_db.query(Profile).count()
        pg_opps = pg_db.query(Opportunity).count()
        pg_tracks = pg_db.query(TrackedOpportunity).count()
        pg_reminders = pg_db.query(Reminder).count()
        
        print(f"\n{'='*50}")
        print(f"Migration Complete!")
        print(f"  Users:         {pg_users}")
        print(f"  Profiles:      {pg_profiles}")
        print(f"  Opportunities: {pg_opps}")
        print(f"  Trackings:     {pg_tracks}")
        print(f"  Reminders:     {pg_reminders}")
        print(f"{'='*50}")
        
    except Exception as e:
        pg_db.rollback()
        print(f"\nERROR during migration: {e}")
        raise
    finally:
        sqlite_db.close()
        pg_db.close()


if __name__ == "__main__":
    migrate()
