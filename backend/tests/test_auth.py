"""Tests for authentication endpoints."""

import pytest

from todayflow_backend.db import models as db_models


def test_signup(client, db_session, test_user_data):
    """Test user signup."""
    response = client.post("/auth/signup", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "email" in data
    assert "token" in data
    assert data["email"] == test_user_data["email"]
    
    # Verify user exists in database
    user = db_session.query(db_models.User).filter_by(email=test_user_data["email"]).first()
    assert user is not None
    assert user.email == test_user_data["email"]


def test_signup_duplicate_email(client, db_session, test_user_data):
    """Test signup with duplicate email."""
    # Create first user
    client.post("/auth/signup", json=test_user_data)
    
    # Try to create duplicate
    response = client.post("/auth/signup", json=test_user_data)
    assert response.status_code == 400


@pytest.mark.smoke
def test_login(client, db_session, test_user_data):
    """Test user login."""
    # Create user first
    client.post("/auth/signup", json=test_user_data)
    
    # Login
    response = client.post("/auth/login", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "email" in data
    assert "token" in data
    assert "is_paid" in data


def test_login_invalid_credentials(client, db_session, test_user_data):
    """Test login with invalid credentials."""
    # Create user
    client.post("/auth/signup", json=test_user_data)
    
    # Try to login with wrong password
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_get_current_user(client, db_session, test_user_data):
    """Test getting current user info."""
    # Signup and get token
    signup_response = client.post("/auth/signup", json=test_user_data)
    token = signup_response.json()["token"]
    
    # Get current user
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "email" in data
    assert "is_paid" in data
    assert "has_lite_report" in data
    assert "has_full_report" in data
    assert data.get("subscription_level") == "free"
    assert data.get("active_plan_id") is None
    assert data.get("subscription_status") is None
    assert data.get("insight_depth_tier") == "free"


def test_get_current_user_unauthorized(client):
    """Test getting current user without token."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_forgot_password_always_returns_success(client, db_session, test_user_data):
    """Forgot password should not reveal whether user exists."""
    client.post("/auth/signup", json=test_user_data)

    existing_response = client.post("/auth/forgot-password", json={"email": test_user_data["email"]})
    unknown_response = client.post("/auth/forgot-password", json={"email": "unknown@example.com"})

    assert existing_response.status_code == 200
    assert unknown_response.status_code == 200


def test_reset_password_with_token(client, db_session, test_user_data):
    """Reset password flow should issue token and allow login with new password."""
    client.post("/auth/signup", json=test_user_data)
    client.post("/auth/forgot-password", json={"email": test_user_data["email"]})

    user = db_session.query(db_models.User).filter_by(email=test_user_data["email"]).first()
    reset_token = (
        db_session.query(db_models.PasswordResetToken)
        .filter_by(user_id=user.id, used_at=None)
        .order_by(db_models.PasswordResetToken.created_at.desc())
        .first()
    )
    assert reset_token is not None

    new_password = "newpassword123"
    reset_response = client.post(
        "/auth/reset-password",
        json={"token": reset_token.token, "new_password": new_password},
    )
    assert reset_response.status_code == 200

    old_login = client.post("/auth/login", json=test_user_data)
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        json={"email": test_user_data["email"], "password": new_password},
    )
    assert new_login.status_code == 200


def test_oauth_providers_google_without_client(client, monkeypatch):
    from todayflow_backend.core import config as config_module

    s = config_module.Settings()
    s.google_client_id = None
    s.google_client_secret = None
    s.apple_client_id = None
    monkeypatch.setattr(config_module, "settings", s)

    import todayflow_backend.api.oauth as oauth_api

    monkeypatch.setattr(oauth_api, "settings", s)

    r = client.get("/oauth/providers")
    assert r.status_code == 200
    data = r.json()["providers"]
    assert data["google"]["enabled"] is False
    assert data["google"]["code_exchange_enabled"] is False


def test_oauth_providers_google_code_flag(client, monkeypatch):
    from todayflow_backend.core import config as config_module

    s = config_module.Settings()
    s.google_client_id = "g-client"
    s.google_client_secret = None
    monkeypatch.setattr(config_module, "settings", s)

    import todayflow_backend.api.oauth as oauth_api

    monkeypatch.setattr(oauth_api, "settings", s)

    r = client.get("/oauth/providers")
    assert r.json()["providers"]["google"]["code_exchange_enabled"] is False

    s2 = config_module.Settings()
    s2.google_client_id = "g-client"
    s2.google_client_secret = "secret"
    monkeypatch.setattr(config_module, "settings", s2)
    monkeypatch.setattr(oauth_api, "settings", s2)

    r2 = client.get("/oauth/providers")
    assert r2.json()["providers"]["google"]["code_exchange_enabled"] is True


def test_google_oauth_code_happy_path(client, monkeypatch):
    from todayflow_backend.core import config as config_module

    s = config_module.Settings()
    s.google_client_id = "g-client"
    s.google_client_secret = "secret"
    monkeypatch.setattr(config_module, "settings", s)

    import todayflow_backend.api.oauth as oauth_api

    monkeypatch.setattr(oauth_api, "settings", s)

    async def fake_exchange(_code: str, _redirect_uri: str) -> str:
        return "fake.id.token"

    monkeypatch.setattr(oauth_api, "_exchange_google_authorization_code", fake_exchange)
    monkeypatch.setattr(
        oauth_api,
        "_verify_google_id_token",
        lambda _t: {
            "email": "google_user@example.com",
            "sub": "sub-1",
            "iss": "https://accounts.google.com",
        },
    )

    r = client.post(
        "/oauth/google/code",
        json={"code": "auth-code", "redirect_uri": "http://localhost:3000/auth/google/callback"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "google_user@example.com"
    assert "token" in body

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['token']}"})
    assert me.status_code == 200
