"""15-Site Mega Scraper Orchestrator.
Uses the Universal AI Scraper to fetch data from top platforms.
"""
import sys
import os
import json
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scraper.dispatcher import ScraperDispatcher
from services.scraper.monitoring import ScraperEvaluation
from database import SessionLocal
from models.opportunity import Opportunity

# Target Platforms for Indian Students
TARGET_PLATFORMS = [
    {"name": "Devfolio", "url": "https://devfolio.co/hackathons"},
    {"name": "HackerEarth", "url": "https://www.hackerearth.com/challenges/"},
    {"name": "Unstop", "url": "https://unstop.com/hackathons"},
    {"name": "TechGig", "url": "https://www.techgig.com/hackathon"},
    {"name": "GeeksForGeeks", "url": "https://www.geeksforgeeks.org/events"},
    {"name": "SIH (Smart India Hackathon)", "url": "https://sih.gov.in/"},
    {"name": "Devpost", "url": "https://devpost.com/hackathons"},
    {"name": "MLH (Major League Hacking)", "url": "https://mlh.io/seasons/2024/events"},
    {"name": "CodeChef", "url": "https://www.codechef.com/contests"},
    {"name": "LeetCode", "url": "https://leetcode.com/contest/"},
    {"name": "Kaggle", "url": "https://www.kaggle.com/competitions"},
    {"name": "Internshala", "url": "https://internshala.com/hackathons"},
    {"name": "Microsoft Imagine Cup", "url": "https://imaginecup.microsoft.com/"},
    {"name": "Buddy4Study", "url": "https://www.buddy4study.com/scholarships"},
    {"name": "Reliance Foundation", "url": "https://www.reliancefoundation.org/scholarships"}
]

def run_mega_scrape():
    print(f"--- Mega Scrape Started at {datetime.now()} ---")
    dispatcher = ScraperDispatcher(ollama_model_name="gemma3:4b")
    db = SessionLocal()
    
    stats = {"total_processed": 0, "added": 0, "skipped": 0, "errors": 0}
    
    for platform in TARGET_PLATFORMS:
        p_name = platform["name"]
        print(f"\n[MEGA] Scraping {p_name}...")
        try:
            # The dispatcher uses the Universal AI Scraper + Playwright
            # This returns a list of opportunities or a single one depending on the page
            scraped_data = dispatcher.execute_scrape(platform["url"])
            
            # The Universal Scraper might return a single item or a list wrapped in a dict
            items = []
            if isinstance(scraped_data, list):
                items = scraped_data
            elif isinstance(scraped_data, dict):
                # Check for nested list if extractor returned multiple
                items = scraped_data.get("opportunities", [scraped_data])
            
            added_this_run = 0
            for item in items:
                stats["total_processed"] += 1
                
                # Basic validation
                source_url = item.get("source_url") or item.get("application_link")
                if not source_url or not item.get("title"):
                    continue
                
                # Check for duplicates
                existing = db.query(Opportunity).filter(Opportunity.source_url == source_url).first()
                if existing:
                    # UPDATED: Still update registration counts for duplicates
                    if "source_registration_count" in item:
                        existing.source_registration_count = item["source_registration_count"]
                        db.add(existing)
                    stats["skipped"] += 1
                    continue
                
                # Create new opportunity
                # Handle potential list values for tags/skills if LLM returned them as lists
                tags = item.get("tags", ["Hackathon"])
                if isinstance(tags, list):
                    tags = json.dumps(tags[:5])
                
                skills = item.get("required_skills", [])
                if isinstance(skills, list):
                    skills = json.dumps(skills[:5])
                
                # Handle deadline
                deadline = item.get("deadline")
                if not deadline or not isinstance(deadline, datetime):
                    deadline = datetime.utcnow() + timedelta(days=30)
                
                new_opp = Opportunity(
                    title=item["title"],
                    description=item.get("description", f"Hackathon on {p_name}"),
                    type=item.get("type", "hackathon"),
                    deadline=deadline,
                    application_link=item["application_link"],
                    image_url=item.get("image_url"),
                    tags=tags,
                    required_skills=skills,
                    eligibility=item.get("eligibility", "Open to all"),
                    location=item.get("location", "India"),
                    location_type=item.get("location_type", "Online"),
                    source_url=source_url,
                    status="active",
                    source_registration_count=item.get("source_registration_count", 0)
                )
                
                db.add(new_opp)
                stats["added"] += 1
                added_this_run += 1
                print(f"  + Added: {item['title'][:50]}...")
            
            db.commit()
            
            # Record health monitoring
            ScraperEvaluation.record_run(p_name, added_this_run, success=True)
            
        except Exception as e:
            print(f"  ! Error scraping {p_name}: {e}")
            stats["errors"] += 1
            db.rollback()
            ScraperEvaluation.record_run(p_name, 0, success=False, error=str(e))
        
        # Polite delay to avoid rate limiting
        time.sleep(2)

    db.close()
    print("\n" + "="*50)
    print("Mega Scrape Completed Successfully!")
    print(f"Total Processed: {stats['total_processed']}")
    print(f"New Opportunities Added: {stats['added']}")
    print(f"Duplicates Skipped: {stats['skipped']}")
    print(f"Errors Encountered: {stats['errors']}")
    print("="*50)

if __name__ == "__main__":
    run_mega_scrape()
