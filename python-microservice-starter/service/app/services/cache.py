import redis.asyncio as redis
from redis.exceptions import RedisError

cache = redis.Redis(host="redis", port=6379, decode_responses=True)

async def set_key(key: str, value: str, expire: int = 3600):
    try:
        await cache.set(key, value, ex=expire)
    except RedisError as e:
        print(f"Redis set_key error: {e}")

async def get_key(key: str):
    try:
        return await cache.get(key)
    except RedisError as e:
        print(f"Redis get_key error: {e}")
        return None
