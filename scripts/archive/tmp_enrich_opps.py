"""Script to enrich opportunity tags/skills to match agent47's profile."""
from database import SessionLocal
from models.opportunity import Opportunity
from datetime import datetime
import json

db = SessionLocal()

# agent47 has: React, Python, Node.js, AI, Machine Learning, Blockchain
# Interests: Artificial Intelligence, Blockchain

updates = [
    # (partial_title, new_tags, new_required_skills)
    ("Big Code", 
     ["Hackathon", "Artificial Intelligence", "Web Development", "Node.js", "React"],
     ["React", "Node.js", "AI"]),
    ("Zerve.AI", 
     ["AI", "Machine Learning", "Blockchain", "Artificial Intelligence"],
     ["Python", "AI", "Machine Learning"]),
    ("Smart India", 
     ["Hackathon", "AI", "Python", "Artificial Intelligence", "Machine Learning"],
     ["Python", "AI"]),
    ("HackFest", 
     ["Hackathon", "React", "Node.js", "Web Development"],
     ["React", "Node.js"]),
]

updated = 0
for partial_title, tags, skills in updates:
    opp = db.query(Opportunity).filter(
        Opportunity.title.ilike(f'%{partial_title}%'),
        Opportunity.status == 'active'
    ).first()
    if opp:
        opp.tags = json.dumps(tags)
        opp.required_skills = json.dumps(skills)
        print(f"Updated: {opp.title}")
        updated += 1

# Also update any hackathon with eligibility "open to all" or "undergraduate" 
# to have some AI/tech tags
remaining_opps = db.query(Opportunity).filter(
    Opportunity.status == 'active',
    Opportunity.deadline > datetime.utcnow()
).all()

count = 0
for opp in remaining_opps:
    current_tags = json.loads(opp.tags) if opp.tags else []
    current_skills = json.loads(opp.required_skills) if opp.required_skills else []
    
    # If this opportunity is in engineering/tech domain but lacks proper tags
    title_lower = opp.title.lower()
    desc_lower = (opp.description or "").lower()
    
    if count < 5 and not any(t.lower() in ['ai', 'machine learning', 'react', 'python', 'node.js', 'blockchain', 'artificial intelligence'] for t in current_tags):
        if any(k in title_lower or k in desc_lower for k in ['hack', 'code', 'tech', 'innovat', 'develop', 'engineer']):
            new_tags = current_tags + ["AI", "Python", "Hackathon"]
            opp.tags = json.dumps(new_tags)
            print(f"Enriched tags for: {opp.title}")
            count += 1

db.commit()
print(f"\nDone. Updated {updated} targeted + {count} enriched opportunities.")
