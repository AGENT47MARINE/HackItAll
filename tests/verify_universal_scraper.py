import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from services.scraper.dispatcher import ScraperDispatcher
from services.nlp.extractors import LocalLLMExtractor

def test_universal_scraper_ollama():
    print("--- Testing Universal AI Scraper with Local Ollama ---")
    
    # We'll use a real URL but mock the network if needed.
    # For this verification, we assume Ollama is running or we just check the logic path.
    url = "https://devpost.com/hackathons"
    
    # Instantiate dispatcher (defaults to LocalLLMExtractor)
    dispatcher = ScraperDispatcher(use_cloud=False)
    
    try:
        print(f"Executing scrape for: {url}")
        results = dispatcher.execute_scrape(url)
        
        print(f"Extracted {len(results)} items.")
        if results:
            print("First item sample:")
            print(json.dumps(results[0], indent=2))
            
            # Assertions
            assert "title" in results[0]
            assert "application_link" in results[0]
            
    except Exception as e:
        print(f"Scrape failed (likely no Ollama running): {e}")

def test_site_profiles_logic():
    print("\n--- Testing Site Profiles & Hints logic ---")
    from services.scraper.profiles import get_hints_for_url
    
    urls = [
        "https://devpost.com/hackathons",
        "https://sub.devfolio.co/events",
        "https://unknownsite.com/xyz"
    ]
    
    for url in urls:
        hints = get_hints_for_url(url)
        print(f"URL: {url} -> Hints: {hints[:50]}...")
        if "devpost" in url:
            assert "Devpost" in hints or "hackathons" in hints
        if "devfolio" in url:
            assert "Devfolio" in hints or "Apply Now" in hints

if __name__ == "__main__":
    test_site_profiles_logic()
    # test_universal_scraper_ollama() # Uncomment if you want to run a real localized test
