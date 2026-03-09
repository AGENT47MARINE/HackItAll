
import requests
import sys

def test_proxy():
    url = "https://d8it4huxumps7.cloudfront.net/uploads/images/657989eb252a1_hackathon.jpg"
    proxy_url = f"http://localhost:8000/api/opportunities/proxy-image?url={url}"
    print(f"Testing proxy: {proxy_url}")
    try:
        resp = requests.get(proxy_url, timeout=10)
        print(f"Status Code: {resp.status_code}")
        print(f"Content Type: {resp.headers.get('Content-Type')}")
        print(f"Content Length: {len(resp.content)}")
        if resp.status_code == 200:
            print("Proxy SUCCESS!")
        else:
            print("Proxy FAILED with non-200 status.")
    except Exception as e:
        print(f"Error connecting to proxy: {e}")

if __name__ == "__main__":
    test_proxy()
