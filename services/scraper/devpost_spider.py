"""Lightweight Devpost spider using requests + BeautifulSoup.

Scrapes hackathon listings from devpost.com without requiring
Playwright or Ollama. Focuses on open/upcoming online hackathons.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import re


class DevpostSpider:
    """Scrapes hackathon listings from Devpost."""

    BASE_URL = "https://devpost.com"
    LISTING_URL = "https://devpost.com/api/hackathons"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        })

    def scrape(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Scrape hackathon listings from Devpost.

        Tries the JSON API first, falls back to HTML scraping.

        Args:
            max_results: Maximum number of results to fetch.

        Returns:
            List of dicts matching the Opportunity schema.
        """
        results = []

        # Try API-based approach first
        try:
            results = self._scrape_api(max_results)
        except Exception as e:
            print(f"[DevpostSpider] API approach failed: {e}")

        # Fallback to HTML scraping
        if not results:
            try:
                results = self._scrape_html(max_results)
            except Exception as e:
                print(f"[DevpostSpider] HTML approach also failed: {e}")

        print(f"[DevpostSpider] Scraped {len(results)} hackathons from Devpost")
        return results

    def _scrape_api(self, max_results: int) -> List[Dict[str, Any]]:
        """Try Devpost's JSON API endpoint.

        Args:
            max_results: Maximum results to fetch.

        Returns:
            List of parsed opportunity dicts.
        """
        results = []
        params = {
            "page": "1",
            "status[]": ["upcoming", "open"],
            "order_by": "deadline",
        }

        response = self.session.get(self.LISTING_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        hackathons = data.get("hackathons", [])

        for hack in hackathons[:max_results]:
            parsed = self._parse_api_hackathon(hack)
            if parsed:
                results.append(parsed)

        return results

    def _parse_api_hackathon(self, hack: dict) -> Dict[str, Any] | None:
        """Parse a single hackathon from Devpost API response.

        Args:
            hack: Raw hackathon dict from API.

        Returns:
            Parsed dict or None.
        """
        try:
            title = hack.get("title", "").strip()
            if not title:
                return None

            # Deadline
            deadline_str = hack.get("submission_period_dates", "")
            deadline = self._extract_deadline(deadline_str)

            # URL
            source_url = hack.get("url", "")
            if not source_url:
                return None

            # Themes/tags
            themes = hack.get("themes", [])
            tags = [t.get("name", t) if isinstance(t, dict) else str(t) for t in themes]
            if not tags:
                tags = ["Hackathon"]

            # Image - Prioritize banner over thumbnail
            image_url = hack.get("open_state_banner_url") or hack.get("thumbnail_url", "")

            # Prize
            prize = hack.get("prize_amount", "")
            description = hack.get("tagline", "") or f"Hackathon on Devpost: {title}"
            if prize:
                description = f"{description} Prize: {prize}"

            return {
                "title": title[:200],
                "description": description[:1000],
                "type": "hackathon",
                "deadline": deadline,
                "application_link": source_url,
                "image_url": image_url if image_url else None,
                "tags": json.dumps(tags[:5]),
                "required_skills": json.dumps([]),
                "eligibility": "Open to all",
                "location_type": "Online",  # Devpost is primarily online
                "location": "Online",
                "source_url": source_url,
                "status": "active",
                "source_registration_count": hack.get("registrations_count", 0)
            }
        except Exception as e:
            print(f"[DevpostSpider] Failed to parse API hackathon: {e}")
            return None

    def _scrape_html(self, max_results: int) -> List[Dict[str, Any]]:
        """Fallback: scrape Devpost hackathon listing page via HTML.

        Args:
            max_results: Maximum results to fetch.

        Returns:
            List of parsed opportunity dicts.
        """
        results = []

        response = self.session.get(
            f"{self.BASE_URL}/hackathons",
            params={"status[]": ["upcoming", "open"]},
            timeout=15,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Devpost uses .hackathon-tile or similar card elements
        tiles = soup.select(
            ".hackathon-tile, .challenge-listing, "
            "[data-hackathon-tile], .hackathons-container .hackathon"
        )

        # Broader fallback
        if not tiles:
            tiles = soup.select("a.clearfix, .challenge-card, article")

        for tile in tiles[:max_results]:
            parsed = self._parse_html_tile(tile)
            if parsed:
                results.append(parsed)

        return results

    def _parse_html_tile(self, tile) -> Dict[str, Any] | None:
        """Parse a single hackathon tile from HTML.

        Args:
            tile: BeautifulSoup element for one hackathon.

        Returns:
            Parsed dict or None.
        """
        try:
            # Title
            title_el = tile.select_one("h3, h2, .title, [class*='title']")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                return None

            # Link
            link = ""
            link_el = tile if tile.name == "a" else tile.select_one("a[href]")
            if link_el:
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    link = f"{self.BASE_URL}{href}"
                else:
                    link = href

            if not link:
                return None

            # Image
            img_el = tile.select_one("img[src]")
            image_url = img_el.get("src", "") if img_el else ""

            # Deadline text
            date_el = tile.select_one(".submission-period, .date, [class*='date']")
            deadline_text = date_el.get_text(strip=True) if date_el else ""
            deadline = self._extract_deadline(deadline_text)

            # Tags from metadata
            tag_els = tile.select(".tag, .theme, [class*='theme']")
            tags = [t.get_text(strip=True) for t in tag_els if t.get_text(strip=True)]
            if not tags:
                tags = ["Hackathon"]

            # Participant count (Global registrations)
            reg_count = 0
            reg_el = tile.select_one(".participants strong")
            if reg_el:
                try:
                    reg_text = reg_el.get_text(strip=True).replace(",", "")
                    reg_count = int(reg_text)
                except (ValueError, TypeError):
                    reg_count = 0

            return {
                "title": title[:200],
                "description": f"Hackathon on Devpost: {title}",
                "type": "hackathon",
                "deadline": deadline,
                "application_link": link,
                "image_url": image_url if image_url else None,
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
            print(f"[DevpostSpider] Failed to parse HTML tile: {e}")
            return None

    def _extract_deadline(self, date_text: str) -> datetime:
        """Extract a deadline datetime from various date text formats.

        Devpost often shows ranges like 'Jan 15 - Mar 01, 2025'.
        We take the end date.

        Args:
            date_text: Raw date string from the page.

        Returns:
            Parsed datetime, or 30 days from now as fallback.
        """
        if not date_text:
            return datetime.utcnow() + timedelta(days=30)

        # Try to find a date pattern like "Mar 01, 2025" at the end
        # Devpost format: "Jan 15 - Mar 01, 2025"
        patterns = [
            r"(\w+ \d{1,2},?\s*\d{4})\s*$",  # "Mar 01, 2025"
            r"-\s*(\w+ \d{1,2},?\s*\d{4})",  # "- Mar 01, 2025"
            r"(\d{4}-\d{2}-\d{2})",  # "2025-03-01"
        ]

        for pattern in patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    import dateutil.parser
                    return dateutil.parser.parse(match.group(1))
                except Exception:
                    continue

        # Direct parse attempts
        formats = [
            "%b %d, %Y",
            "%B %d, %Y",
            "%Y-%m-%d",
            "%d %b %Y",
        ]

        clean_text = date_text.strip()
        for fmt in formats:
            try:
                return datetime.strptime(clean_text, fmt)
            except ValueError:
                continue

        return datetime.utcnow() + timedelta(days=30)
