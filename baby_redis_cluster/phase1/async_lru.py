# async_lru.py
import time
import asyncio
from collections import OrderedDict
from typing import Optional, Any, Tuple

class AsyncLRUCache:
    """
    Async-safe LRU cache with TTL support.
    - capacity: max number of items
    - uses OrderedDict to keep recency order
    - stores values as (value, expiry_ts_or_None)
    """
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self._data: "OrderedDict[str, Tuple[Any, Optional[float]]]" = OrderedDict()
        self._lock = asyncio.Lock()
        # metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    async def _purge_expired_locked(self) -> None:
        """Assumes lock already held. Remove expired items."""
        now = time.time()
        # iterate from oldest to newest; stop early if expiry not found
        keys_to_delete = []
        for k, (v, exp) in self._data.items():
            if exp is not None and exp <= now:
                keys_to_delete.append(k)
        for k in keys_to_delete:
            self._data.pop(k, None)

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            await self._purge_expired_locked()
            if key not in self._data:
                self.misses += 1
                return None
            value, exp = self._data.pop(key)
            # check expiry again (in case it expired since purge)
            if exp is not None and exp <= time.time():
                self.misses += 1
                return None
            # mark as most recently used
            self._data[key] = (value, exp)
            self.hits += 1
            return value

    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        expiry = time.time() + ttl if ttl is not None else None
        async with self._lock:
            await self._purge_expired_locked()
            if key in self._data:
                # remove to re-insert at end (MRU)
                self._data.pop(key, None)
            self._data[key] = (value, expiry)
            # evict if over capacity
            while len(self._data) > self.capacity:
                self._data.popitem(last=False)
                self.evictions += 1

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)

    async def size(self) -> int:
        async with self._lock:
            return len(self._data)

    async def keys(self):
        async with self._lock:
            return list(self._data.keys())

    async def metrics(self):
        async with self._lock:
            return {"hits": self.hits, "misses": self.misses, "evictions": self.evictions, "size": len(self._data)}
