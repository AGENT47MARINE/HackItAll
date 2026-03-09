from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.user import User, Profile
from models.opportunity import Opportunity
from datetime import datetime, timedelta
import json
import uuid

def seed_final_verification():
    db = SessionLocal()
    try:
        print("Seeding final verification data...")
        
        # 1. Add 'Hack to Skill' opportunities manually since we don't have a spider for it
        h2s_opps = [
            {
                "title": "HackToSkill GenAI Challenge",
                "description": "Build innovative Generative AI solutions using LLMs. Open for all students and developers.",
                "type": "hackathon",
                "deadline": datetime.utcnow() + timedelta(days=20),
                "application_link": "https://hacktoskill.com/hackathons/genai-challenge",
                "image_url": "https://hacktoskill.com/assets/img/logo.png",
                "tags": json.dumps(["GenAI", "AI/ML", "Innovation"]),
                "required_skills": json.dumps(["Python", "OpenAI", "LangChain"]),
                "eligibility": "All Students",
                "location_type": "Online",
                "location": "Global",
                "source_url": "https://hacktoskill.com/hackathons/genai-challenge",
                "status": "active",
            },
            {
                "title": "HackToSkill Web3 Buidlathon",
                "description": "Building the future of decentralized web. Focus on DeFi, NFTs, and DAO infrastructure.",
                "type": "hackathon",
                "deadline": datetime.utcnow() + timedelta(days=15),
                "application_link": "https://hacktoskill.com/hackathons/web3-buidl",
                "image_url": "https://hacktoskill.com/assets/img/web3.png",
                "tags": json.dumps(["Web3", "Blockchain", "Solidity"]),
                "required_skills": json.dumps(["Solidity", "Rust", "Ethereum"]),
                "eligibility": "Developers",
                "location_type": "In-Person",
                "location": "Bangalore, India",
                "source_url": "https://hacktoskill.com/hackathons/web3-buidl",
                "status": "active",
            }
        ]
        
        for opp_data in h2s_opps:
            # Check if exists
            exists = db.query(Opportunity).filter(Opportunity.source_url == opp_data["source_url"]).first()
            if not exists:
                opp = Opportunity(**opp_data)
                db.add(opp)
        
        # 2. Add a test user with specific domains (Cybersecurity, AI, Web Development)
        user_id = "user_test_verify_domains"
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id,
                username="domain_tester",
                email="tester@hackitall.ai",
            )
            db.add(user)
            db.flush() # Get user into session
            
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            profile = Profile(
                user_id=user_id,
                interests=json.dumps(["Cybersecurity", "Artificial Intelligence", "Blockchain"]),
                skills=json.dumps(["Python", "Solidity", "Ethical Hacking"]),
                education_level="Undergraduate",
            )
            db.add(profile)
        else:
            profile.interests = json.dumps(["Cybersecurity", "Artificial Intelligence", "Blockchain"])
            profile.skills = json.dumps(["Python", "Solidity", "Ethical Hacking"])
        
        db.commit()
        print("Successfully seeded Hack to Skill opportunities and test profile with specific domains.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding verification data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_final_verification()
