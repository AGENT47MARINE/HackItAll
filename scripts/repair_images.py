
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://hackitall:hackitall_pwd@localhost:5432/hackitall_db")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def fetch_og_image(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Try og:image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            return og_image.get("content")
            
        # Try twitter:image
        tw_image = soup.find("meta", name="twitter:image")
        if tw_image:
            return tw_image.get("content")
            
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def repair_images():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Increase limit to 50
    cur.execute("SELECT id, source_url, title FROM opportunities WHERE image_url IS NULL AND status = 'active' LIMIT 50;")
    rows = cur.fetchall()
    
    repaired_count = 0
    print(f"Found {len(rows)} opportunities needing repair.")
    
    for opp_id, source_url, title in rows:
        if not source_url or not source_url.startswith("http"):
            print(f"Skipping {title}: Invalid source_url ({source_url})")
            continue
            
        print(f"Repairing: {title} ({source_url})")
        new_image = fetch_og_image(source_url)
        if new_image:
            print(f"  Found image: {new_image}")
            cur.execute("UPDATE opportunities SET image_url = %s WHERE id = %s", (new_image, opp_id))
            repaired_count += 1
        else:
            print("  No image found.")
            
    conn.commit()
    cur.close()
    conn.close()
    print(f"\nSuccessfully repaired {repaired_count} images.")

if __name__ == "__main__":
    repair_images()
