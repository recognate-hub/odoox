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
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL, decode_responses=True, socket_timeout=0.5
        )
        # Test connection
        redis_client.ping()
        logger.info("Connected to Redis for credential caching.")
    except Exception as e:
        logger.error(
            f"Failed to connect to Redis: {e}. Falling back to in-memory cache."
        )
        redis_client = None

from typing import TypeVar

T = TypeVar("T", bound=BaseModel)


def get_cached_workspace[T: BaseModel](token: str, cls: type[T]) -> T | None:
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

import functools
import hashlib
import json
from typing import Callable, Any

_in_memory_cache = {}

def cache_response(ttl_seconds: int = 300):
    """
    Decorator to cache the JSON-serializable response of an analytics function.
    Uses Redis if available, otherwise falls back to a simple in-memory dict.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # We skip caching if "self" is passed and it doesn't serialize easily,
            # so we'll just hash the class name + function name + all other args
            cache_key_parts = [func.__module__, func.__name__]
            
            # Serialize args (ignoring self if it's the first arg of a method)
            args_to_hash = args[1:] if len(args) > 0 and hasattr(args[0], '__class__') else args
            cache_key_parts.append(str(args_to_hash))
            cache_key_parts.append(str(kwargs))
            
            raw_key = "|".join(cache_key_parts)
            hashed_key = f"mcp_cache:{hashlib.md5(raw_key.encode()).hexdigest()}"
            
            # 1. Try Redis
            if redis_client:
                try:
                    cached_val = redis_client.get(hashed_key)
                    if cached_val:
                        logger.debug(f"Cache hit (Redis): {func.__name__}")
                        return json.loads(cached_val)
                except Exception as e:
                    logger.warning(f"Redis cache read failed: {e}")
            
            # 2. Try in-memory fallback
            else:
                import time
                if hashed_key in _in_memory_cache:
                    cached_time, cached_val = _in_memory_cache[hashed_key]
                    if time.time() - cached_time < ttl_seconds:
                        logger.debug(f"Cache hit (Memory): {func.__name__}")
                        return json.loads(cached_val)
            
            # 3. Execute function
            result = func(*args, **kwargs)
            
            # 4. Save to cache
            try:
                serialized = json.dumps(result)
                if redis_client:
                    redis_client.setex(hashed_key, ttl_seconds, serialized)
                else:
                    import time
                    _in_memory_cache[hashed_key] = (time.time(), serialized)
            except Exception as e:
                logger.warning(f"Failed to serialize/cache result for {func.__name__}: {e}")
                
            return result
        return wrapper
    return decorator
