import sys
import os
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.opportunity import Opportunity
from database import engine, SessionLocal

def clear_opportunities():
    db = SessionLocal()
    try:
        print("🗑️ Deleting all existing opportunities...")
        count = db.query(Opportunity).delete()
        db.commit()
        print(f"✅ Successfully deleted {count} opportunities.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during deletion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_opportunities()
