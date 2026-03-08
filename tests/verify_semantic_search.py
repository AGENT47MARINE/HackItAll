import sys
import os
import requests
import json

def test_semantic_search():
    base_url = "http://localhost:8000/api/opportunities/search/semantic"
    
    # Intent-based queries
    test_queries = [
        "beginner friendly AI hackathons",
        "events for web developers with cash prizes",
        "scholarships for graduate students in india"
    ]
    
    print("Testing Semantic Search Endpoints...")
    
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        try:
            # We assume the server is running or we just check the logic with a unit test style approach if it's not
            # But here let's try a direct request if possible or at least show the intent
            response = requests.get(base_url, params={"q": q, "limit": 3})
            if response.status_code == 200:
                results = response.json()
                print(f"Found {len(results)} matches.")
                for i, res in enumerate(results):
                    print(f"  {i+1}. {res['title']} (Location: {res['location']})")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")

if __name__ == "__main__":
    test_semantic_search()
