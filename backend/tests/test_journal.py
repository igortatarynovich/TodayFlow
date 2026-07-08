"""Tests for journal API endpoints."""

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User, JournalEntry


@pytest.fixture
def auth_token(client, db_session, test_user_data):
    """Get auth token for test user."""
    # Create user first
    client.post("/auth/signup", json=test_user_data)
    
    # Login and get token
    response = client.post("/auth/login", json=test_user_data)
    assert response.status_code == 200
    return response.json()["token"]


def test_get_journal_entries_empty(client, auth_token):
    """Test getting empty journal entries list."""
    response = client.get(
        "/journal/entries",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_create_journal_entry_wish(client, auth_token):
    """Test creating a wish journal entry."""
    response = client.post(
        "/journal/entries",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "type": "wish",
            "content": "Хочу научиться медитировать",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "wish"
    assert data["content"] == "Хочу научиться медитировать"
    assert "id" in data
    assert "created_at" in data


def test_create_journal_entry_gratitude(client, auth_token):
    """Test creating a gratitude journal entry."""
    response = client.post(
        "/journal/entries",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "type": "gratitude",
            "content": "Благодарен за сегодняшний день",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "gratitude"
    assert data["content"] == "Благодарен за сегодняшний день"


def test_create_journal_entry_invalid_type(client, auth_token):
    """Test creating journal entry with invalid type."""
    response = client.post(
        "/journal/entries",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "type": "invalid",
            "content": "Some content",
        },
    )
    assert response.status_code == 400


def test_create_journal_entry_empty_content(client, auth_token):
    """Test creating journal entry with empty content."""
    response = client.post(
        "/journal/entries",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "type": "wish",
            "content": "",
        },
    )
    assert response.status_code == 400


def test_get_journal_entries_by_type(client, auth_token, db_session):
    """Test getting journal entries filtered by type."""
    # Create test entries
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    entry1 = JournalEntry(
        user_id=user.id,
        type="wish",
        content="Wish 1",
    )
    entry2 = JournalEntry(
        user_id=user.id,
        type="gratitude",
        content="Gratitude 1",
    )
    db_session.add(entry1)
    db_session.add(entry2)
    db_session.commit()

    # Get wishes
    response = client.get(
        "/journal/entries?entry_type=wish",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "wish"

    # Get gratitude entries
    response = client.get(
        "/journal/entries?entry_type=gratitude",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "gratitude"


def test_delete_journal_entry(client, auth_token, db_session):
    """Test deleting a journal entry."""
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    entry = JournalEntry(
        user_id=user.id,
        type="wish",
        content="Test entry",
    )
    db_session.add(entry)
    db_session.commit()
    entry_id = entry.id

    response = client.delete(
        f"/journal/entries/{entry_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204

    # Verify entry is deleted
    deleted_entry = db_session.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    assert deleted_entry is None


def test_delete_journal_entry_not_found(client, auth_token):
    """Test deleting non-existent journal entry."""
    response = client.delete(
        "/journal/entries/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


def test_delete_journal_entry_other_user(client, auth_token, db_session):
    """Test that user cannot delete other user's entries."""
    from todayflow_backend.services.auth import hash_password
    
    # Create another user
    other_user = User(
        email="other@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(other_user)
    db_session.commit()

    # Create entry for other user
    entry = JournalEntry(
        user_id=other_user.id,
        type="wish",
        content="Other user's entry",
    )
    db_session.add(entry)
    db_session.commit()
    entry_id = entry.id

    # Try to delete it
    response = client.delete(
        f"/journal/entries/{entry_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


def test_get_journal_entries_requires_auth(client):
    """Test that getting journal entries requires authentication."""
    response = client.get("/journal/entries")
    assert response.status_code == 401 or response.status_code == 403


def test_create_journal_entry_requires_auth(client):
    """Test that creating journal entry requires authentication."""
    response = client.post(
        "/journal/entries",
        json={
            "type": "wish",
            "content": "Test",
        },
    )
    assert response.status_code == 401 or response.status_code == 403

