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
        """Heuristic keyword matching to deduce skills and categorization tags.
        
        Expanded to cover a wide range of tech domains including cybersecurity,
        data science, hardware, design, gaming, DevOps, and cloud platforms.
        """
        import json
        
        # Comprehensive tech skills dictionary
        tech_skills = {
            # Languages
            "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
            "react": "React", "angular": "Angular", "vue": "Vue.js",
            "node": "Node.js", "java ": "Java", "kotlin": "Kotlin", "swift": "Swift",
            "c++": "C++", "c#": "C#", "rust": "Rust", "golang": "Go", "go ": "Go",
            "ruby": "Ruby", "php": "PHP", "html": "HTML", "css": "CSS",
            "sql": "SQL", "graphql": "GraphQL", "r ": "R",
            # AI / ML / Data
            "machine learning": "Machine Learning", "ml ": "Machine Learning",
            "deep learning": "Deep Learning", "ai ": "AI", "artificial intelligence": "AI",
            "tensorflow": "TensorFlow", "pytorch": "PyTorch", "keras": "Keras",
            "nlp": "NLP", "computer vision": "Computer Vision", "opencv": "OpenCV",
            "data science": "Data Science", "data analysis": "Data Analysis",
            "pandas": "Pandas", "scikit": "Scikit-learn",
            "large language model": "LLM", "llm": "LLM", "generative ai": "Generative AI",
            # Cloud & DevOps
            "aws": "AWS", "gcp": "GCP", "azure": "Azure",
            "docker": "Docker", "kubernetes": "Kubernetes", "terraform": "Terraform",
            "ci/cd": "CI/CD", "devops": "DevOps",
            # Security
            "cybersecurity": "Cybersecurity", "cyber security": "Cybersecurity",
            "penetration testing": "Penetration Testing", "ethical hacking": "Ethical Hacking",
            "ctf": "CTF", "capture the flag": "CTF",
            "infosec": "InfoSec", "malware": "Malware Analysis",
            "cryptography": "Cryptography", "encryption": "Encryption",
            # Web3 & Blockchain
            "blockchain": "Blockchain", "web3": "Web3", "solidity": "Solidity",
            "ethereum": "Ethereum", "smart contract": "Smart Contracts", "defi": "DeFi",
            "nft": "NFT",
            # Hardware & IoT
            "arduino": "Arduino", "raspberry pi": "Raspberry Pi",
            "iot": "IoT", "internet of things": "IoT",
            "embedded": "Embedded Systems", "robotics": "Robotics", "3d print": "3D Printing",
            "hardware": "Hardware",
            # Design
            "figma": "Figma", "ui/ux": "UI/UX", "ux design": "UX Design",
            "ui design": "UI Design", "user experience": "UX Design",
            # Gaming
            "unity": "Unity", "unreal": "Unreal Engine", "game dev": "Game Development",
            "godot": "Godot",
        }
        
        found_skills = set()
        for key, display_name in tech_skills.items():
            if f" {key} " in f" {body_text} " or f" {key} " in f" {meta_text} ":
                found_skills.add(display_name)
                
        # Expanded categorization tags
        tags = set()
        tag_rules = {
            "hackathon": "Hackathon", "workshop": "Workshop", "conference": "Conference",
            "beginner": "Beginner Friendly", "open source": "Open Source",
            "prize": "Prizes", " win ": "Prizes",
            "sustainability": "Sustainability", "climate": "Climate Tech",
            "health": "HealthTech", "medtech": "MedTech", "fintech": "FinTech",
            "edtech": "EdTech", "social impact": "Social Impact",
            "women in tech": "Diversity", "diversity": "Diversity",
            "virtual": "Virtual", "hybrid": "Hybrid", "in-person": "In-Person",
            "cybersecurity": "Cybersecurity", "ctf": "CTF",
            "game jam": "Game Jam", "datathon": "Datathon",
            "designathon": "Designathon", "ideathon": "Ideathon",
            "startup": "Startup", "entrepreneurship": "Entrepreneurship",
        }
        for key, tag_name in tag_rules.items():
            if key in body_text:
                tags.add(tag_name)
        
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
