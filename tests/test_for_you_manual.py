"""Manual test script to verify 'For You' recommendations."""
import sys
import os
import uuid
from datetime import datetime, timedelta

# Ensure project modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.profile_service import ProfileService
from services.opportunity_service import OpportunityService
from services.recommendation_service import RecommendationEngine
from models.user import User, Profile
from models.opportunity import Opportunity

def test_for_you_recommendations():
    """Verify that recommendations are personalized based on profile."""
    db = SessionLocal()
    try:
        profile_service = ProfileService(db)
        opportunity_service = OpportunityService(db)
        engine = RecommendationEngine(db)

        # 1. Create a test user with specific interests
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        email = f"{user_id}@example.com"
        interests = ["Blockchain", "Web3"]
        skills = ["Solidity", "JavaScript"]
        
        print(f"Creating test profile for {email} with interests {interests}...")
        profile_service.create_profile(
            user_id=user_id,
            email=email,
            education_level="bachelor",
            interests=interests,
            skills=skills
        )

        # 2. Get recommendations
        print("Generating recommendations...")
        recommendations = engine.generate_recommendations(user_id=user_id, limit=5)

        if not recommendations:
            print("No recommendations generated.")
            return

        print(f"\nTop Recommendations for {email}:")
        found_blockchain = False
        for opp, score in recommendations:
            print(f"- [{score:.2f}] {opp.title} (Type: {opp.type}, Tags: {opp.tags})")
            if "Blockchain" in opp.tags or "Web3" in opp.tags:
                found_blockchain = True

        # 3. Verification
        if found_blockchain:
            print("\n[SUCCESS] Found Blockchain/Web3 opportunities in recommendations!")
        else:
            print("\n[WARNING] No Blockchain/Web3 opportunities found. Check scoring logic.")

        # Cleanup test user
        # Note: We might want to keep it or delete it. For now, let's keep it in the test DB.
        
    except Exception as e:
        print(f"Error testing recommendations: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_for_you_recommendations()
