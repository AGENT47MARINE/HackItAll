import sys
import os
import random
import uuid
import json
from datetime import datetime, timedelta

# Fix path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.user import User, Profile
from models.gamification import UserXP

def seed_mock_users(count=100):
    db = SessionLocal()
    
    print(f"Seeding {count} mock users...")
    
    for i in range(count):
        user_id = str(uuid.uuid4())
        email = f"user_{i}_{random.randint(1000, 9999)}@hackitall.ai"
        
        # 1. Create User
        new_user = User(
            id=user_id,
            email=email
        )
        db.add(new_user)
        
        # 2. Create Profile
        new_profile = Profile(
            user_id=user_id,
            education_level=random.choice(["High School", "Undergraduate", "Postgraduate", "PhD"]),
            interests=json.dumps(random.sample(["Web Development", "AI/ML", "Blockchain", "Cybersecurity", "UI/UX"], 2)),
            skills=json.dumps(random.sample(["Python", "JavaScript", "React", "Node.js", "Docker"], 2))
        )
        db.add(new_profile)
        
        # 3. Create UserXP
        xp = random.randint(50, 12000)
        # Tier logic: 
        # 1: 0, 2: 500, 3: 1500, 4: 3500, 5: 7000, 6: 15000
        tier = 1
        if xp >= 7000: tier = 5
        elif xp >= 3500: tier = 4
        elif xp >= 1500: tier = 3
        elif xp >= 500: tier = 2
        
        user_xp = UserXP(
            user_id=user_id,
            total_xp=xp,
            league_tier=tier,
            streak_days=random.randint(0, 25),
            last_login_at=datetime.utcnow() - timedelta(hours=random.randint(0, 72))
        )
        db.add(user_xp)
        
    db.commit()
    print("Seeding complete.")
    db.close()

if __name__ == "__main__":
    seed_mock_users(100)
