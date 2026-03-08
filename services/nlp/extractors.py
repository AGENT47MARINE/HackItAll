import json
import requests
from typing import Optional, Any, Dict, List
from abc import ABC, abstractmethod

class LLMExtractor(ABC):
    """Base interface for all LLM-based extractors."""
    
    @abstractmethod
    def extract(self, text: str, hints: str = "", schema_class: Optional[Any] = None) -> Optional[dict]:
        """High-level extraction from raw text using schema."""
        pass

    @abstractmethod
    def generic_extract(self, prompt: str, schema_class: Optional[Any] = None) -> Optional[dict]:
        """Low-level extraction using a raw prompt."""
        pass

    def _build_prompt(self, text: str, hints: str = "", schema_class: Optional[Any] = None) -> str:
        schema_json = ""
        if schema_class:
            schema_json = json.dumps(schema_class.model_json_schema(), indent=2)
            
        hints_section = f"\n**SITE-SPECIFIC HINTS**:\n{hints}\n" if hints else ""
        
        return f"""
You are an expert Hackathon Data Extractor.
Your task is to scan the raw website text and extract ALL hackathons or opportunities listed.
Return them as a list matching the JSON schema below.
{hints_section}
**CRITICAL INSTRUCTIONS**:
1. **Application Link**: For each item, find the direct link to THAT specific event. 
2. **Batch Extraction**: Many websites list 10-20 events. Extract as many as you see clearly.
3. **Clean JSON**: Only return valid JSON. Do not include titles, notes, or markdown blocks.

SCHEMA:
{schema_json}

WEBSITE TEXT:
{text}
"""

class LocalLLMExtractor(LLMExtractor):
    """Local extraction using Ollama."""
    
    def __init__(self, model_name: str = "gemma3:4b", base_url: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.api_url = f"{base_url}/api/generate"
        
    def extract(self, text: str, hints: str = "", schema_class: Optional[Any] = None) -> Optional[dict]:
        prompt = self._build_prompt(text, hints, schema_class)
        return self.generic_extract(prompt, schema_class)

    def generic_extract(self, prompt: str, schema_class: Optional[Any] = None) -> Optional[dict]:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=90)
            response.raise_for_status()
            result = response.json()
            response_text = result.get("response", "{}").strip()
            
            if schema_class:
                return schema_class.model_validate_json(response_text).model_dump()
            return json.loads(response_text)
        except Exception as e:
            print(f"Local LLM Extraction failed: {e}")
            return None

class OpenAIExtractor(LLMExtractor):
    """Cloud extraction using OpenAI (GPT-4o)."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
    def extract(self, text: str, hints: str = "", schema_class: Optional[Any] = None) -> Optional[dict]:
        prompt = self._build_prompt(text, hints, schema_class)
        return self.generic_extract(prompt, schema_class)

    def generic_extract(self, prompt: str, schema_class: Optional[Any] = None) -> Optional[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            
            if schema_class:
                return schema_class.model_validate_json(response_text).model_dump()
            return json.loads(response_text)
        except Exception as e:
            print(f"OpenAI Extraction failed: {e}")
            return None

class AnthropicExtractor(LLMExtractor):
    """Cloud extraction using Anthropic (Claude 3.5 Sonnet)."""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20240620"):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.anthropic.com/v1/messages"
        
    def extract(self, text: str, hints: str = "", schema_class: Optional[Any] = None) -> Optional[dict]:
        prompt = self._build_prompt(text, hints, schema_class)
        return self.generic_extract(prompt, schema_class)

    def generic_extract(self, prompt: str, schema_class: Optional[Any] = None) -> Optional[dict]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt + "\nRemember: RETURN ONLY VALID JSON."}]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            response_text = result["content"][0]["text"]
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            if schema_class:
                return schema_class.model_validate_json(response_text).model_dump()
            return json.loads(response_text)
            return json.loads(response_text)
        except Exception as e:
            print(f"Anthropic Extraction failed: {e}")
            return None

class AWSBedrockExtractor(LLMExtractor):
    """Cloud extraction using AWS Bedrock (Claude 3.5 Sonnet or Nova)."""
    
    def __init__(self, region_name: str = "us-east-1", model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"):
        import boto3
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
        self.model_id = model_id
        
    def extract(self, text: str, hints: str = "", schema_class: Optional[Any] = None) -> Optional[dict]:
        prompt = self._build_prompt(text, hints, schema_class)
        return self.generic_extract(prompt, schema_class)

    def generic_extract(self, prompt: str, schema_class: Optional[Any] = None) -> Optional[dict]:
        # Bedrock Claude 3 specific payload
        import json
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt + "\nRemember: RETURN ONLY VALID JSON."}]
                }
            ]
        }
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(payload)
            )
            
            result = json.loads(response.get("body").read())
            response_text = result["content"][0]["text"]
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            if schema_class:
                return schema_class.model_validate_json(response_text).model_dump()
            return json.loads(response_text)
        except Exception as e:
            print(f"AWS Bedrock Extraction failed: {e}")
            return None
