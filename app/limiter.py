import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request, status
try:
    from redis.asyncio import Redis
except ImportError: Redis = None
from app.config import get_settings

local = defaultdict(deque)
async def enforce_rate_limit(request: Request, limit: int = 60, window: int = 60):
    key = f"rate:{request.client.host if request.client else 'unknown'}:{request.url.path}"
    try:
        redis = Redis.from_url(get_settings().redis_url, decode_responses=True)
        count = await redis.incr(key)
        if count == 1: await redis.expire(key, window)
        await redis.aclose()
    except Exception:
        now = time.monotonic(); bucket = local[key]
        while bucket and bucket[0] < now - window: bucket.popleft()
        bucket.append(now); count = len(bucket)
    if count > limit: raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded")

