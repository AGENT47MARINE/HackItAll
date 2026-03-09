"""Utility for cleaning and filtering opportunity tags."""
import re
from typing import List, Tuple

# Terms that should be moved from tags to eligibility
ELIGIBILITY_TERMS = [
    r"undergraduate", r"postgraduate", r"ph\.?d", r"mba", r"engineering", 
    r"b\.?tech", r"m\.?tech", r"high school", r"students?", r"professionals?", 
    r"freshers?", r"graduates?", r"alumni", r"masters?", r"bachelors?",
    r"school", r"college", r"university", r"working", r"early career",
    r"open to all", r"batch", r"class of", r"women", r"diversity"
]

def clean_tags(tags: List[str], current_eligibility: str = "") -> Tuple[List[str], str]:
    """Clean tags by removing eligibility criteria and moving them to eligibility field.
    
    Args:
        tags: List of tags to clean
        current_eligibility: Existing eligibility string
        
    Returns:
        Tuple of (cleaned_tags, updated_eligibility)
    """
    cleaned_tags = []
    eligibility_additions = []
    
    # Pre-compiled regex patterns
    patterns = [re.compile(term, re.IGNORECASE) for term in ELIGIBILITY_TERMS]
    
    for tag in tags:
        tag_str = str(tag).strip()
        is_eligibility = False
        
        for pattern in patterns:
            if pattern.search(tag_str):
                is_eligibility = True
                break
        
        if is_eligibility:
            if tag_str not in eligibility_additions:
                eligibility_additions.append(tag_str)
        else:
            # Only keep if it's not a generic term and has reasonable length
            if tag_str and len(tag_str) > 1 and tag_str.lower() not in ["hackathon", "competition", "event"]:
                cleaned_tags.append(tag_str)
    
    # Update eligibility string
    new_eligibility = current_eligibility
    if eligibility_additions:
        additions_str = ", ".join(eligibility_additions)
        if new_eligibility and new_eligibility.lower() != "open to all":
            # Append if not already present partially
            if additions_str.lower() not in new_eligibility.lower():
                new_eligibility = f"{new_eligibility}; {additions_str}"
        else:
            new_eligibility = additions_str
            
    return cleaned_tags, new_eligibility

def extract_tech_skills(text: str) -> List[str]:
    """Extract technical skills from text using a pre-defined dictionary."""
    # Simplified version of the logic in ScraperService
    tech_skills = {
        # Languages
        "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
        "java ": "Java", "cpp": "C++", "c#": "C#", "kotlin": "Kotlin", "swift": "Swift", 
        "rust": "Rust", "golang": "Go", "go ": "Go", "ruby": "Ruby", "php": "PHP", 
        "dart": "Dart", "scala": "Scala",
        
        # Web Frameworks
        "react": "React", "next.js": "Next.js", "nextjs": "Next.js", "angular": "Angular", 
        "vue": "Vue.js", "node": "Node.js", "express": "Express", "django": "Django", 
        "flask": "Flask", "fastapi": "FastAPI", "svelte": "Svelte", "laravel": "Laravel",
        "spring": "Spring Boot", "tailwind": "Tailwind CSS",
        
        # Mobile & Cross-platform
        "flutter": "Flutter", "react native": "React Native", "android": "Android", "ios": "iOS",
        
        # AI & Data Science
        "tensorflow": "TensorFlow", "pytorch": "PyTorch", "ai ": "AI", "ml ": "ML",
        "nlp": "NLP", "opencv": "OpenCV", "pandas": "Pandas", "numpy": "NumPy",
        "generative ai": "Generative AI", "llm": "LLM", "deep learning": "Deep Learning",
        
        # Cloud & DevOps
        "docker": "Docker", "kubernetes": "Kubernetes", "aws": "AWS", "gcp": "GCP",
        "azure": "Azure", "terraform": "Terraform", "jenkins": "Jenkins", "github actions": "CI/CD",
        "ansible": "Ansible", "firebase": "Firebase",
        
        # Database
        "sql": "SQL", "postgresql": "PostgreSQL", "mongodb": "MongoDB", "redis": "Redis",
        "graphql": "GraphQL", "elasticsearch": "Elasticsearch",
        
        # Design & Specialized
        "figma": "Figma", "ui/ux": "UI/UX", "unity": "Unity", "web3": "Web3", 
        "blockchain": "Blockchain", "cybersecurity": "Cybersecurity", "ar/vr": "AR/VR"
    }
    
    found = set()
    lower_text = f" {text.lower()} "
    for key, display in tech_skills.items():
        if f" {key} " in lower_text or f" {key.strip()}," in lower_text or f" {key.strip()}." in lower_text:
            found.add(display)
            
    return sorted(list(found))

def extract_interests(text: str) -> List[str]:
    """Extract professional interests from text using keyword mapping."""
    interest_map = {
        "artificial intelligence": "AI", "machine learning": "Machine Learning",
        "deep learning": "Deep Learning", "natural language processing": "NLP",
        "computer vision": "Computer Vision", "ai/ml": "AI/ML",
        "web development": "Web Development", "frontend": "Frontend", 
        "backend": "Backend", "full stack": "Full Stack",
        "mobile development": "Mobile Development", "android": "Android", "ios": "iOS",
        "cybersecurity": "Cybersecurity", "ethical hacking": "Cybersecurity",
        "blockchain": "Blockchain", "web3": "Web3", "cryptocurrency": "Web3",
        "cloud computing": "Cloud", "devops": "DevOps",
        "data science": "Data Science", "data analytics": "Data Science",
        "fintech": "Fintech", "finance": "Fintech",
        "game development": "Game Dev", "ar/vr": "AR/VR", "augmented reality": "AR/VR",
        "open source": "Open Source", "competitive programming": "Competitive Programming"
    }
    
    found = set()
    lower_text = text.lower()
    for key, display in interest_map.items():
        if key in lower_text:
            found.add(display)
            
    return sorted(list(found))
