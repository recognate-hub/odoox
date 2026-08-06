import time

from fastapi import Depends, HTTPException, Request

from config.settings import get_settings
from core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Simple in-memory rate limiter (works without Redis too)
# For production with multiple workers, use Redis-backed version
_rate_store: dict[str, list[float]] = {}

async def init_rate_limiter():
    """Initialize rate limiter. Currently uses in-memory store.
    When REDIS_URL is set, you can swap to a Redis-backed implementation."""
    if settings.REDIS_URL:
        logger.info("REDIS_URL configured. Rate limiting is active.")
    else:
        logger.warning("REDIS_URL not set. Using in-memory rate limiting (single-worker only).")

def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    """Returns True if the request is allowed, False if rate limited."""
    now = time.time()
    if key not in _rate_store:
        _rate_store[key] = []
    
    # Clean old entries outside the window
    _rate_store[key] = [t for t in _rate_store[key] if now - t < window_seconds]
    
    if len(_rate_store[key]) >= max_requests:
        return False
    
    _rate_store[key].append(now)
    return True

def get_rate_limiter(times: int = 50, seconds: int = 60):
    """Returns a FastAPI dependency that enforces rate limiting."""
    async def _rate_limit_dependency(request: Request):
        # Use client IP or forwarded header as the rate limit key
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}"
        
        if not _check_rate_limit(key, times, seconds):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {times} requests per {seconds} seconds."
            )
    
    return Depends(_rate_limit_dependency)
