import json
import requests
from typing import Optional
from services.scraper.base import OpportunityExtraction

class LocalLLMExtractor:
    """Wrapper for the local Ollama instance."""
    
    def __init__(self, model_name: str = "gemma3:4b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/generate"
        
    def _build_prompt(self, text: str) -> str:
        schema = OpportunityExtraction.model_json_schema()
        
        return f"""
You are an expert Hackathon Data Extractor.
Your task is to read the raw website text and extract the hackathon details exactly matching the JSON schema below.

**CRITICAL INSTRUCTIONS**:
1. **Application Link**: Look for the most direct registration or apply URL. Common patterns include "Register Now", "Apply", "Join", or URLs containing "/register" or "/apply".
2. **Deadline**: Extract the registration deadline. Handle various formats (e.g., "Ends in 2 days", "March 15, 2025", "2025-03-15"). If multiple dates are present, use the registration deadline.
3. **Tags**: Extract up to 10 relevant technology or theme tags (e.g., "AI", "Blockchain", "Beginner Friendly").
4. **Clean JSON**: Only return valid JSON. No markdown, no prefixes, no explanations.

SCHEMA:
{json.dumps(schema, indent=2)}

WEBSITE TEXT:
{text[:4500]} 
"""

    def extract(self, text: str) -> Optional[OpportunityExtraction]:
        """Calls Ollama locally to extract JSON."""
        
        prompt = self._build_prompt(text)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json" # Forces Ollama to output valid JSON
        }
        
        try:
            print(f"Calling Local Ollama Model: {self.model_name}...")
            response = requests.post(self.base_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "{}").strip()
            
            # Pydantic validation
            parsed_data = OpportunityExtraction.model_validate_json(response_text)
            return parsed_data
            
        except Exception as e:
            print(f"LLM Extraction failed: {e}")
            if 'response_text' in locals():
                 print(f"Raw Output: {response_text}")
            return None
