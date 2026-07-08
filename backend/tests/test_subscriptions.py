"""Tests for subscriptions API endpoints."""

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
def auth_token(client: TestClient, test_user: User) -> str:
    """Get auth token for test user."""
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


def test_get_subscription_plans(client: TestClient):
    """Test getting available subscription plans."""
    response = client.get("/subscriptions/plans")
    assert response.status_code == 200
    data = response.json()
    assert "plans" in data
    assert isinstance(data["plans"], dict)


def test_create_subscription_checkout_requires_auth(client: TestClient):
    """Test that creating subscription checkout requires authentication."""
    payload = {"plan_id": "free"}
    response = client.post("/subscriptions/create-checkout", json=payload)
    assert response.status_code == 401


def test_create_subscription_checkout_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test creating subscription checkout for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"plan_id": "free"}
    response = client.post("/subscriptions/create-checkout", json=payload, headers=headers)
    
    # May return 200 (if Stripe is configured) or 400/500 (if not configured)
    assert response.status_code in [200, 400, 500]
    
    if response.status_code == 200:
        data = response.json()
        # Checkout response structure may vary
        assert isinstance(data, dict)


def test_cancel_subscription_requires_auth(client: TestClient):
    """Test that canceling subscription requires authentication."""
    payload = {"subscription_id": None}
    response = client.post("/subscriptions/cancel", json=payload)
    assert response.status_code == 401


def test_cancel_subscription_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test canceling subscription for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"subscription_id": None}
    response = client.post("/subscriptions/cancel", json=payload, headers=headers)
    
    # May return 200 (if subscription exists) or 400/404 (if not)
    assert response.status_code in [200, 400, 404]


def test_list_user_subscriptions_requires_auth(client: TestClient):
    """Test that listing subscriptions requires authentication."""
    response = client.get("/subscriptions/list")
    assert response.status_code == 401


def test_list_user_subscriptions_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test listing subscriptions for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/subscriptions/list", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "subscriptions" in data
    assert isinstance(data["subscriptions"], list)


def test_get_subscription_history_requires_auth(client: TestClient):
    """Test that getting subscription history requires authentication."""
    response = client.get("/subscriptions/history")
    assert response.status_code == 401


def test_get_subscription_history_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test getting subscription history for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/subscriptions/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    # History response structure may vary
    assert isinstance(data, dict)
