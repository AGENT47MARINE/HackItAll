import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.notification_service import NotificationService
from models.user import User, Profile
from models.opportunity import Opportunity
from datetime import datetime, timedelta

def verify_adaptive_notifications():
    db = SessionLocal()
    try:
        print("--- VERIFYING ADAPTIVE CONNECTIVITY SUITE ---")
        
        # 1. Setup Mock User with Low-Bandwidth Mode
        from sqlalchemy import text
        user_row = db.execute(text("SELECT id, email FROM users WHERE email IS NOT NULL LIMIT 1")).fetchone()
        
        if not user_row:
            print("INFO: Creating mock user...")
            db.execute(text("INSERT INTO users (id, email, created_at, updated_at) VALUES (:id, :email, :now, :now)"), 
                       {"id": "lite-test-uid", "email": "lite_user@example.com", "now": datetime.utcnow()})
            db.commit()
            user_id = "lite-test-uid"
            user_email = "lite_user@example.com"
        else:
            user_id = user_row[0]
            user_email = user_row[1]

        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            print("INFO: Creating mock profile...")
            profile = Profile(user_id=user.id, education_level="B.Tech")
            db.add(profile)
            db.commit()
            db.refresh(profile)

        opp = db.query(Opportunity).first()
        
        if not (user_id and profile and opp):
            print("ERROR: Missing data for verification.")
            return

        service = NotificationService(db)

        # 2. Test LITE Notification (Plain Text)
        print("\n[Case A] Testing Lite Notification (is_low_bandwidth=True)")
        profile.low_bandwidth_mode = True
        db.commit()
        
        subject, body = service.format_email_message(opp, "deadline", is_low_bandwidth=True)
        print(f"Subject: {subject}")
        print(f"Body (LITE):\n{body}")
        
        if len(body) < 200:
            print("SUCCESS: Lite body is compact.")
        else:
            print("WARNING: Lite body might be too large.")

        # 3. Test RICH Notification (Standard HTML)
        print("\n[Case B] Testing Rich Notification (is_low_bandwidth=False)")
        subject, body = service.format_email_message(opp, "deadline", is_low_bandwidth=False)
        print(f"Subject: {subject}")
        print(f"Body (RICH) Starts: {body[:30]}...")
        
        # 4. SMS Formatting Check
        print("\n[Case C] Testing SMS Compression")
        sms_msg = service.format_sms_message(opp, "deadline")
        print(f"SMS: {sms_msg}")
        print(f"Length: {len(sms_msg)} (Max: 160)")
        
        if len(sms_msg) <= 160:
            print("SUCCESS: SMS within limits.")
        else:
            print("FAIL: SMS too long.")

        print("\n--- CONNECTIVITY VERIFICATION COMPLETE ---")

    except Exception as e:
        print(f"Verification Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_adaptive_notifications()
