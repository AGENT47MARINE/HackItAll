from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import Profile, User
import json

def check_profiles():
    db = SessionLocal()
    try:
        profiles = db.query(Profile).all()
        print(f"Checking {len(profiles)} profiles...")
        for profile in profiles:
            user = db.query(User).filter(User.id == profile.user_id).first()
            email = user.email if user else "Unknown"
            interests = profile.interests
            skills = profile.skills
            print(f"User: {email}")
            print(f"  Level: {profile.education_level}")
            print(f"  Interests: {interests}")
            print(f"  Skills: {skills}")
            print("-" * 20)
    finally:
        db.close()

if __name__ == "__main__":
    check_profiles()
