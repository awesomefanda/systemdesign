# test_run.py
import asyncio
import httpx

BASE = "http://127.0.0.1:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # store with TTL=2s
        r = await client.post(f"{BASE}/store", json={"key": "foo", "value": "bar", "ttl": 2})
        print("store foo:", r.status_code, r.json())

        r = await client.get(f"{BASE}/get/foo")
        print("get foo immediately:", r.status_code, r.json())

        await asyncio.sleep(3)
        r = await client.get(f"{BASE}/get/foo")
        print("get foo after ttl:", r.status_code, r.text)

        # store many keys to trigger eviction
        for i in range(5):
            await client.post(f"{BASE}/store", json={"key": f"k{i}", "value": f"v{i}"})
        r = await client.get(f"{BASE}/metrics")
        print("metrics:", r.json())

if __name__ == "__main__":
    asyncio.run(main())
