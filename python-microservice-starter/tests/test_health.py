import requests
import time

BASE_URL = "http://localhost:8000"
CACHE_API = f"{BASE_URL}/api/cache"
HEALTH = f"{BASE_URL}/health"
NUM_REQUESTS = 120  # Number of requests to send for testing rate limit

def test_health():
    resp = requests.get(HEALTH)
    print("Health:", resp.status_code, resp.json())

def test_cache():
    # Set some keys
    for i in range(5):
        key = f"key{i}"
        value = f"value{i}"
        resp = requests.get(f"{CACHE_API}/set?key={key}&value={value}")
        print("Set:", resp.json())

    # Get the keys
    for i in range(5):
        key = f"key{i}"
        resp = requests.get(f"{CACHE_API}/get?key={key}")
        print("Get:", resp.json())

def test_rate_limit():
    print("\nTesting rate limiting:")
    for i in range(NUM_REQUESTS):
        resp = requests.get(HEALTH)
        if resp.status_code == 429:
            print(f"Request {i+1}: Rate limited!")
        else:
            print(f"Request {i+1}: OK")
        time.sleep(0.05)  # 50ms between requests

if __name__ == "__main__":
    print("=== Health Check ===")
    test_health()

    print("\n=== Cache Test ===")
    test_cache()

    print("\n=== Rate Limit Test ===")
    test_rate_limit()
