"""Manual cleanup script for expired opportunities."""
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.opportunity import Opportunity
from models.tracking import TrackedOpportunity
from models.reminder import Reminder

def cleanup_expired():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Find all expired opportunities
        expired = db.query(Opportunity).filter(Opportunity.deadline < now).all()
        expired_ids = [opp.id for opp in expired]
        
        if not expired_ids:
            print("No expired opportunities found.")
            return

        print(f"Found {len(expired_ids)} expired opportunities.")
        
        # 1. Clean up reminders
        reminders_deleted = db.query(Reminder).filter(Reminder.opportunity_id.in_(expired_ids)).delete(synchronize_session=False)
        print(f"Deleted {reminders_deleted} associated reminders.")
        
        # 2. Clean up tracked opportunities
        tracked_deleted = db.query(TrackedOpportunity).filter(TrackedOpportunity.opportunity_id.in_(expired_ids)).delete(synchronize_session=False)
        print(f"Deleted {tracked_deleted} associated tracking records.")
        
        # 3. Delete the opportunities
        opps_deleted = db.query(Opportunity).filter(Opportunity.id.in_(expired_ids)).delete(synchronize_session=False)
        print(f"Successfully deleted {opps_deleted} expired opportunities.")
        
        db.commit()
        print("Cleanup complete.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_expired()
