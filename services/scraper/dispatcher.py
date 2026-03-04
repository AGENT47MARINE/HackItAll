from services.scraper.universal import UniversalLocalScraper

class ScraperDispatcher:
    """Routes ALL incoming URLs to the Universal AI Scraper."""
    
    def __init__(self, ollama_model_name: str = "gemma3:4b"):
        self.ollama_model_name = ollama_model_name
        self._scraper = UniversalLocalScraper(model_name=self.ollama_model_name)
        
    def execute_scrape(self, url: str) -> dict:
        """Main entry point. Passes the URL directly to the AI crawler."""
        extracted_data = self._scraper.extract(url)
            
        if not extracted_data:
            raise ValueError(f"AI Scraper failed to extract data from {url}")
            
        if isinstance(extracted_data, dict):
            return extracted_data
        
        return extracted_data.model_dump()
