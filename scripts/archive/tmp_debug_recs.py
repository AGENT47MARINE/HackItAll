import sys
import os
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User, Profile
from models.opportunity import Opportunity
from services.recommendation_service import RecommendationEngine

def check_recommendations(email):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"User with email {email} not found")
        return

    profile = user.profile
    if not profile:
        print(f"Profile for user {user.username} not found")
        return

    print(f"User: {user.username} ({user.email})")
    print(f"Profile Skills: {profile.skills}")
    print(f"Profile Interests: {profile.interests}")
    print(f"Education Level: {profile.education_level}")

    engine = RecommendationEngine(db)
    recommendations = engine.generate_recommendations(user.id)
    
    print(f"\nFound {len(recommendations)} recommendations:")
    for i, (opp, score) in enumerate(recommendations, 1):
        print(f"{i}. {opp.title} (Score: {score:.2f})")
        print(f"   Tags: {opp.tags}")
        print(f"   Eligibility: {opp.eligibility}")
    
    if not recommendations:
        all_opps = db.query(Opportunity).all()
        print(f"\nTotal opportunities in DB: {len(all_opps)}")
        for opp in all_opps[:20]:
            print(f"- {opp.title} | Tags: {opp.tags} | Elig: {opp.eligibility}")

if __name__ == "__main__":
    check_recommendations("thedudegowild1234@gmail.com")
