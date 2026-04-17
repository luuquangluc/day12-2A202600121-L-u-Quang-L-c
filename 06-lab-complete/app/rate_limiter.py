import time
from fastapi import HTTPException
import redis
from app.config import settings

r = redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None

def check_rate_limit(user_id: str):
    if not r:
        return # Skip if no redis configured
        
    now = int(time.time())
    window_start = now - 60
    key = f"rate_limit:{user_id}"
    
    # Remove older entries
    r.zremrangebyscore(key, 0, window_start)
    
    # Get current count
    count = r.zcard(key)
    
    if count >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": "60"},
        )
        
    r.zadd(key, {str(now): now})
    r.expire(key, 60)
