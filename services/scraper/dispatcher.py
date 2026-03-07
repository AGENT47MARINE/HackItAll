from services.scraper.universal import UniversalAIScraper
from services.scraper.devpost_spider import DevpostSpider
from services.scraper.unstop_spider import UnstopSpider
from urllib.parse import urlparse

class ScraperDispatcher:
    """Routes URLs to specialized spiders or the Universal AI Scraper."""
    
    def __init__(self, ollama_model_name: str = "gemma3:4b"):
        self.ollama_model_name = ollama_model_name
        self._universal = UniversalAIScraper(model_name=self.ollama_model_name)
        self._devpost = DevpostSpider()
        self._unstop = UnstopSpider()
        
    def execute_scrape(self, url: str) -> list:
        """Main entry point. Routes to specialized spiders or fallback to AI crawler."""
        domain = urlparse(url).netloc.lower()
        path = urlparse(url).path.lower()
        
        # Detect category hint (e.g. hackathons, internships, scholarships)
        category_hint = "hackathons"
        for cat in ["internships", "scholarships", "workshops", "events", "jobs"]:
            if cat in path:
                category_hint = cat
                break

        if "devpost.com" in domain:
            print(f"[Dispatcher] Routing {url} to specialized DevpostSpider...")
            return self._devpost.scrape(max_results=20)
            
        if "unstop.com" in domain:
            print(f"[Dispatcher] Routing {url} to specialized UnstopSpider (Category: {category_hint})...")
            return self._unstop.scrape(max_results=20, opportunity_type=category_hint)
            
        # Fallback to Universal AI Scraper for unknown domains
        return self.scrape_single_url(url)

    def scrape_single_url(self, url: str) -> dict:
        """Forces the use of Universal AI Scraper for high-fidelity extraction of a single page."""
        print(f"[Dispatcher] Performing high-fidelity AI scrape on: {url}")
        extracted_items = self._universal.extract(url)
            
        if not extracted_items:
            raise ValueError(f"AI Scraper failed to extract data from {url}")
            
        # Return the first item (most relevant for a single URL)
        return extracted_items[0]
