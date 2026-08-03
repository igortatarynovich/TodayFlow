"""SQLAlchemy engine and session utilities."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from todayflow_backend.core.config import settings

_engine_kwargs: dict = {"echo": False, "future": True}
_db_url = settings.database_url
if _db_url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    # Один общий in-memory SQLite на процесс (pytest без файловой БД).
    if _db_url in ("sqlite://", "sqlite:///:memory:"):
        _engine_kwargs["poolclass"] = StaticPool
else:
    # Prewarm/LLM must not starve interactive requests (auth/me, practices).
    _engine_kwargs.update(
        {
            "pool_size": 12,
            "max_overflow": 18,
            "pool_timeout": 8,
            "pool_pre_ping": True,
            "pool_recycle": 1800,
        }
    )

engine = create_engine(_db_url, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
