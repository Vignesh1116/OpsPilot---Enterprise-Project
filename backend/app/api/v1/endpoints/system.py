import time
from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.api.deps import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Perform system health check")
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Health check verifying FastAPI, database, and Redis connectivity."""
    start_time = time.perf_counter()

    # 1. Database Check
    db_status = "unhealthy"
    db_latency_ms = None
    try:
        db_start = time.perf_counter()
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_status = "healthy"
            db_latency_ms = round((time.perf_counter() - db_start) * 1000, 2)
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # 2. Redis Check
    redis_status = "unhealthy"
    redis_latency_ms = None
    try:
        redis_start = time.perf_counter()
        r = aioredis.from_url(settings.REDIS_URL, socket_timeout=1.0)
        pong = await r.ping()
        await r.aclose()
        if pong:
            redis_status = "healthy"
            redis_latency_ms = round((time.perf_counter() - redis_start) * 1000, 2)
    except Exception:
        # If redis is not running in local offline dev mode, provide graceful info
        redis_status = "disconnected"

    total_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    overall_status = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_latency_ms": total_latency_ms,
        "components": {
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
            },
            "redis": {
                "status": redis_status,
                "latency_ms": redis_latency_ms,
            },
        },
        "enterprise_context": {
            "organization": settings.DEMO_COMPANY_NAME,
            "headquarters": f"{settings.DEMO_HQ_CITY}, {settings.DEMO_HQ_STATE}",
        },
    }
