import sys
import os
import random

# Ensure project modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.opportunity import Opportunity

def seed_trending():
    """Assign random tracked_count values to active opportunities."""
    db = SessionLocal()
    try:
        # Get all active opportunities
        opportunities = db.query(Opportunity).filter(Opportunity.status == "active").all()
        
        if not opportunities:
            print("No active opportunities found to update.")
            return

        print(f"Found {len(opportunities)} active opportunities. Assigning trending data...")

        for opp in opportunities:
            # Assign a random tracked count between 5 and 50 to make them "trending"
            # Some will have higher counts than others
            opp.tracked_count = random.randint(5, 50)
            print(f"Updated '{opp.title}' with tracked_count={opp.tracked_count}")

        db.commit()
        print("\nSuccessfully updated trending data!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding trending data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_trending()
