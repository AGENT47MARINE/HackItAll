from services.scraper.base import BaseScraper, OpportunityExtraction
from services.scraper.playwright_engine import PlaywrightEngine
from services.nlp.local_extractor import LocalLLMExtractor

class UniversalLocalScraper(BaseScraper):
    """Tier-2 scraper: Uses Playwright to load any domain, and local Ollama to extract data."""
    
    def __init__(self, model_name: str = "gemma3:4b"):
        self.engine = PlaywrightEngine()
        self.extractor = LocalLLMExtractor(model_name=model_name)
        
    def extract(self, url: str) -> OpportunityExtraction:
        print(f"Running Universal Scraper on: {url}")
        
        # 1. Load JS and strip DOM
        clean_text, metadata = self.engine.fetch_clean_content(url)
        
        if not clean_text:
            raise ValueError(f"Failed to fetch content from {url}")
            
        # 2. Extract structured JSON using Ollama
        extracted_data = self.extractor.extract(clean_text)
        
        if not extracted_data:
            raise ValueError(f"LLM failed to extract JSON from {url}")
            
        # 3. Fast-Patch with OpenGraph metadata
        if metadata.get("title") and ("Untitled" in extracted_data.title or len(extracted_data.title) < 3):
             extracted_data.title = metadata["title"]
             
        if not extracted_data.description and metadata.get("description"):
             extracted_data.description = metadata["description"]
             
        # Add the raw URL and Image to the final output (not handled by the strict LLM schema)
        return {
            **extracted_data.model_dump(),
            "image_url": metadata.get("image", ""),
            "application_link": extracted_data.application_link or url
        }
