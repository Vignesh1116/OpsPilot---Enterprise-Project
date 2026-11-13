import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api_router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

# Initialize structured logging
logger = setup_logging()

app = FastAPI(
    title=f"{settings.PROJECT_NAME} – Enterprise Operations Platform",
    description="Backend API for OpsPilot – Asset Management, Work Orders, and Industrial Operations",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.DEBUG else None,
)

# Exception handlers
register_exception_handlers(app)

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Correlation ID and Request Timing Middleware
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-MS"] = str(process_time)

    # Log operational requests
    logger.info(
        "%s %s %d - %sms [req_id=%s]",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
        request_id,
    )
    return response


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs" if settings.DEBUG else "disabled in production",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Root"])
async def top_level_health():
    """Lightweight top-level liveness probe for container orchestrators."""
    return {"status": "ok"}
