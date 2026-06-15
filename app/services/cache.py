import json
import time
from collections.abc import Awaitable, Callable
from typing import Any
from redis.asyncio import Redis
from app.core.config import get_settings

_memory: dict[str, tuple[float, Any]] = {}
_redis: Redis | None = None


async def get_cached(key: str, factory: Callable[[], Awaitable[Any]], ttl: int | None = None) -> Any:
    settings = get_settings()
    ttl = ttl or settings.cache_ttl_seconds
    global _redis
    if settings.redis_url and _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    if _redis:
        cached = await _redis.get(key)
        if cached:
            return json.loads(cached)
        value = await factory()
        await _redis.setex(key, ttl, json.dumps(value, default=str))
        return value
    expires, value = _memory.get(key, (0, None))
    if expires > time.time():
        return value
    value = await factory()
    _memory[key] = (time.time() + ttl, value)
    return value
