from services.scraper.hacker_earth_spider import HackerEarthSpider
import json

spider = HackerEarthSpider()
results = spider.scrape(max_results=5)
print(f"Results: {len(results)}")
for r in results:
    print(f"- {r['title']}")
