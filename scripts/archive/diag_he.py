import requests
from bs4 import BeautifulSoup

url = "https://www.hackerearth.com/challenges/hackathon/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

resp = requests.get(url, headers=headers)
print(f"Status: {resp.status_code}")
soup = BeautifulSoup(resp.text, 'html.parser')
cards = soup.select(".challenge-card-wrapper")
print(f"Cards found: {len(cards)}")
if cards:
    print("--- CARD 1 HTML ---")
    print(cards[0].prettify())
    print("--- END CARD 1 HTML ---")
