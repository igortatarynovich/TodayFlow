"""Pytest configuration and fixtures."""

from __future__ import annotations

import importlib
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

# До импорта приложения: общий URL БД и флаг, чтобы startup не гнал SQL-миграции
# поверх схемы, которую между тестами сбрасывают через metadata.drop_all.
# Общая in-memory SQLite на процесс (StaticPool в session.py): без файла и прав на диск.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["TODAYFLOW_PYTEST"] = "1"
# Тот же astro, что в `backend/.env.example`; CI/локально можно переопределить. Без сервиса на :8081 synastry-тесты не дойдут до ассертов.
if "ASTRO_SERVICE_URL" not in os.environ:
    os.environ["ASTRO_SERVICE_URL"] = "http://127.0.0.1:8081"

from todayflow_backend.db.models import Base
from todayflow_backend.main import app
from todayflow_backend.db.session import engine, get_session
from todayflow_backend.services.astro import get_astro_service

from tests.support.fake_astro_service import FakeAstroServiceForTests

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

# Модули с ``from todayflow_backend.db.session import SessionLocal`` на уровне файла.
_SESSION_LOCAL_CONSUMER_MODULES = (
    "todayflow_backend.services.numerology",
    "todayflow_backend.services.tarot",
    "todayflow_backend.services.library",
    "todayflow_backend.services.full_reports",
    "todayflow_backend.services.thematic_reports",
    "todayflow_backend.services.lite_reports",
    "todayflow_backend.services.subscriptions",
    "todayflow_backend.services.payments",
    "todayflow_backend.core.ai_client",
)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override.

    Сервисы, которые открывают собственные сессии через ``SessionLocal()`` (таро,
    нумерология и т.д.), должны попадать в **тот же** engine, что и override
    ``get_session`` — иначе данные уезжают в ``settings.database_url``, а роуты
    видят только ``db_session`` из этого фикстуры.
    """
    import todayflow_backend.db.session as db_session_pkg

    test_engine = db_session.get_bind()
    saved_engine = db_session_pkg.engine
    saved_session_local = db_session_pkg.SessionLocal
    db_session_pkg.engine = test_engine
    new_local = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False
    )
    db_session_pkg.SessionLocal = new_local

    saved_consumer_locals: dict[str, object] = {}
    for mod_name in _SESSION_LOCAL_CONSUMER_MODULES:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "SessionLocal"):
            saved_consumer_locals[mod_name] = mod.SessionLocal
            mod.SessionLocal = new_local

    def override_get_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_astro_service] = lambda: FakeAstroServiceForTests()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        db_session_pkg.engine = saved_engine
        db_session_pkg.SessionLocal = saved_session_local
        for mod_name, prev in saved_consumer_locals.items():
            mod = importlib.import_module(mod_name)
            mod.SessionLocal = prev


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


def login_bearer_token(client: TestClient, email: str, password: str) -> str:
    """POST /auth/login returns `token` (legacy `access_token` не используется в API)."""
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    data = response.json()
    token = data.get("token") or data.get("access_token")
    assert token, data
    return str(token)
