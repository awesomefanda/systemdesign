from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import make_asgi_app

from app.core.config import get_settings
from app.core.logging import logger
from app.api.routes import router as api_router
from app.services.rate_limit import limiter

settings = get_settings()

app = FastAPI(title=f"Python Microservice Starter — {settings.app_name}")

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        limiter.check("global", request.client.host)
    except Exception:
        return PlainTextResponse("Too Many Requests", status_code=429)
    response = await call_next(request)
    return response

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    return {"ready": True}

@app.get("/")
async def root():
    return {"service": settings.app_name}

app.include_router(api_router, prefix="/api")

metrics_app = make_asgi_app()
app.mount(settings.metrics_path, metrics_app)
