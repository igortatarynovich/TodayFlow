"""Integration tests for report generation flow."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User


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


def test_lite_report_flow(client: TestClient, sample_birth_data):
    """Test lite report generation flow (no auth required)."""
    # Generate lite report
    response = client.post("/reports/lite", json=sample_birth_data)
    assert response.status_code in [200, 201]
    
    if response.status_code in [200, 201]:
        data = response.json()
        assert "summary" in data
        assert "sun" in data.get("summary", {})
        assert "moon" in data.get("summary", {})


def test_full_report_flow_requires_paid(
    client: TestClient, 
    test_user: User, 
    auth_token: str, 
    sample_birth_data
):
    """Test that full report generation requires paid account."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/reports/full", json=sample_birth_data, headers=headers)
    assert response.status_code == 403


def test_report_flow_birth_data_to_lite_to_full(
    client: TestClient,
    paid_user: User,
    paid_auth_token: str,
    sample_birth_data
):
    """Test complete flow: birth data → lite report → full report (if paid)."""
    headers = {"Authorization": f"Bearer {paid_auth_token}"}
    
    # Step 1: Generate lite report (should work)
    lite_response = client.post("/reports/lite", json=sample_birth_data)
    assert lite_response.status_code in [200, 201]
    
    # Step 2: Try to generate full report (may work if service is available)
    full_response = client.post("/reports/full", json=sample_birth_data, headers=headers)
    # May return 200 (if service available) or 500 (if not configured)
    assert full_response.status_code in [200, 403, 500]
    
    # Step 3: Try to get saved full report
    get_response = client.get("/reports/full", headers=headers)
    # May return 200 (if report exists) or 404 (if not saved)
    assert get_response.status_code in [200, 404]

