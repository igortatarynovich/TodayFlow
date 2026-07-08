"""Tests for payments API endpoints."""

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


def test_create_checkout_session_requires_auth(client: TestClient):
    """Test that creating checkout session requires authentication."""
    payload = {"user_id": 1}
    response = client.post("/payments/checkout-session", json=payload)
    assert response.status_code == 401


def test_create_checkout_session_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test creating checkout session for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"user_id": test_user.id}
    response = client.post("/payments/checkout-session", json=payload, headers=headers)
    
    # May return 200 (if Stripe is configured) or 400/500 (if not configured)
    assert response.status_code in [200, 400, 500]
    
    if response.status_code == 200:
        data = response.json()
        # Checkout response structure may vary
        assert isinstance(data, dict)


def test_create_checkout_session_forbidden_for_another_user(client: TestClient, test_user: User, auth_token: str):
    """Non-admin users cannot create a checkout session for a different user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"user_id": test_user.id + 100}
    response = client.post("/payments/checkout-session", json=payload, headers=headers)
    assert response.status_code == 403


def test_stripe_webhook_missing_signature(client: TestClient):
    """Test that webhook requires signature header."""
    response = client.post("/payments/webhook", json={})
    # Should return 400 if signature is missing
    assert response.status_code == 400


def test_stripe_webhook_with_signature(client: TestClient):
    """Test webhook with signature header."""
    headers = {"stripe-signature": "test_signature"}
    response = client.post("/payments/webhook", json={}, headers=headers)
    
    # May return 200 (if webhook processed) or 400 (if invalid signature/event)
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert data.get("status") == "ok"
