"""Service for scraping hackathon and opportunity details from external URLs."""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from datetime import datetime
from typing import Dict, Any, List

class ScraperService:
    """Service for extracting metadata from external opportunity URLs."""

    def __init__(self):
        # Use a standard user agent to avoid basic blocks
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape a URL and extract relevant opportunity metadata.
        
        Extracts Open Graph tags (og:title, og:image) and analyzes body text 
        to deduce required skills and tags for the ML recommendation engine.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing scraped data (title, description, image, skills, tags)
        """
        try:
            # Add scheme if missing
            if not url.startswith('http'):
                url = 'https://' + url
                
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Extract Title
            title = self._extract_title(soup)
            
            # 2. Extract Description
            description = self._extract_description(soup)
            
            # 3. Extract Image (crucial for visual frontend cards)
            image_url = self._extract_image(soup, url)
            
            # 4. Extract Keywords/Skills from body text
            body_text = soup.get_text(separator=' ', strip=True).lower()
            skills, tags = self._extract_keywords(body_text, title.lower() + " " + description.lower())
            
            # Determine type based on keywords
            opp_type = self._determine_type(title.lower() + " " + tags)
            
            return {
                "title": title[:200] if title else "Unknown Opportunity",
                "description": description[:1000] if description else "No description provided.",
                "image_url": image_url,
                "required_skills": skills,
                "tags": tags,
                "type": opp_type,
                "application_link": url,
                # We can't reliably parse arbitrary deadlines from HTML without LLMs, 
                # so we will leave it empty for the user to confirm/edit manually on frontend
                "deadline": None 
            }
            
        except Exception as e:
            print(f"Scraping error for {url}: {str(e)}")
            # Return graceful fallback
            return {
                "title": urlparse(url).netloc,
                "description": "Scraped from " + url,
                "application_link": url,
                "image_url": None,
                "required_skills": "[]",
                "tags": "[]",
                "type": "other"
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Try to find the best title using og:title falling back to <title>."""
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
            
        if soup.title and soup.title.string:
            return soup.title.string.strip()
            
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
            
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Try to find the best description."""
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
            
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
            
        # Fallback to first decent paragraph
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 50:
                return text
                
        return ""

    def _extract_image(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract the main promotional image using og:image."""
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            # Handle relative URLs in og tags (rare but happens)
            if img_url.startswith('/'):
                parsed_base = urlparse(base_url)
                return f"{parsed_base.scheme}://{parsed_base.netloc}{img_url}"
            return img_url
        return None

    def _extract_keywords(self, body_text: str, meta_text: str) -> Tuple[str, str]:
        """Simple heuristic keyword matching to deduce skills and categorization tags."""
        import json
        
        # Pre-defined list of common tech hackathon skills
        tech_skills = {
            "python": "Python", "javascript": "JavaScript", "react": "React", 
            "node": "Node.js", "java ": "Java", "c++": "C++", "html": "HTML", 
            "css": "CSS", "sql": "SQL", "aws": "AWS", "gcp": "GCP", 
            "azure": "Azure", "docker": "Docker", "kubernetes": "Kubernetes",
            "machine learning": "Machine Learning", "ml": "Machine Learning", 
            "ai ": "AI", "artificial intelligence": "AI", 
            "tensorflow": "TensorFlow", "pytorch": "PyTorch", 
            "nlp": "NLP", "blockchain": "Blockchain", "web3": "Web3"
        }
        
        found_skills = set()
        for key, display_name in tech_skills.items():
            # Check if skill keyword exists in body or metadata
            if f" {key} " in f" {body_text} " or f" {key} " in f" {meta_text} ":
                found_skills.add(display_name)
                
        # Generate some generic tags based on the text
        tags = set()
        if "hackathon" in body_text: tags.add("Hackathon")
        if "workshop" in body_text: tags.add("Workshop")
        if "beginner" in body_text: tags.add("Beginner Friendly")
        if "open source" in body_text: tags.add("Open Source")
        if "prize" in body_text or "win" in body_text: tags.add("Prizes")
        
        # Return as JSON strings for the database
        return json.dumps(list(found_skills)), json.dumps(list(tags))

    def _determine_type(self, text_to_analyze: str) -> str:
        """Deduce the opportunity type from text."""
        if "internship" in text_to_analyze or "intern " in text_to_analyze:
            return "internship"
        if "scholarship" in text_to_analyze:
            return "scholarship"
        if "fellowship" in text_to_analyze:
            return "fellowship"
        if "workshop" in text_to_analyze or "bootcamp" in text_to_analyze:
            return "skill_program"
            
        # Default to hackathon if unsure, since that's the platform's focus
        return "hackathon"
