import sys
import os
import time
import json

# Ensure services can be imported run running scripts/test_scraper_bulk.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scraper.dispatcher import ScraperDispatcher

TEST_URLS = [
    "https://devpost.com/hackathons",        # Global Aggregator
    "https://devfolio.co/hackathons",      # Global Aggregator
    "https://unstop.com/hackathons",       # India Aggregator
    "https://mlh.io/seasons/2024/events",  # Global Student League
    "https://hackmit.org/",                # React Custom Site
    "https://vithack.in/",                 # Next.js Custom Site
    "https://www.treehacks.com/",          # Next.js Custom Site
    "https://hackthenorth.com/",           # React Custom Site
    "https://pennapps.com/",               # Standard Custom Site
    "https://taikai.network/hackathons"    # Web3 Aggregator
]

def main():
    print("=" * 50)
    print("Starting Universal Scraper Evaluation...")
    print(f"Targeting 10 Diverse Domains using local Gemma 3:4b")
    print("=" * 50)
    
    # Initialize the Scraper
    dispatcher = ScraperDispatcher() 
    results = []

    for url in TEST_URLS:
        print(f"\nEvaluating: {url}")
        start_time = time.time()
        try:
            # We are testing the exact identical code path the API Endpoint uses
            data = dispatcher.execute_scrape(url)
            duration = time.time() - start_time
            print(f"[SUCCESS] Parsed in {duration:.2f}s")
            print(f"  -> Title: {data.get('title', 'N/A')}")
            print(f"  -> Deadline: {data.get('deadline', 'N/A')}")
            
            results.append({
                "url": url,
                "status": "success",
                "duration_seconds": round(duration, 2),
                "data": {
                    "title": data.get("title", ""),
                    "deadline": data.get("deadline", "")
                }
            })
        except Exception as e:
            duration = time.time() - start_time
            print(f"[FAILED] Error after {duration:.2f}s: {e}")
            results.append({
                "url": url,
                "status": "failed",
                "duration_seconds": round(duration, 2),
                "error": str(e)
            })
            
    # Write summary
    print("\n" + "=" * 50)
    print("FINAL SUMMARY")
    successes = len([r for r in results if r["status"] == "success"])
    print(f"Overall Success Rate: {successes} / {len(TEST_URLS)}")
    print("=" * 50)
    
    with open("scraper_evaluation.json", "w") as f:
        json.dump(results, f, indent=4)
        print("Detailed JSON saved to scraper_evaluation.json")

if __name__ == "__main__":
    main()
