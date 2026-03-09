"""Service for parsing resumes and extracting structured profile data."""
import os
from typing import Dict, Any, List, Optional
import json
from pypdf import PdfReader
from utils.tags import extract_tech_skills, extract_interests
import io

from services.nlp.extractors import LLMExtractor, LocalLLMExtractor

class ResumeParserService:
    """Service for extracting profile data from resumes."""

    def __init__(self, extractor: Optional[LLMExtractor] = None):
        """Initialize the resume parser service.
        
        Args:
            extractor: Optional LLM extractor instance
        """
        self.extractor = extractor or LocalLLMExtractor()

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract raw text from a PDF file.
        
        Args:
            pdf_content: Binary content of the PDF file
            
        Returns:
            Extracted text string
        """
        try:
            reader = PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"[ResumeParserService] text extraction failed: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Use LLM to extract structured profile data from resume text.
        
        Args:
            text: Raw resume text
            
        Returns:
            Dictionary containing extracted skills, interests, and education
        """
        # Truncate text to fit context window (approx 4k characters is safe for gemma3:4b)
        truncated_text = text[:4000]
        
        prompt = f"""
        Extract professional profile data from the following resume text. 
        Focus on:
        1. **Skills**: Technical stack, languages, tools, and methodologies.
        2. **Interests**: Specific fields like AI, Web Dev, Cybersecurity, or Fintech.
        3. **Education**: Highest degree or currently pursuing level.

        Return ONLY a JSON object with these keys:
        - "skills": [list of strings]
        - "interests": [list of strings]
        - "education_level": "Undergraduate" | "B.Tech" | "Graduate" | "M.Tech" | "High School" | "PhD"

        RESUME TEXT:
        {truncated_text}
        """
        
        try:
            result = self.extractor.generic_extract(prompt)
            print(f"[ResumeParserService] LLM result: {result}")
            
            # If LLM fails or returns empty, use keyword fallback
            if not result or (not result.get("skills") and not result.get("interests")):
                print("[ResumeParserService] LLM returned no data. Using keyword fallback.")
                fallback_skills = extract_tech_skills(truncated_text)
                fallback_interests = extract_interests(truncated_text)
                return {
                    "skills": fallback_skills,
                    "interests": fallback_interests,
                    "education_level": "Undergraduate",
                    "raw_text": truncated_text
                }
                
            return {
                "skills": result.get("skills", []),
                "interests": result.get("interests", []),
                "education_level": result.get("education_level", "Undergraduate"),
                "raw_text": truncated_text
            }
        except Exception as e:
            print(f"Resume parsing error: {e}. Using keyword fallback.")
            fallback_skills = extract_tech_skills(truncated_text)
            fallback_interests = extract_interests(truncated_text)
            return {
                "skills": fallback_skills, 
                "interests": fallback_interests, 
                "education_level": "Undergraduate",
                "raw_text": truncated_text
            }

    def get_structured_profile(self, pdf_content: bytes) -> Dict[str, Any]:
        """Full pipeline: Extract text and parse into structured data.
        
        Args:
            pdf_content: Binary PDF data
            
        Returns:
            Structured profile dictionary
        """
        text = self.extract_text_from_pdf(pdf_content)
        print(f"[ResumeParserService] Extracted {len(text)} characters from PDF.")
        return self.parse_resume(text)
