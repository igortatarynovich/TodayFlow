"""Tests for challenges API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.main import app
from todayflow_backend.db.models import User, Challenge, ChallengeParticipant
from todayflow_backend.services.auth import hash_password

client = TestClient(app)


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
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
def pro_user(db_session: Session) -> User:
    """Create a Pro test user."""
    user = User(
        email="pro@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=True,
        subscription_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Get auth token for test user."""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def pro_auth_token(pro_user: User) -> str:
    """Get auth token for Pro user."""
    response = client.post(
        "/auth/login",
        json={"email": "pro@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def test_challenge(db_session: Session) -> Challenge:
    """Create a test challenge."""
    challenge = Challenge(
        id="test-challenge",
        title="Test Challenge",
        description="Test description",
        duration=7,
        goal="Test goal",
        price=99000,  # 990 rubles in cents
        is_pro_only=False,
        icon="🎯",
        is_active=True,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


@pytest.fixture
def pro_challenge(db_session) -> Challenge:
    """Create a Pro-only challenge."""
    challenge = Challenge(
        id="pro-challenge",
        title="Pro Challenge",
        description="Pro description",
        duration=14,
        goal="Pro goal",
        price=None,
        is_pro_only=True,
        icon="💎",
        is_active=True,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


def test_get_challenges_empty(client):
    """Test getting empty challenges list (no auth required)."""
    response = client.get("/challenges")
    assert response.status_code == 200
    assert response.json() == []


def test_get_challenges_with_challenge(client, test_challenge):
    """Test getting challenges list."""
    response = client.get("/challenges")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "test-challenge"
    assert data[0]["title"] == "Test Challenge"


def test_get_challenges_filters_pro_only(client, auth_token, test_challenge, pro_challenge):
    """Test that non-Pro users don't see Pro-only challenges."""
    response = client.get(
        "/challenges",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    # Should only see non-Pro challenge
    assert len(data) == 1
    assert data[0]["id"] == "test-challenge"


def test_get_challenges_pro_user_sees_all(client, pro_auth_token, test_challenge, pro_challenge):
    """Test that Pro users see all challenges."""
    response = client.get(
        "/challenges",
        headers={"Authorization": f"Bearer {pro_auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_challenge_by_id(client, test_challenge):
    """Test getting a specific challenge."""
    response = client.get("/challenges/test-challenge")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-challenge"
    assert data["title"] == "Test Challenge"


def test_get_challenge_not_found(client):
    """Test getting non-existent challenge."""
    response = client.get("/challenges/non-existent")
    assert response.status_code == 404


def test_get_pro_challenge_requires_pro(client, auth_token, pro_challenge):
    """Test that non-Pro users cannot access Pro-only challenge."""
    response = client.get(
        "/challenges/pro-challenge",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 403


def test_get_pro_challenge_allowed(client, pro_auth_token, pro_challenge):
    """Test that Pro users can access Pro-only challenge."""
    response = client.get(
        "/challenges/pro-challenge",
        headers={"Authorization": f"Bearer {pro_auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "pro-challenge"


def test_join_challenge(client, auth_token, test_challenge):
    """Test joining a challenge."""
    response = client.post(
        "/challenges/test-challenge/join",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["challenge_id"] == "test-challenge"
    assert data["current_day"] == 1
    assert data["is_active"] is True


def test_join_challenge_requires_auth(client, test_challenge):
    """Test that joining requires authentication."""
    response = client.post("/challenges/test-challenge/join")
    assert response.status_code == 401 or response.status_code == 403


def test_join_pro_challenge_requires_pro(client, auth_token, pro_challenge):
    """Test that joining Pro-only challenge requires Pro subscription."""
    response = client.post(
        "/challenges/pro-challenge/join",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 403


def test_join_pro_challenge_allowed(client, pro_auth_token, pro_challenge):
    """Test that Pro users can join Pro-only challenge."""
    response = client.post(
        "/challenges/pro-challenge/join",
        headers={"Authorization": f"Bearer {pro_auth_token}"},
    )
    assert response.status_code == 201


def test_join_challenge_duplicate(client, auth_token, test_challenge, db_session):
    """Test that joining same challenge twice returns error."""
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    
    # Join first time
    response1 = client.post(
        "/challenges/test-challenge/join",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response1.status_code == 201

    # Try to join again
    response2 = client.post(
        "/challenges/test-challenge/join",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response2.status_code == 400


def test_get_my_participations(client, auth_token, test_challenge):
    """Test getting user's challenge participations."""
    # Join a challenge first
    client.post(
        "/challenges/test-challenge/join",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Get participations
    response = client.get(
        "/challenges/my/participations",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["challenge_id"] == "test-challenge"


def test_get_my_participations_empty(client, auth_token):
    """Test getting empty participations list."""
    response = client.get(
        "/challenges/my/participations",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_leave_challenge(client, auth_token, test_challenge, db_session):
    """Test leaving a challenge."""
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    
    # Join first
    client.post(
        "/challenges/test-challenge/join",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Leave
    response = client.post(
        "/challenges/test-challenge/leave",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204

    # Verify participation is deactivated
    participation = db_session.query(ChallengeParticipant).filter(
        ChallengeParticipant.user_id == user.id,
        ChallengeParticipant.challenge_id == "test-challenge"
    ).first()
    assert participation is not None
    assert participation.is_active is False


def test_leave_challenge_not_found(client, auth_token):
    """Test leaving a challenge user hasn't joined."""
    response = client.post(
        "/challenges/non-existent/leave",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404

