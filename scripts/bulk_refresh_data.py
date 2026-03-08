import sys
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from services.scraper.dispatcher import ScraperDispatcher
from services.opportunity_service import OpportunityService

def refresh_data():
    db = SessionLocal()
    dispatcher = ScraperDispatcher()
    service = OpportunityService(db)
    
    urls_to_scrape = [
        "https://unstop.com/hackathons",
        "https://unstop.com/internships",
        "https://unstop.com/scholarships",
        "https://devpost.com/hackathons"
    ]
    
    total_new = 0
    print("🚜 Starting bulk data refresh...")
    
    for url in urls_to_scrape:
        try:
            print(f"🔍 Scraping {url}...")
            items = dispatcher.execute_scrape(url)
            
            if not items:
                print(f"⚠️ No items found for {url}")
                continue
                
            print(f"✅ Found {len(items)} items. Saving to DB...")
            
            for item in items:
                if not isinstance(item, dict):
                    print(f"⚠️ Warning: Scraper returned non-dict item: {type(item)}: {item}")
                    continue

                try:
                    # Parse deadline
                    deadline_dt = None
                    if item.get("deadline"):
                        try:
                            if isinstance(item["deadline"], datetime):
                                deadline_dt = item["deadline"]
                            else:
                                deadline_dt = datetime.fromisoformat(str(item["deadline"]).replace("Z", "+00:00"))
                        except Exception:
                            deadline_dt = None
                            
                    if not deadline_dt:
                        deadline_dt = datetime(2025, 12, 31)
                    
                    # Handle tags and skills that might be JSON strings
                    tags = item.get("tags", [])
                    if isinstance(tags, str):
                        try:
                            tags = json.loads(tags)
                        except:
                            tags = [tags] if tags else []
                            
                    skills = item.get("required_skills", [])
                    if isinstance(skills, str):
                        try:
                            skills = json.loads(skills)
                        except:
                            skills = [skills] if skills else []

                    service.create_opportunity(
                        title=item.get("title", "Unknown Opportunity"),
                        description=item.get("description", "No description provided"),
                        opportunity_type=item.get("type", "hackathon"),
                        deadline=deadline_dt,
                        application_link=item.get("application_link", ""),
                        tags=tags,
                        required_skills=skills,
                        eligibility=item.get("eligibility", "Open to all"),
                        timeline=item.get("timeline", []),
                        prizes=item.get("prizes", [])
                    )
                    total_new += 1
                except Exception as e:
                    print(f"❌ Error saving item '{item.get('title')}': {e}")
                    
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            
    print(f"\n✨ COMPLETED! Refreshed {total_new} new opportunities with enhanced details.")
    db.close()

if __name__ == "__main__":
    refresh_data()
