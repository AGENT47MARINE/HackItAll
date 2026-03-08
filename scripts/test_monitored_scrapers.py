import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scraper.dispatcher import ScraperDispatcher
from services.scraper.monitoring import ScraperEvaluation
from database import SessionLocal
from models.opportunity import Opportunity

def run_targeted_test():
    print(f"--- Targeted Scraper Test Started at {datetime.now()} ---")
    dispatcher = ScraperDispatcher()
    db = SessionLocal()
    
    # Test Unstop and Devpost
    platforms = [
        {"name": "Unstop", "url": "https://unstop.com/hackathons"},
        {"name": "Devpost", "url": "https://devpost.com/hackathons"}
    ]
    
    for platform in platforms:
        p_name = platform["name"]
        print(f"\nTesting {p_name}...")
        try:
            items = dispatcher.execute_scrape(platform["url"])
            print(f"  > Scraped {len(items)} items from {p_name}")
            
            # Check if any have registration counts
            with_regs = [i for i in items if i.get("source_registration_count", 0) > 0]
            print(f"  > Items with Reg Counts: {len(with_regs)}")
            
            ScraperEvaluation.record_run(p_name, len(items), success=True)
        except Exception as e:
            print(f"  ! Error: {e}")
            ScraperEvaluation.record_run(p_name, 0, success=False, error=str(e))
            
    db.close()
    ScraperEvaluation.get_summary()

if __name__ == "__main__":
    run_targeted_test()
