"""Verification script for real-world recommendations and link integrity."""
import sys
import os
import json
import uuid
from datetime import datetime

# Ensure project modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.opportunity import Opportunity
from models.user import Profile
from services.profile_service import ProfileService
from services.recommendation_service import RecommendationEngine

def verify_real_data_quality():
    """Check scraped data and verify recommendations."""
    db = SessionLocal()
    try:
        # 1. Check for real data and links
        real_opps = db.query(Opportunity).filter(Opportunity.source_url != None).all()
        print(f"Total Scraped Opportunities: {len(real_opps)}")
        
        if not real_opps:
            print("[FAILURE] No scraped data found in DB.")
            return

        print("\nVerifying Top 5 Scraped Links:")
        for opp in real_opps[:5]:
            has_link = opp.application_link.startswith("http")
            status = "[OK]" if has_link else "[MISSING LINK]"
            print(f" {status} {opp.title[:30]}... -> {opp.application_link}")

        # 2. Test Recommendation Engine with Real Data
        profile_service = ProfileService(db)
        engine = RecommendationEngine(db)

        # Create a user interested in "Software Engineering" or "Hackathon"
        user_id = f"real-test-{uuid.uuid4().hex[:6]}"
        email = f"{user_id}@example.com"
        # Most Unstop/Devpost ones have 'Hackathon' or 'Engineering'
        interests = ["Hackathon", "Coding"]
        
        print(f"\nCreating test user '{email}' with interests {interests}...")
        profile_service.create_profile(
            user_id=user_id,
            email=email,
            education_level="bachelor",
            interests=interests,
            skills=["Python", "JavaScript"]
        )

        print("Generating recommendations from real data...")
        recommendations = engine.generate_recommendations(user_id=user_id, limit=5)

        if not recommendations:
            print("[FAILURE] No recommendations generated from real data.")
            return

        print("\nTop 5 Personalized Recommendations:")
        for opp, score in recommendations:
            print(f" [{score:.2f}] {opp.title} (Tags: {opp.tags})")
            print(f"      🔗 Register: {opp.application_link}")

        print("\n[SUCCESS] Scraped data is live and recommendations are functional.")
        
    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_real_data_quality()
