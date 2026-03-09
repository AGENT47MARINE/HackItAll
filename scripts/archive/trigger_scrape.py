from sqlalchemy.orm import Session
from database import SessionLocal
from services.scraper.unstop_spider import UnstopSpider
from services.scraper.devpost_spider import DevpostSpider
from services.scraper.hacker_earth_spider import HackerEarthSpider
from models.opportunity import Opportunity
from datetime import datetime
import json

db = SessionLocal()
try:
    errors = []
    all_scraped = []
    sources_used = []

    print("Starting Unstop scrape...")
    try:
        unstop = UnstopSpider()
        unstop_results = unstop.scrape(max_results=50)
        all_scraped.extend(unstop_results)
        if unstop_results:
            sources_used.append("unstop.com")
    except Exception as e:
        errors.append(f"Unstop spider failed: {str(e)}")

    print("Starting Devpost scrape...")
    try:
        devpost = DevpostSpider()
        devpost_results = devpost.scrape(max_results=15)
        all_scraped.extend(devpost_results)
        if devpost_results:
            sources_used.append("devpost.com")
    except Exception as e:
        errors.append(f"Devpost spider failed: {str(e)}")

    print("Starting HackerEarth scrape...")
    try:
        hackerearth = HackerEarthSpider()
        he_results = hackerearth.scrape(max_results=15)
        all_scraped.extend(he_results)
        if he_results:
            sources_used.append("hackerearth.com")
    except Exception as e:
        errors.append(f"HackerEarth spider failed: {str(e)}")

    print(f"Scraped {len(all_scraped)} total opportunities.")

    # Deduplicate and insert
    new_count = 0
    skipped_count = 0

    scraped_urls = [item.get("source_url") for item in all_scraped if item.get("source_url")]
    existing_urls = set()
    if scraped_urls:
        existing_urls = {
            url for (url,) in db.query(Opportunity.source_url).filter(
                Opportunity.source_url.in_(scraped_urls)
            ).all()
        }

    for item in all_scraped:
        source_url = item.get("source_url", "")

        if not source_url or source_url in existing_urls:
            skipped_count += 1
            continue

        try:
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
                status="active"
            )
            db.add(opp)
            new_count += 1
        except Exception as e:
            errors.append(f"Failed to insert {source_url}: {e}")

    db.commit()
    print(f"Batch Scrape Done. New: {new_count}, Skipped: {skipped_count}, Errors: {len(errors)}")
    if errors:
        print("Errors encountered:")
        for err in errors:
            print(f"- {err}")

finally:
    db.close()
