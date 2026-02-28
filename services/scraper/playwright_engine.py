import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
from typing import Tuple

class PlaywrightEngine:
    """Handles rendering complex JS websites and extracting clean text and metadata."""
    
    def __init__(self, timeout: int = 15000):
        self.timeout = timeout
        
    def fetch_clean_content(self, url: str) -> Tuple[str, dict]:
        """
        Loads the page, extracts OpenGraph metadata (image, title), 
        and strips all HTML logic to return just the plaintext visible to the user.
        Uses a fallback Stealth Mode if the initial fetch is blocked.
        """
        metadata = {
            "title": "",
            "image": "",
            "description": ""
        }
        
        # Helper to fetch HTML
        def _get_html(use_stealth=False) -> str:
            with sync_playwright() as p:
                args = ["--disable-blink-features=AutomationControlled"] if use_stealth else []
                browser = p.chromium.launch(headless=True, args=args)
                
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = context.new_page()
                if use_stealth:
                    from playwright_stealth import stealth_sync
                    stealth_sync(page)
                    
                # wait_until='networkidle' ensures React/Next.js finishes loading
                page.goto(url, timeout=self.timeout if not use_stealth else self.timeout + 15000, wait_until="networkidle")
                
                # Optional: scroll down to trigger lazy loading
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1) # wait for lazy images/text
                
                content = page.content()
                browser.close()
                return content

        html_content = ""
        try:
            print(f"[{url}] Attempting standard Playwright fetch...")
            html_content = _get_html(use_stealth=False)
        except Exception as e:
            print(f"[{url}] Blocked or Timeout detected: {e}.")
            print(f"[{url}] Automatically retrying with Stealth Mode...")
            try:
                html_content = _get_html(use_stealth=True)
            except Exception as stealth_e:
                print(f"[{url}] Stealth Mode also failed: {stealth_e}")
                return "", metadata
                
            
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Extract Metadata Fast-Path
        title_tag = soup.find("meta", property="og:title") or soup.find("title")
        if title_tag:
            metadata["title"] = title_tag.get("content", title_tag.string) if title_tag.name == "meta" else title_tag.string
            
        img_tag = soup.find("meta", property="og:image")
        if img_tag:
            metadata["image"] = img_tag.get("content", "")
            
        desc_tag = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            metadata["description"] = desc_tag.get("content", "")
            
        # 2. Strip junk tags
        for script in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "svg"]):
            script.extract()
            
        # 3. Get clean text
        text = soup.get_text(separator='\n')
        
        # 4. Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return clean_text, metadata
