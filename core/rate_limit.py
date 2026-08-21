import time

from fastapi import Depends, HTTPException, Request

from config.settings import get_settings
from core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# In-memory fallback rate limiter (single-worker only)
_rate_store: dict[str, list[float]] = {}


async def init_rate_limiter():
    """Initialize rate limiter. Uses Redis when REDIS_URL is set, in-memory otherwise."""
    if settings.REDIS_URL:
        logger.info("REDIS_URL configured. Redis-backed rate limiting is active.")
    else:
        logger.warning(
            "REDIS_URL not set. Using in-memory rate limiting (single-worker only)."
        )


def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    """Returns True if the request is allowed, False if rate limited.
    Uses Redis INCR+EXPIRE when available, falls back to in-memory."""
    from core.cache import redis_client

    if redis_client:
        try:
            window_key = int(time.time()) // window_seconds
            redis_key = f"{key}:{window_key}"
            current = redis_client.incr(redis_key)
            if current == 1:
                redis_client.expire(redis_key, window_seconds + 1)
            return current <= max_requests
        except Exception as e:
            logger.warning(f"Redis rate limit failed, falling back to in-memory: {e}")

    # In-memory fallback
    now = time.time()
    if key not in _rate_store:
        _rate_store[key] = []

    _rate_store[key] = [t for t in _rate_store[key] if now - t < window_seconds]

    if len(_rate_store[key]) >= max_requests:
        return False

    _rate_store[key].append(now)
    return True


def get_rate_limiter(times: int = 50, seconds: int = 60):
    """Returns a FastAPI dependency that enforces rate limiting."""

    async def _rate_limit_dependency(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}"

        if not _check_rate_limit(key, times, seconds):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {times} requests per {seconds} seconds.",
            )

    return Depends(_rate_limit_dependency)
