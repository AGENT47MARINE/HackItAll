"""Script to run batch scraping from Unstop and Devpost and populate the database."""
import sys
import os
import json
from datetime import datetime

# Ensure project modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.opportunity import Opportunity
from services.scraper.unstop_spider import UnstopSpider
from services.scraper.devpost_spider import DevpostSpider

def run_batch_scrape():
    """Trigger spiders and save results to DB."""
    db = SessionLocal()
    
    errors = []
    all_scraped = []
    
    print("Starting batch scrape from Unstop...")
    try:
        unstop = UnstopSpider()
        unstop_results = unstop.scrape(max_results=50)
        all_scraped.extend(unstop_results)
    except Exception as e:
        errors.append(f"Unstop spider failed: {str(e)}")
        print(f"Error: {e}")

    print("\nStarting batch scrape from Devpost...")
    try:
        devpost = DevpostSpider()
        devpost_results = devpost.scrape(max_results=10)
        all_scraped.extend(devpost_results)
    except Exception as e:
        errors.append(f"Devpost spider failed: {str(e)}")
        print(f"Error: {e}")

    # Deduplicate and insert
    new_count = 0
    skipped_count = 0

    print(f"\nProcessing {len(all_scraped)} scraped items...")
    for item in all_scraped:
        source_url = item.get("source_url", "")

        if not source_url:
            skipped_count += 1
            continue

        # Check if already exists
        existing = db.query(Opportunity).filter(
            Opportunity.source_url == source_url
        ).first()

        if existing:
            skipped_count += 1
            continue

        try:
            # Note: tags and required_skills are already JSON strings from the spiders
            opp = Opportunity(
                title=item.get("title", "Unknown"),
                description=item.get("description", "Scraped opportunity"),
                type=item.get("type", "hackathon"),
                deadline=item.get("deadline", datetime.utcnow()),
                application_link=item.get("application_link", source_url),
                image_url=item.get("image_url"),
                tags=item.get("tags", "[]"),
                required_skills=item.get("required_skills", "[]"),
                eligibility=item.get("eligibility"),
                location=item.get("location"),
                location_type=item.get("location_type", "Online"),
                source_url=source_url,
                status="active",
            )
            db.add(opp)
            new_count += 1
            print(f"Added: {opp.title}")
        except Exception as e:
            errors.append(f"Failed to insert '{item.get('title', '?')}': {str(e)}")
            print(f"Insertion Error: {e}")

    if new_count > 0:
        db.commit()
    
    print("-" * 50)
    print(f"Batch Scrape Completed.")
    print(f"New Opportunities: {new_count}")
    print(f"Skipped (Duplicates): {skipped_count}")
    print(f"Errors: {len(errors)}")
    print("-" * 50)
    
    db.close()

if __name__ == "__main__":
    run_batch_scrape()
