import redis
from pydantic import BaseModel

from config.settings import get_settings
from core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Initialize synchronous Redis client for cache
redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=0.5)
        # Test connection
        redis_client.ping()
        logger.info("Connected to Redis for credential caching.")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}. Falling back to in-memory cache.")
        redis_client = None

from typing import TypeVar

T = TypeVar("T", bound=BaseModel)

def get_cached_workspace(token: str, cls: type[T]) -> T | None:
    if not redis_client:
        return None
    try:
        data = redis_client.get(f"workspace:{token}")
        if data:
            return cls.model_validate_json(data)
    except Exception as e:
        logger.warning(f"Redis get failed: {e}")
    return None

def set_cached_workspace(token: str, workspace: BaseModel, ttl: int = 300) -> None:
    if not redis_client:
        return
    try:
        redis_client.setex(f"workspace:{token}", ttl, workspace.model_dump_json())
    except Exception as e:
        logger.warning(f"Redis set failed: {e}")

def get_cached_value(key: str) -> str | None:
    if not redis_client:
        return None
    try:
        return redis_client.get(key)
    except Exception as e:
        logger.warning(f"Redis get_cached_value failed: {e}")
    return None

def set_cached_value(key: str, value: str, ttl: int = 3600) -> None:
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, value)
    except Exception as e:
        logger.warning(f"Redis set_cached_value failed: {e}")
