# node_fastapi.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from typing import Optional
from async_lru import AsyncLRUCache

app = FastAPI(title="Local Async LRU Cache Node")

class StoreRequest(BaseModel):
    key: str
    value: str
    ttl: Optional[float] = None  # seconds

# create global cache instance (will be reused by uvicorn workers if single-process)
cache = AsyncLRUCache(capacity=1000)

# Background TTL purge task control
PURGE_INTERVAL_SECONDS = 5
_purge_task = None

@app.on_event("startup")
async def startup_event():
    global _purge_task
    # start background purge loop
    _purge_task = asyncio.create_task(purge_loop())

@app.on_event("shutdown")
async def shutdown_event():
    global _purge_task
    if _purge_task:
        _purge_task.cancel()
        try:
            await _purge_task
        except asyncio.CancelledError:
            pass

async def purge_loop():
    while True:
        try:
            await asyncio.sleep(PURGE_INTERVAL_SECONDS)
            # call internal purge by acquiring lock and scanning expired
            async with cache._lock:
                await cache._purge_expired_locked()
        except asyncio.CancelledError:
            break
        except Exception:
            # keep loop alive if unexpected error
            continue

@app.post("/store")
async def store_item(req: StoreRequest):
    if not req.key:
        raise HTTPException(status_code=400, detail="key required")
    await cache.set(req.key, req.value, req.ttl)
    return {"status": "ok"}

@app.get("/get/{key}")
async def get_item(key: str):
    val = await cache.get(key)
    if val is None:
        raise HTTPException(status_code=404, detail="not found")
    return {"key": key, "value": val}

@app.delete("/delete/{key}")
async def delete_item(key: str):
    await cache.delete(key)
    return {"status": "deleted"}

@app.get("/metrics")
async def metrics():
    return await cache.metrics()

if __name__ == "__main__":
    uvicorn.run("node_fastapi:app", host="127.0.0.1", port=8000, reload=False)
