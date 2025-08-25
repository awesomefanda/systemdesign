from fastapi import APIRouter
from app.services.cache import set_key, get_key

router = APIRouter()

@router.get("/cache/set")
async def cache_set(key: str, value: str):
    await set_key(key, value)
    return {"message": f"Key '{key}' set with value '{value}'"}

@router.get("/cache/get")
async def cache_get(key: str):
    value = await get_key(key)
    if value is None:
        return {"message": f"Key '{key}' not found"}
    return {"key": key, "value": value}
