"""Lightweight Unstop spider using requests + BeautifulSoup.

Scrapes hackathon listings from unstop.com without requiring
Playwright or Ollama. Focuses on online/hybrid events.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
import json
import re
import time
from utils.tags import clean_tags, extract_tech_skills


class UnstopSpider:
    """Scrapes hackathon listings from Unstop (formerly Dare2Compete)."""

    BASE_URL = "https://unstop.com"
    LISTING_URL = "https://unstop.com/api/public/opportunity/search-result"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://unstop.com/hackathons",
        })

    def scrape(self, max_results: int = 20, opportunity_type: str = "hackathons") -> List[Dict[str, Any]]:
        """Scrape listings from Unstop's public API.

        Args:
            max_results: Maximum number of results to fetch.
            opportunity_type: The type of opportunity (hackathons, internships, scholarships, workshops, etc.)

        Returns:
            List of dicts matching the Opportunity schema.
        """
        results = []
        retries = 3

        for i in range(retries):
            try:
                # Unstop exposes a public JSON API for search results
                params = {
                    "opportunity": opportunity_type,
                    "per_page": str(min(max_results, 50)),
                    "oppstatus": "open",
                    "page": "1",
                }

                response = self.session.get(self.LISTING_URL, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                opportunities = data.get("data", {}).get("data", [])

                for opp in opportunities[:max_results]:
                    # Map Unstop types to our internal types
                    our_type = "hackathon"
                    if opportunity_type == "scholarships": our_type = "scholarship"
                    elif opportunity_type == "internships": our_type = "internship"
                    elif opportunity_type == "workshops": our_type = "skill_program"
                    
                    parsed = self._parse_opportunity(opp, our_type)
                    if parsed:
                        results.append(parsed)
                
                # If we successfully got results, break the retry loop
                if results:
                    break

            except (requests.exceptions.RequestException, ValueError, KeyError) as e:
                print(f"[UnstopSpider] Attempt {i+1} failed: {e}")
                if i < retries - 1:
                    time.sleep(2)
                    continue
                else:
                    print(f"[UnstopSpider] Max retries reached. Falling back to HTML scraping.")
                    # Fallback: try HTML scraping
                    results = self._scrape_html_fallback(max_results)

        print(f"[UnstopSpider] Scraped {len(results)} hackathons from Unstop")
        return results

    def _parse_opportunity(self, opp: dict, opp_type: str = "hackathon") -> Dict[str, Any] | None:
        """Parse a single opportunity from the Unstop API response.

        Args:
            opp: Raw opportunity dict from API.
            opp_type: Our internal type.

        Returns:
            Parsed dict matching Opportunity schema, or None if invalid.
        """
        try:
            title = opp.get("title", "").strip()
            if not title:
                return None

            # Parse deadline
            deadline_str = opp.get("end_date") or opp.get("regnEndDate", "")
            deadline = self._parse_date(deadline_str)

            # Determine location type
            opp_type_str = opp.get("festival", "") or ""
            is_online = opp.get("isOnline", False)
            location_type = "Online" if is_online else "Hybrid"

            # Build tags from categories/themes
            tags = []
            for cat in opp.get("filters", []):
                tag_name = cat.get("name", "").strip()
                if tag_name:
                    tags.append(tag_name)

            # Try to get subcategory tags too
            for sub in opp.get("subCategory", []):
                sub_name = sub.get("name", "").strip() if isinstance(sub, dict) else str(sub).strip()
                if sub_name and sub_name not in tags:
                    tags.append(sub_name)

            if not tags:
                tags = ["Hackathon"]
                
            # Clean tags and update eligibility
            # The title and description often contain clues too
            meta_text = f"{title} {opp.get('short_desc', '')} {opp.get('description', '')}"
            tech_skills = extract_tech_skills(meta_text)
            
            orig_eligibility = opp.get("eligibility", "Open to all")
            if isinstance(orig_eligibility, list):
                orig_eligibility = ", ".join(orig_eligibility) if orig_eligibility else "Open to all"
                
            cleaned_tags, final_eligibility = clean_tags(tags, str(orig_eligibility))
            
            # Combine extracted tech skills back into tags if they aren't already there
            for skill in tech_skills:
                if skill not in cleaned_tags:
                    cleaned_tags.append(skill)
            slug = opp.get("public_url") or opp.get("seo_url", "")
            if slug and not slug.startswith("http"):
                source_url = f"{self.BASE_URL}/{slug}"
            elif slug:
                source_url = slug
            else:
                source_url = f"{self.BASE_URL}/hackathons/{opp.get('id', '')}"

            # Image - Prioritize banner for better visual relevance
            image_url = opp.get("banner") or opp.get("logoUrl2") or opp.get("logoUrl", "")

            # Eligibility
            eligibility = opp.get("eligibility", "Open to all")
            if isinstance(eligibility, list):
                eligibility = ", ".join(eligibility) if eligibility else "Open to all"

            return {
                "title": title[:200],
                "description": (opp.get("short_desc") or opp.get("description", "") or f"{opp_type.capitalize()} on Unstop: {title}")[:1000],
                "type": opp_type,
                "deadline": deadline,
                "application_link": source_url,
                "image_url": image_url if image_url else None,
                "tags": json.dumps(cleaned_tags[:8]),
                "required_skills": json.dumps(tech_skills[:5]),
                "eligibility": str(final_eligibility)[:100] if final_eligibility else "Open to all",
                "location_type": location_type,
                "location": "India" if not is_online else "Online",
                "source_url": source_url,
                "status": "active",
                "source_registration_count": opp.get("registerCount", 0),
                "source_views_count": opp.get("viewsCount", 0)
            }
        except Exception as e:
            print(f"[UnstopSpider] Failed to parse opportunity: {e}")
            return None

    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats from Unstop into a datetime.

        Args:
            date_str: Date string in various possible formats.

        Returns:
            Parsed datetime, or 30 days from now as fallback.
        """
        from datetime import timedelta

        if not date_str:
            return datetime.utcnow() + timedelta(days=30)

        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d %b %Y",
            "%d %B %Y",
            "%b %d, %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        # Last resort: try dateutil
        try:
            import dateutil.parser
            return dateutil.parser.parse(date_str)
        except Exception:
            return datetime.utcnow() + timedelta(days=30)

    def _scrape_html_fallback(self, max_results: int) -> List[Dict[str, Any]]:
        """Fallback HTML scraping if the API approach fails.

        Args:
            max_results: Maximum number of results.

        Returns:
            List of parsed opportunity dicts.
        """
        results = []
        try:
            response = self.session.get(
                "https://unstop.com/hackathons",
                timeout=15
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Look for hackathon cards in the page
            cards = soup.select(".single_profile, .opportunity-card, [class*='hackathon']")

            for card in cards[:max_results]:
                title_el = card.select_one("h2, h3, .title, [class*='title']")
                link_el = card.select_one("a[href]")

                if title_el and link_el:
                    title = title_el.get_text(strip=True)
                    href = link_el.get("href", "")
                    if href and not href.startswith("http"):
                        href = f"{self.BASE_URL}{href}"

                    results.append({
                        "title": title[:200],
                        "description": f"Hackathon on Unstop: {title}",
                        "type": "hackathon",
                        "deadline": datetime.utcnow() + __import__("datetime").timedelta(days=30),
                        "application_link": href,
                        "tags": json.dumps(["Hackathon"]),
                        "required_skills": json.dumps([]),
                        "eligibility": "Open to all",
                        "location_type": "Online",
                        "location": "India",
                        "source_url": href,
                        "status": "active",
                    })
        except Exception as e:
            print(f"[UnstopSpider] HTML fallback also failed: {e}")

        return results
