"""
Production AI Café Recommendation Agent
"""
import os
import time
import signal
import logging
import json
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import redis

from app.config import settings
from app.auth import verify_api_key
from app.rate_limiter import check_rate_limit
from app.cost_guard import check_and_record_cost
from app.cafe import get_cafe_info

# ─────────────────────────────────────────────────────────
# Logging — JSON structured
# ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False
_request_count = 0
_error_count = 0

r = redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None

# ─────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info(json.dumps({
        "event": "startup",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }))
    await asyncio.sleep(0.1)  # dùng sleep bất đồng bộ
    # Không block startup bằng lệnh ping, để app khởi động nhanh nhất có thể
    _is_ready = True
    logger.info(json.dumps({"event": "ready"}))

    yield

    _is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))
    if r:
        r.close()

# ─────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    global _request_count, _error_count
    start = time.time()
    _request_count += 1
    try:
        response: Response = await call_next(request)
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        if "server" in response.headers:
            del response.headers["server"]
        duration = round((time.time() - start) * 1000, 1)
        logger.info(json.dumps({
            "event": "request",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "ms": duration,
        }))
        return response
    except Exception as e:
        _error_count += 1
        raise

# ─────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    city: str = Field(..., min_length=2, max_length=100, description="Tên thành phố bạn muốn tìm quán cafe")

class AskResponse(BaseModel):
    question: str
    answer: str
    timestamp: str
    history: list[str] = []

# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "ask": "POST /ask (requires X-API-Key)",
            "health": "GET /health",
            "ready": "GET /ready",
        },
    }

@app.post("/ask", response_model=AskResponse, tags=["Café Agent"])
async def ask_agent(
    body: AskRequest,
    request: Request,
    _key: str = Depends(verify_api_key),
):
    user_id = _key[:8]
    # Rate limit per API key
    check_rate_limit(user_id)

    # Budget check (Mock token calculation)
    input_tokens = len(body.city.split()) * 2
    check_and_record_cost(user_id, input_tokens, 0)

    logger.info(json.dumps({
        "event": "cafe_query_call",
        "city": body.city,
        "client": str(request.client.host) if request.client else "unknown",
    }))

    answer = await get_cafe_info(body.city)

    output_tokens = len(answer.split()) * 2
    check_and_record_cost(user_id, 0, output_tokens)
    
    history = []
    # Save conversation state in Redis
    if r:
        hist_key = f"history:{user_id}"
        r.rpush(hist_key, f"Q: Tìm quán cafe tại {body.city}")
        r.rpush(hist_key, f"A: {answer}")
        r.ltrim(hist_key, -10, -1) # Keep last 10 messages
        r.expire(hist_key, 3600 * 24) # 1 day TTL
        history = r.lrange(hist_key, 0, -1)

    return AskResponse(
        question=f"Quán cafe nào ngon ở {body.city}?",
        answer=answer,
        timestamp=datetime.now(timezone.utc).isoformat(),
        history=history
    )

@app.get("/health", tags=["Operations"])
def health():
    status = "ok"
    return {
        "status": status,
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }

@app.get("/ready", tags=["Operations"])
def ready():
    if not _is_ready:
        raise HTTPException(503, "Not ready")
    return {"ready": True}


# ─────────────────────────────────────────────────────────
# Graceful Shutdown
# ─────────────────────────────────────────────────────────
def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))

signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)

if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        timeout_graceful_shutdown=30,
    )
