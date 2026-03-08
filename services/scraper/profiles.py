"""Registry for site-specific hints to help the AI scraper."""

SITE_PROFILES = {
    "devpost.com": "Devpost: Look for the 'Hackathons' list. Extract title, prizes, and 'Registration Ends' date.",
    "devfolio.co": "Focus on the cards. Each card contains a 'Apply Now' button link.",
    "mlh.io": "Major League Hacking events usually have a location (City, State or Virtual).",
    "unstop.com": "Look for 'Compete' or 'Hackathons' categories. Extract the specific registration link.",
    "hackerearth.com": "Events are often categorized as 'Upcoming' or 'Ongoing'. Focus on registration dates.",
    "unstop.com": "Extraction should focus on the 'Register' button and the title in the main card.",
}

def get_hints_for_url(url: str) -> str:
    """Extract domain from URL and return matching hints."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    
    # Try exact match first
    if domain in SITE_PROFILES:
        return SITE_PROFILES[domain]
    
    # Try partial match (e.g., 'sub.devpost.com' matches 'devpost.com')
    for key, hints in SITE_PROFILES.items():
        if key in domain:
            return hints
            
    return ""
