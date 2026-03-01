"""Seed script to reset and populate the database with diverse test data."""
import json
from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
from models.opportunity import Opportunity


def reset_and_seed():
    """Drop tables, recreate, and seed with rich test data."""
    # Drop and recreate tables to ensure new schema columns exist
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    opportunities = [
        {
            "title": "MLH Global Hack 2025",
            "description": "Build innovative solutions with hackers worldwide. Huge prizes for Web and AI.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=10),
            "application_link": "https://mlh.io/seasons/2025/events",
            "image_url": "https://static.mlh.io/brand-assets/logo/official/mlh-logo-color.png",
            "tags": json.dumps(["AI", "Web Dev", "Machine Learning"]),
            "required_skills": json.dumps(["Python", "React"]),
            "eligibility": "B.Tech",
            "location_type": "Online",
            "location": "Global",
            "source_url": "https://mlh.io/seasons/2025/events/global-hack",
            "status": "active",
        },
        {
            "title": "Local High School Hack",
            "description": "In-person event specifically for high schoolers.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=40),
            "application_link": "https://example.com/hs-hack",
            "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400",
            "tags": json.dumps(["Web Dev", "Beginner"]),
            "required_skills": json.dumps(["HTML"]),
            "eligibility": "High School",
            "location_type": "In-Person",
            "location": "New York",
            "source_url": "https://example.com/hs-hack",
            "status": "active",
        },
        {
            "title": "Devpost AI Challenge",
            "description": "Build the next frontier of Agentic AI.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=30),
            "application_link": "https://devpost.com/hackathons/ai-challenge",
            "image_url": "https://devpost-challengepost.netdna-ssl.com/assets/defaults/thumbnail-default.png",
            "tags": json.dumps(["AI/ML", "Agentic AI", "Data Science"]),
            "required_skills": json.dumps(["Python", "LLMs"]),
            "eligibility": "All students",
            "location_type": "Hybrid",
            "location": "San Francisco / Online",
            "source_url": "https://devpost.com/hackathons/ai-challenge",
            "status": "active",
        },
        {
            "title": "Graduate Research Symposium",
            "description": "Showcase your Master's or PhD research.",
            "type": "skill_program",
            "deadline": datetime.utcnow() + timedelta(days=20),
            "application_link": "https://symposium.edu/apply",
            "image_url": "https://images.unsplash.com/photo-1532619675605-1ede6c2ed2b0?w=400",
            "tags": json.dumps(["Research", "Data Science"]),
            "required_skills": json.dumps(["Data Analysis"]),
            "eligibility": "Graduate",
            "location_type": "Online",
            "location": "Virtual",
            "source_url": "https://symposium.edu/apply",
            "status": "active",
        },
        {
            "title": "Unstop Code Clash 2025",
            "description": "India's largest competitive coding hackathon. Open for all B.Tech students.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=7),
            "application_link": "https://unstop.com/hackathons/code-clash-2025",
            "image_url": "https://d8it4huxumps7.cloudfront.net/uploads/images/150x150/uploadedManual-64efaborcecd.png",
            "tags": json.dumps(["Competitive Coding", "DSA", "App Dev"]),
            "required_skills": json.dumps(["C++", "Python"]),
            "eligibility": "B.Tech",
            "location_type": "Online",
            "location": "India",
            "source_url": "https://unstop.com/hackathons/code-clash-2025",
            "status": "active",
        },
        {
            "title": "Women in Tech Hackathon",
            "description": "Empowering women through technology. Build projects that make a difference.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=25),
            "application_link": "https://example.com/wit-hackathon",
            "image_url": "https://images.unsplash.com/photo-1573164713988-8665fc963095?w=400",
            "tags": json.dumps(["Web Dev", "IoT", "Social Impact"]),
            "required_skills": json.dumps(["JavaScript", "React"]),
            "eligibility": "All students",
            "location_type": "Hybrid",
            "location": "Bangalore / Online",
            "source_url": "https://example.com/wit-hackathon",
            "status": "active",
        },
        {
            "title": "Blockchain Builders Summit",
            "description": "48-hour sprint to build the next decentralized killer app.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=15),
            "application_link": "https://example.com/blockchain-summit",
            "image_url": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400",
            "tags": json.dumps(["Blockchain", "Web3", "DeFi"]),
            "required_skills": json.dumps(["Solidity", "JavaScript"]),
            "eligibility": "All students",
            "location_type": "Online",
            "location": "Global",
            "source_url": "https://example.com/blockchain-summit",
            "status": "active",
        },
        {
            "title": "Expired Old Hackathon",
            "description": "This hackathon has already passed for testing expired-event exclusion.",
            "type": "hackathon",
            "deadline": datetime.utcnow() - timedelta(days=5),
            "application_link": "https://example.com/old-hack",
            "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400",
            "tags": json.dumps(["AI"]),
            "required_skills": json.dumps([]),
            "eligibility": "All students",
            "location_type": "In-Person",
            "location": "Delhi",
            "source_url": "https://example.com/old-hack",
            "status": "active",
        },
    ]

    for opp_data in opportunities:
        opp = Opportunity(**opp_data)
        db.add(opp)

    db.commit()
    print(f"Successfully seeded {len(opportunities)} opportunities!")
    db.close()


if __name__ == "__main__":
    reset_and_seed()