from services.scraper.base import BaseScraper, OpportunityExtraction
from services.scraper.playwright_engine import PlaywrightEngine
from services.nlp.local_extractor import LocalLLMExtractor
from services.nlp.chunker import SemanticHTMLChunker

class UniversalAIScraper(BaseScraper):
    """Tier-2 scraper: Uses Playwright to load any domain, and local Ollama to extract data with intelligent chunking."""
    
    def __init__(self, model_name: str = "gemma3:4b", chunk_size: int = 12000, site_hints: dict = None):
        self.engine = PlaywrightEngine()
        self.extractor = LocalLLMExtractor(model_name=model_name)
        self.chunker = SemanticHTMLChunker(chunk_size=chunk_size)
        self.site_hints = site_hints or {}
        
    def extract(self, url: str) -> list:
        print(f"Running Universal AI Scraper on: {url}")
        
        # Get hints for this domain if available
        domain = url.split("//")[-1].split("/")[0]
        hints = self.site_hints.get(domain, "")
        if hints:
            print(f"Applying Site Profile hints for {domain}: {hints}")
        
        # 1. Load JS and strip DOM
        clean_text, metadata = self.engine.fetch_clean_content(url)
        
        if not clean_text:
            raise ValueError(f"Failed to fetch content from {url}")
            
        # 2. Split into semantic chunks
        chunks = self.chunker.chunk(clean_text)
        print(f"Split content into {len(chunks)} chunks for extraction.")
        
        final_items = []
        seen_links = set()
        
        # 3. Process each chunk
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            extraction_result = self.extractor.extract(chunk, hints=hints)
            
            if not extraction_result or "opportunities" not in extraction_result:
                continue
                
            for item in extraction_result["opportunities"]:
                # Basic fallback for link if missing
                if not item.get("application_link"):
                    item["application_link"] = url
                    
                # Deduplication check
                link = item.get("application_link")
                if link in seen_links:
                    continue
                seen_links.add(link)
                
                # Inherit image from page metadata if item doesn't have one
                if not item.get("image_url") and metadata.get("image"):
                    item["image_url"] = metadata["image"]
                    
                final_items.append(item)
                
        if not final_items:
            print(f"Warning: AI Scraper failed to find any unique opportunities for {url}")
            
        return final_items
