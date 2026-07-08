"""Tests for admin API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user (non-admin)."""
    from todayflow_backend.services.auth import hash_password
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        is_admin=False,
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create an admin test user."""
    from todayflow_backend.services.auth import hash_password
    user = User(
        email="admin@example.com",
        password_hash=hash_password("adminpassword123"),
        is_admin=True,
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


@pytest.fixture
def admin_token(client: TestClient, admin_user: User) -> str:
    """Get auth token for admin user."""
    response = client.post(
        "/auth/login",
        json={"email": admin_user.email, "password": "adminpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


def test_list_paragraphs_requires_auth(client: TestClient):
    """Test that listing paragraphs requires authentication."""
    response = client.get("/admin/paragraphs")
    assert response.status_code == 401


def test_list_paragraphs_requires_admin(client: TestClient, test_user: User, auth_token: str):
    """Test that listing paragraphs requires admin access."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/admin/paragraphs", headers=headers)
    assert response.status_code == 403


def test_list_paragraphs_admin(client: TestClient, admin_user: User, admin_token: str):
    """Test listing paragraphs for admin user."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/paragraphs", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_paragraph_requires_auth(client: TestClient):
    """Test that getting paragraph requires authentication."""
    response = client.get("/admin/paragraphs/EP-A1-BASE-001")
    assert response.status_code == 401


def test_get_paragraph_requires_admin(client: TestClient, test_user: User, auth_token: str):
    """Test that getting paragraph requires admin access."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/admin/paragraphs/EP-A1-BASE-001", headers=headers)
    assert response.status_code == 403


def test_get_paragraph_admin(client: TestClient, admin_user: User, admin_token: str):
    """Test getting paragraph for admin user."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/paragraphs/EP-A1-BASE-001", headers=headers)
    # May return 200 (if paragraph exists) or 404 (if not found)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)


def test_toggle_paragraph_requires_auth(client: TestClient):
    """Test that toggling paragraph requires authentication."""
    payload = {"lite_enabled": True}
    response = client.post("/admin/paragraphs/EP-A1-BASE-001/toggle", json=payload)
    assert response.status_code == 401


def test_toggle_paragraph_requires_admin(client: TestClient, test_user: User, auth_token: str):
    """Test that toggling paragraph requires admin access."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"lite_enabled": True}
    response = client.post("/admin/paragraphs/EP-A1-BASE-001/toggle", json=payload, headers=headers)
    assert response.status_code == 403


def test_update_variant_text_requires_auth(client: TestClient):
    """Test that updating variant text requires authentication."""
    payload = {"text": "New text"}
    response = client.post("/admin/paragraphs/EP-A1-BASE-001/variants/v1", json=payload)
    assert response.status_code == 401


def test_update_variant_text_requires_admin(client: TestClient, test_user: User, auth_token: str):
    """Test that updating variant text requires admin access."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"text": "New text"}
    response = client.post("/admin/paragraphs/EP-A1-BASE-001/variants/v1", json=payload, headers=headers)
    assert response.status_code == 403


def test_audit_logs_requires_auth(client: TestClient):
    """Test that getting audit logs requires authentication."""
    response = client.get("/admin/paragraphs/audit")
    assert response.status_code == 401


def test_audit_logs_requires_admin(client: TestClient, test_user: User, auth_token: str):
    """Test that getting audit logs requires admin access."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/admin/paragraphs/audit", headers=headers)
    assert response.status_code == 403


def test_audit_logs_admin(client: TestClient, admin_user: User, admin_token: str):
    """Test getting audit logs for admin user."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/paragraphs/audit", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_tarot_reminders_due_requires_auth(client: TestClient):
    """Test that getting due tarot reminders requires authentication."""
    response = client.get("/admin/tarot/reminders/due")
    assert response.status_code == 401


def test_get_tarot_reminders_due_requires_admin(client: TestClient, test_user: User, auth_token: str):
    """Test that getting due tarot reminders requires admin access."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/admin/tarot/reminders/due", headers=headers)
    assert response.status_code == 403


def test_get_tarot_reminders_due_admin(client: TestClient, admin_user: User, admin_token: str):
    """Test getting due tarot reminders for admin user."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/tarot/reminders/due", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_mark_tarot_reminder_sent_requires_auth(client: TestClient):
    """Test that marking tarot reminder as sent requires authentication."""
    response = client.post("/admin/tarot/reminders/1/sent")
    assert response.status_code == 401


def test_mark_tarot_reminder_sent_requires_admin(client: TestClient, test_user: User, auth_token: str):
    """Test that marking tarot reminder as sent requires admin access."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/admin/tarot/reminders/1/sent", headers=headers)
    assert response.status_code == 403

