"""FastAPI entrypoint for TodayFlow backend."""

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from todayflow_backend.api.routes import router
from todayflow_backend.core.config import settings
from todayflow_backend.core.logging_config import setup_logging
from todayflow_backend.core.monitoring import capture_exception, init_monitoring
from todayflow_backend.core.rate_limit import limiter
from todayflow_backend.db.models import Base
from todayflow_backend.db.session import engine
from todayflow_backend.db.migrations import apply_migrations

# Setup logging
setup_logging()

# Initialize monitoring (Sentry) if configured
init_monitoring()

app = FastAPI(
    title="TodayFlow Backend API",
    version=settings.narrative_model_version,
    description="Core API that orchestrates chart calculations and report assembly.",
    redirect_slashes=False,  # Отключаем автоматический redirect для trailing slash
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Personalized responses must never be shared via CDN/proxy caches.
_PERSONALIZED_PREFIXES = (
    "/today",
    "/account",
    "/natal-chart",
    "/morning-ritual",
    "/tracking",
    "/meaning",
    "/auth/me",
    "/day-symbols",
)


@app.middleware("http")
async def personalize_cache_control(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path or ""
    auth = request.headers.get("authorization") or ""
    cookie = request.headers.get("cookie") or ""
    is_personalized = any(path == p or path.startswith(p + "/") for p in _PERSONALIZED_PREFIXES)
    has_credentials = auth.lower().startswith("bearer ") or bool(cookie.strip())
    if is_personalized or has_credentials:
        response.headers["Cache-Control"] = "private, no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
        vary = response.headers.get("Vary")
        extra = "Authorization, Cookie, Accept-Language"
        response.headers["Vary"] = f"{vary}, {extra}" if vary else extra
    return response

app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


# Обработка ошибок с CORS заголовками
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Обработка HTTP исключений с CORS заголовками."""
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    # Добавляем CORS заголовки
    origin = request.headers.get("origin")
    if origin in settings.allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработка ошибок валидации с CORS заголовками."""
    response = JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )
    origin = request.headers.get("origin")
    if origin in settings.allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработка общих исключений с CORS заголовками."""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    capture_exception(exc, context={"path": str(request.url.path), "method": request.method})
    
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
    origin = request.headers.get("origin")
    if origin in settings.allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.on_event("startup")
def create_tables() -> None:
    """Create tables from models and apply SQL migrations."""
    # First, create tables from SQLAlchemy models
    Base.metadata.create_all(bind=engine)

    # Pytest пересоздаёт схему через metadata между тестами; повторный прогон .sql
    # миграций после drop_all даёт конфликты на SQLite. В CI без Postgres миграции не нужны.
    if os.getenv("TODAYFLOW_PYTEST") == "1":
        return

    # Then, apply SQL migrations
    try:
        apply_migrations(engine)
    except Exception as e:
        # Log error but don't crash the app - migrations might fail if tables already exist
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error applying migrations: {e}", exc_info=True)
