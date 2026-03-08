import sys
import os
from datetime import datetime
import json

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
from models.opportunity import Opportunity

def test_insert():
    # Recreate tables with new schema
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("🧪 Testing manual insertion after schema reset...")
        opp = Opportunity(
            title="Test Opp",
            description="Test Description",
            type="hackathon",
            deadline=datetime.now().isoformat(),
            application_link="https://test.com",
            tags="[]",
            required_skills="[]",
            status="active"
        )
        db.add(opp)
        db.commit()
        print("✅ Success!")
    except Exception as e:
        db.rollback()
        print(f"❌ Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_insert()
