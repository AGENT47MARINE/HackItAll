from services.nlp.extractors import LocalLLMExtractor, OpenAIExtractor, AnthropicExtractor, AWSBedrockExtractor
from config import config
from urllib.parse import urlparse

class ScraperDispatcher:
    """Routes URLs to specialized spiders or the Universal AI Scraper."""
    
    def __init__(self, use_cloud: bool = False, provider: str = "local"):
        self.use_cloud = use_cloud
        
        # Determine extractor
        if provider == "bedrock":
            self.extractor = AWSBedrockExtractor()
        elif use_cloud and config.OPENAI_API_KEY:
            self.extractor = OpenAIExtractor(api_key=config.OPENAI_API_KEY)
        elif use_cloud and config.ANTHROPIC_API_KEY:
            self.extractor = AnthropicExtractor(api_key=config.ANTHROPIC_API_KEY)
        else:
            self.extractor = LocalLLMExtractor(model_name=config.DEFAULT_SCRAPER_MODEL)
            
        self._universal = UniversalAIScraper(extractor=self.extractor)
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
        # For general scraping, we return the list of items
        return self._universal.extract(url)

    def scrape_single_url(self, url: str) -> dict:
        """Forces the use of Universal AI Scraper for high-fidelity extraction of a single page."""
        print(f"[Dispatcher] Performing AI extraction on: {url}")
        extracted_items = self._universal.extract(url)
            
        if not extracted_items:
            raise ValueError(f"AI Scraper failed to extract data from {url}")
            
        # Return the first item (most relevant for a single URL)
        return extracted_items[0]
