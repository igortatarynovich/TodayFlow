"""Integration tests for authentication flow."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User


def test_full_auth_flow_signup_login_protected_route(client: TestClient, db_session: Session):
    """Test complete auth flow: signup → login → access protected route."""
    # Step 1: Signup
    signup_payload = {
        "email": "newuser@example.com",
        "password": "securepassword123"
    }
    signup_response = client.post("/auth/signup", json=signup_payload)
    assert signup_response.status_code == 200
    signup_data = signup_response.json()
    assert "token" in signup_data
    assert "user_id" in signup_data
    assert signup_data["email"] == "newuser@example.com"
    
    token = signup_data["token"]
    
    # Step 2: Login
    login_payload = {
        "email": "newuser@example.com",
        "password": "securepassword123"
    }
    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "token" in login_data
    login_token = login_data["token"]
    
    # Step 3: Access protected route (account profile)
    headers = {"Authorization": f"Bearer {login_token}"}
    profile_response = client.get("/account/profile", headers=headers)
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["email"] == "newuser@example.com"


def test_auth_flow_invalid_credentials(client: TestClient, db_session: Session):
    """Test auth flow with invalid credentials."""
    # Try to login with non-existent user
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 401


def test_auth_flow_protected_route_without_token(client: TestClient):
    """Test that protected routes require authentication."""
    # Try to access protected route without token
    profile_response = client.get("/account/profile")
    assert profile_response.status_code == 401


def test_auth_flow_duplicate_signup(client: TestClient, db_session: Session):
    """Test that duplicate signup is rejected."""
    # First signup
    signup_payload = {
        "email": "duplicate@example.com",
        "password": "password123"
    }
    first_response = client.post("/auth/signup", json=signup_payload)
    assert first_response.status_code == 200
    
    # Try to signup again with same email
    second_response = client.post("/auth/signup", json=signup_payload)
    assert second_response.status_code == 400

