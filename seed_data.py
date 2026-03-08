"""Seed script to reset and populate the database with diverse test data."""
import json
from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
from models.opportunity import Opportunity


def reset_and_seed():
    """Drop tables, recreate, and seed with rich test data."""
    # Use raw SQL for CASCADE drop if on postgres
    if "postgresql" in str(engine.url):
        from sqlalchemy import text
        with engine.connect() as conn:
            # Drop all tables in public schema with cascade
            conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO hackitall; GRANT ALL ON SCHEMA public TO public;"))
            conn.commit()
    else:
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
            "eligibility": "All Students",
            "location_type": "Online",
            "location": "Global",
            "source_url": "https://mlh.io/seasons/2025/events/global-hack",
            "status": "active",
        },
        {
            "title": "Smart India Hackathon 2025",
            "description": "World's biggest open innovation model. Solve problem statements from various ministries.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=45),
            "application_link": "https://sih.gov.in/",
            "image_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800&q=80",
            "tags": json.dumps(["Governance", "Hardware", "Software"]),
            "required_skills": json.dumps(["Innovation", "Tech Stack Agnostic"]),
            "eligibility": "College Students",
            "location_type": "In-Person",
            "location": "Nodal Centers, India",
            "source_url": "https://sih.gov.in/",
            "status": "active",
        },
        {
            "title": "Google Summer of Code (GSoC)",
            "description": "Global program focused on bringing student developers into open source software development.",
            "type": "internship",
            "deadline": datetime.utcnow() + timedelta(days=60),
            "application_link": "https://summerofcode.withgoogle.com/",
            "image_url": "https://images.unsplash.com/photo-1614741118887-7a4ee193a5fa?w=800&q=80",
            "tags": json.dumps(["Open Source", "Professional Dev"]),
            "required_skills": json.dumps(["Git", "Language Specific"]),
            "eligibility": "18+ Students",
            "location_type": "Online",
            "location": "Global",
            "source_url": "https://summerofcode.withgoogle.com/",
            "status": "active",
        },
        {
            "title": "Reliance Foundation Scholarships",
            "description": "Scholarships for undergraduate and postgraduate students in India pursuing tech education.",
            "type": "scholarship",
            "deadline": datetime.utcnow() + timedelta(days=30),
            "application_link": "https://www.scholarships.reliancefoundation.org/",
            "image_url": "https://images.unsplash.com/photo-1523050853063-bd331574043b?w=800&q=80",
            "tags": json.dumps(["Financial Aid", "Merit-based"]),
            "required_skills": json.dumps(["Academic Excellence"]),
            "eligibility": "Undergrad/Postgrad",
            "location_type": "Online",
            "location": "India",
            "source_url": "https://www.scholarships.reliancefoundation.org/",
            "status": "active",
        },
        {
            "title": "Unstop Code Clash 2025",
            "description": "India's largest competitive coding hackathon. Open for all B.Tech students.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=7),
            "application_link": "https://unstop.com/hackathons/code-clash-2025",
            "image_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80",
            "tags": json.dumps(["Competitive Coding", "DSA", "App Dev"]),
            "required_skills": json.dumps(["C++", "Python"]),
            "eligibility": "Eng. Students",
            "location_type": "Online",
            "location": "India",
            "source_url": "https://unstop.com/hackathons/code-clash-2025",
            "status": "active",
        },
        {
            "title": "TCS CodeVita Season 12",
            "description": "The world's largest coding contest. Win rewards and internship opportunities at TCS.",
            "type": "hackathon",
            "deadline": datetime.utcnow() + timedelta(days=20),
            "application_link": "https://www.tcscodevita.com/",
            "image_url": "https://images.unsplash.com/photo-1516259762381-22954d7d3ad2?w=800&q=80",
            "tags": json.dumps(["Competitive Coding", "Hiring"]),
            "required_skills": json.dumps(["Algorithms", "DSA"]),
            "eligibility": "Pre-Final/Final Year",
            "location_type": "Online",
            "location": "Global / India",
            "source_url": "https://www.tcscodevita.com/",
            "status": "active",
        },
    ]

    for opp_data in opportunities:
        opp = Opportunity(**opp_data)
        db.add(opp)

    db.commit()
    print(f"Successfully seeded {len(opportunities)} diverse Indian & Global opportunities!")
    db.close()


if __name__ == "__main__":
    reset_and_seed()