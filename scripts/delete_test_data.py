from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.user import User, Profile, ContentView
from models.opportunity import Opportunity
from models.tracking import TrackedOpportunity, ParticipationHistory
from models.reminder import Reminder
from models.gamification import UserXP, XPTransaction, Achievement, UserAchievement
from models.team import Team, TeamMember, TeamRequest
from models.intelligence import HistoricalProject, ScoutAnalysis, SquadBlueprint, PitchBlueprint, AuditReport

def delete_all_data():
    db = SessionLocal()
    try:
        print("Trashing all test data...")
        
        # Delete in order of dependencies
        db.query(ParticipationHistory).delete()
        db.query(TrackedOpportunity).delete()
        db.query(Reminder).delete()
        db.query(UserXP).delete()
        db.query(XPTransaction).delete()
        db.query(UserAchievement).delete()
        db.query(TeamRequest).delete()
        db.query(TeamMember).delete()
        db.query(Team).delete()
        db.query(ScoutAnalysis).delete()
        db.query(SquadBlueprint).delete()
        db.query(PitchBlueprint).delete()
        db.query(AuditReport).delete()
        db.query(HistoricalProject).delete()
        db.query(ContentView).delete()
        # Profiles depend on Users
        db.query(Profile).delete()
        db.query(User).delete()
        # Opportunities are largely independent but could be tracked
        db.query(Opportunity).delete()
        
        db.commit()
        print("Database cleared successfully (except for core metadata like Achievements).")
    except Exception as e:
        db.rollback()
        print(f"Error clearing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_all_data()
