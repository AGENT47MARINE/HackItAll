import sys
import os
import traceback
from datetime import datetime

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.opportunity import Opportunity

def test_insert():
    db = SessionLocal()
    try:
        print("🧪 Testing manual insertion with traceback...")
        opp = Opportunity(
            title="Test Opp",
            description="Test Description",
            type="hackathon",
            deadline=datetime.now(),
            application_link="https://test.com",
            tags="[]",
            required_skills="[]",
            status="active"
        )
        db.add(opp)
        db.commit()
        print("✅ Success!")
    except Exception:
        print("❌ Failed with traceback:")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_insert()
