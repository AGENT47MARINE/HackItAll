from services.scraper.base import BaseScraper, BatchOpportunityExtraction
from services.scraper.playwright_engine import PlaywrightEngine
from services.nlp.extractors import LLMExtractor, LocalLLMExtractor
from services.nlp.chunker import SemanticHTMLChunker
from services.scraper.profiles import get_hints_for_url

class UniversalAIScraper(BaseScraper):
    """Tier-2 scraper: Uses Playwright to load any domain, and semantic LLMs to extract data."""
    
    def __init__(self, extractor: LLMExtractor = None, chunk_size: int = 12000):
        self.engine = PlaywrightEngine()
        self.extractor = extractor or LocalLLMExtractor()
        self.chunker = SemanticHTMLChunker(chunk_size=chunk_size)
    
    def extract(self, url: str) -> list:
        print(f"Running Universal AI Scraper on: {url}")
        
        # Get hints from refined Site Profiles
        hints = get_hints_for_url(url)
        if hints:
            print(f"Applying Site Profile hints: {hints}")
        
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
            extraction_result = self.extractor.extract(
                chunk, 
                hints=hints, 
                schema_class=BatchOpportunityExtraction
            )
            
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
