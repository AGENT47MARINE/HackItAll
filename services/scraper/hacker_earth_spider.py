"""Lightweight HackerEarth spider using requests + BeautifulSoup.

Scrapes hackathon listings from hackerearth.com.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import re

class HackerEarthSpider:
    """Scrapes hackathon listings from HackerEarth."""

    BASE_URL = "https://www.hackerearth.com"
    CHALLENGES_URL = "https://www.hackerearth.com/challenges/hackathon/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        })

    def scrape(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Scrape hackathon listings from HackerEarth.

        Args:
            max_results: Maximum number of results to fetch.

        Returns:
            List of dicts matching the Opportunity schema.
        """
        results = []
        try:
            response = self.session.get(self.CHALLENGES_URL, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # HackerEarth uses .challenge-card-wrapper or similar
            cards = soup.select(".challenge-card-wrapper, .challenge-list .challenge-card")
            
            # Fallback if selectors changed
            if not cards:
                cards = soup.select(".upcoming.challenge-list .challenge-card-wrapper")

            for card in cards[:max_results]:
                parsed = self._parse_card(card)
                if parsed:
                    results.append(parsed)
        except Exception as e:
            print(f"[HackerEarthSpider] Scraping failed: {e}")

        print(f"[HackerEarthSpider] Scraped {len(results)} hackathons from HackerEarth")
        return results

    def _parse_card(self, card) -> Dict[str, Any] | None:
        """Parse a single challenge card from HackerEarth.

        Args:
            card: BeautifulSoup element for one challenge.

        Returns:
            Parsed dict or None.
        """
        try:
            # Title extraction - can be on the card itself or a child
            title = ""
            if card.has_attr('class') and any(c in card['class'] for c in ['challenge-list-title', 'challenge-name']):
                title = card.get_text(strip=True)
            else:
                title_el = card.select_one(".challenge-name, .challenge-list-title, .challenge-card-title")
                if title_el:
                    title = title_el.get_text(strip=True)
            
            if not title:
                # Last resort title extraction
                title_el = card.find(['h1', 'h2', 'h3', 'h4'])
                if title_el:
                    title = title_el.get_text(strip=True)

            if not title:
                return None

            # Link extraction
            link = ""
            if card.name == 'a' and card.has_attr('href'):
                link = card['href']
            else:
                link_el = card.select_one("a[href]")
                if link_el:
                    link = link_el.get("href", "")
            
            if link and not link.startswith("http"):
                link = f"{self.BASE_URL}{link}"
            
            if not link:
                return None

            # Type - identify if it's a hackathon
            challenge_type_el = card.select_one(".challenge-type, .challenge-card-type")
            challenge_type = challenge_type_el.get_text(strip=True).lower() if challenge_type_el else "hackathon"
            
            # Tags
            tag_els = card.select(".challenge-tags, .tag")
            tags = [t.get_text(strip=True) for t in tag_els if t.get_text(strip=True)]
            if not tags:
                tags = ["Hackathon"]

            # Deadline extraction (HackerEarth usually shows "Starts on" or "Ends on")
            # We'll default to 30 days if we can't parse it easily from the list view
            deadline = datetime.utcnow() + timedelta(days=30)
            date_el = card.select_one(".date, .challenge-date")
            if date_el:
                date_text = date_el.get_text(strip=True)
                # Simple parsing attempt
                try:
                    import dateutil.parser
                    deadline = dateutil.parser.parse(date_text, fuzzy=True)
                except:
                    pass

            # Registration Count
            reg_count = 0
            reg_el = card.select_one(".participants, .registrations, [class*='registrations']")
            if reg_el:
                reg_text = reg_el.get_text(strip=True).replace(",", "")
                digits = re.findall(r"\d+", reg_text)
                if digits:
                    reg_count = int(digits[0])

            return {
                "title": title[:200],
                "description": f"Hackathon on HackerEarth: {title}",
                "type": "hackathon",
                "deadline": deadline,
                "application_link": link,
                "image_url": None, # HackerEarth usually has background images in CSS
                "tags": json.dumps(tags[:5]),
                "required_skills": json.dumps([]),
                "eligibility": "Open to all",
                "location_type": "Online",
                "location": "Online",
                "source_url": link,
                "status": "active",
                "source_registration_count": reg_count
            }
        except Exception as e:
            print(f"[HackerEarthSpider] Failed to parse card: {e}")
            return None
