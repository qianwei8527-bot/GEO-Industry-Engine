"""V10.6-R1.1 atomic intake rate limiting.

Redis is preferred for cross-process atomic windows. When Redis is
unavailable, an in-process asyncio lock provides atomic local fallback so
local development and tests keep the same 429 semantics.
"""

import asyncio
import os
import time
from collections import defaultdict, deque
from functools import lru_cache
from typing import Deque, Dict

from app.core.config import settings

INTAKE_RATE_LIMITS = {
    "context": (60, 60),
    "draft": (10, 3600),
    "submit": (5, 3600),
}


class RateLimitBackendUnavailable(Exception):
    pass


class MemoryRateLimitBackend:
    def __init__(self):
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        async with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] <= now - window_seconds:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True


class RedisRateLimitBackend:
    def __init__(self):
        import redis.asyncio as aioredis
        self.client = aioredis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=0.4,
            socket_timeout=0.6,
        )

    async def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        script = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""
        count = await self.client.eval(script, 1, key, window_seconds)
        return int(count) <= limit


class ResilientRateLimitBackend:
    def __init__(self):
        self.memory = MemoryRateLimitBackend()
        self.redis: RedisRateLimitBackend | None = None
        self._use_redis = True

    async def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        if self._use_redis:
            try:
                if self.redis is None:
                    self.redis = RedisRateLimitBackend()
                return await self.redis.allow(key, limit, window_seconds)
            except Exception:
                if os.getenv("APP_ENV", "development").lower() == "production":
                    raise RateLimitBackendUnavailable("Redis rate limiter unavailable in production")
                self._use_redis = False
        return await self.memory.allow(key, limit, window_seconds)


class IntakeRateLimiter:
    def __init__(self, backend=None):
        self.backend = backend or ResilientRateLimitBackend()

    async def _deny(self):
        from app.services.intake_service import IntakeRateLimitError
        raise IntakeRateLimitError()

    async def check_ip(
        self,
        scope: str,
        client_ip: str,
        limit: int,
        window_seconds: int,
    ):
        key = f"intake:{scope}:ip:{client_ip or 'unknown'}"
        if not await self.backend.allow(key, limit, window_seconds):
            await self._deny()

    async def check_token(
        self,
        scope: str,
        token_id: str,
        limit: int,
        window_seconds: int,
    ):
        key = f"intake:{scope}:token:{token_id}"
        if not await self.backend.allow(key, limit, window_seconds):
            await self._deny()

    async def check(
        self,
        scope: str,
        token_id: str,
        client_ip: str,
        limit: int,
        window_seconds: int,
    ):
        await self.check_ip(scope, client_ip, limit, window_seconds)
        await self.check_token(scope, token_id, limit, window_seconds)


@lru_cache()
def get_intake_rate_limiter():
    return IntakeRateLimiter()
