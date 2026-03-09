
import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    # Try health check first
    try:
        r = requests.get(f"{base_url}/health")
        print(f"Health Status: {r.status_code}")
        print(f"Health Response: {r.text}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # Try notifications (will likely 401 without token, but shouldn't 500)
    try:
        r = requests.get(f"{base_url}/api/notifications")
        print(f"Notifications Status: {r.status_code}")
        print(f"Notifications Response: {r.text}")
    except Exception as e:
        print(f"Notifications Call Failed: {e}")

if __name__ == "__main__":
    test_api()
