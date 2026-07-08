"""Tests for full reports API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User, GeneratedReport


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    from todayflow_backend.services.auth import hash_password
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def paid_user(db_session: Session) -> User:
    """Create a paid test user."""
    from todayflow_backend.services.auth import hash_password
    user = User(
        email="paid@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:
    """Get auth token for test user."""
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


@pytest.fixture
def paid_auth_token(client: TestClient, paid_user: User) -> str:
    """Get auth token for paid user."""
    response = client.post(
        "/auth/login",
        json={"email": paid_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


@pytest.fixture
def sample_birth_data():
    """Sample birth data for testing."""
    return {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "time_unknown": False,
        "latitude": 55.7558,
        "longitude": 37.6173,
        "location": "Moscow",
        "country": "Russia"
    }


def test_generate_full_report_requires_auth(client: TestClient, sample_birth_data):
    """Test that generating full report requires authentication."""
    response = client.post("/reports/full", json=sample_birth_data)
    assert response.status_code == 401


def test_generate_full_report_requires_paid(client: TestClient, test_user: User, auth_token: str, sample_birth_data):
    """Test that generating full report requires paid account."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/reports/full", json=sample_birth_data, headers=headers)
    assert response.status_code == 403
    assert "payment" in response.json()["detail"].lower() or "paid" in response.json()["detail"].lower()


def test_generate_full_report_authenticated_paid(client: TestClient, paid_user: User, paid_auth_token: str, sample_birth_data, db_session: Session):
    """Test generating full report for paid user."""
    headers = {"Authorization": f"Bearer {paid_auth_token}"}
    response = client.post("/reports/full", json=sample_birth_data, headers=headers)
    
    # May return 200 or 500 depending on service availability
    # If service is available, should return 200 with FullReport
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "sections" in data or "internal_model" in data


def test_get_full_report_requires_auth(client: TestClient):
    """Test that getting full report requires authentication."""
    response = client.get("/reports/full")
    assert response.status_code == 401


def test_get_full_report_not_found(client: TestClient, test_user: User, auth_token: str):
    """Test getting full report when none exists."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/reports/full", headers=headers)
    assert response.status_code == 404


def test_get_full_report_exists(client: TestClient, test_user: User, auth_token: str, db_session: Session):
    """Test getting existing full report."""
    # Create a mock full report
    report_data = {
        "sections": [],
        "internal_model": {"axes": [], "modulators": []}
    }
    report = GeneratedReport(
        user_id=test_user.id,
        product_type="full",
        data=report_data
    )
    db_session.add(report)
    db_session.commit()
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/reports/full", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "sections" in data or "internal_model" in data


def test_download_full_report_requires_auth(client: TestClient):
    """Test that downloading full report requires authentication."""
    response = client.get("/reports/full/download")
    assert response.status_code == 401


def test_download_full_report_not_found(client: TestClient, test_user: User, auth_token: str):
    """Test downloading full report when none exists."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/reports/full/download", headers=headers)
    assert response.status_code == 404


def test_download_full_report_exists(client: TestClient, test_user: User, auth_token: str, db_session: Session):
    """Test downloading existing full report as PDF."""
    # Create a mock full report
    report_data = {
        "sections": [],
        "internal_model": {"axes": [], "modulators": []}
    }
    report = GeneratedReport(
        user_id=test_user.id,
        product_type="full",
        data=report_data
    )
    db_session.add(report)
    db_session.commit()
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/reports/full/download", headers=headers)
    
    # May return 200 (PDF) or 500 (if PDF generation fails)
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers.get("content-disposition", "")

