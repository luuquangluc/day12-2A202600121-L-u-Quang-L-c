import time
import logging
from datetime import datetime
from fastapi import HTTPException
import redis
from app.config import settings

logger = logging.getLogger(__name__)

r = redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None

def check_and_record_cost(user_id: str, input_tokens: int, output_tokens: int):
    # Free API call count as tiny cost for demonstration
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    
    if not r:
        return cost  # Skip if no redis configured
        
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(r.get(key) or 0)
    
    if current + cost > settings.daily_budget_usd:
        logger.error(f"BUDGET EXCEEDED for {user_id}: ${current:.4f}")
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Monthly budget exceeded",
                "used_usd": current,
                "budget_usd": settings.daily_budget_usd,
                "resets_at": "start of next month"
            }
        )
        
    if cost > 0:
        new_total = r.incrbyfloat(key, cost)
        r.expire(key, 32 * 24 * 3600)  # 32 days
        return new_total
    
    return current
