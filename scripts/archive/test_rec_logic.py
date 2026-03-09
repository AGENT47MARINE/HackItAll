
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json

from models.opportunity import Opportunity
from models.user import Profile
from services.recommendation_service import RecommendationEngine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://hackitall:hackitall_pwd@localhost:5432/hackitall_db")

def test_recommendation_logic():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session(autoflush=False)
    
    # Use the same test user
    user_id = "user_test_verify_domains"
    print(f"Testing RECOMMENDATION LOGIC for user_id: {user_id}")
    
    # Check if this user exists
    from models.user import Profile
    profile = session.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        # Create a mock profile if it doesn't exist for test
        profile = Profile(user_id=user_id, interests=json.dumps(["AI", "Web3"]), skills=json.dumps(["Python"]))
        session.add(profile)
        session.commit()
    
    rec_engine = RecommendationEngine(session)
    recs = rec_engine.generate_recommendations(user_id=user_id, limit=5)
    
    print(f"\nFound {len(recs)} recommendations.")
    for opp, score in recs:
        print(f" - {opp.title}: image_url={opp.image_url}, type={opp.type}")
    
    session.close()

if __name__ == "__main__":
    test_recommendation_logic()
