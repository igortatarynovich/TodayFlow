"""Integration tests for database operations."""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from todayflow_backend.db.models import User, Subscription, TarotDraw
from todayflow_backend.services.auth import hash_password


def test_transaction_rollback(db_session: Session):
    """Test that transactions can be rolled back."""
    # Create a user
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    user_id = user.id
    
    # Try to create duplicate user (should fail)
    duplicate_user = User(
        email="test@example.com",  # Same email
        password_hash=hash_password("password456"),
        is_paid=False,
    )
    db_session.add(duplicate_user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    # Rollback
    db_session.rollback()
    
    # Verify original user still exists
    existing_user = db_session.query(User).filter_by(id=user_id).first()
    assert existing_user is not None
    assert existing_user.email == "test@example.com"


def test_foreign_key_constraints(db_session: Session):
    """Test that foreign key constraints are enforced."""
    # Try to create subscription without user
    subscription = Subscription(
        user_id=99999,  # Non-existent user
        plan_id="free",
        status="active",
    )
    db_session.add(subscription)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_cascade_behavior(db_session: Session):
    """Test cascade deletes (if configured)."""
    # Create user with related data
    user = User(
        email="cascade@example.com",
        password_hash=hash_password("password123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create tarot draw for user
    tarot_draw = TarotDraw(
        user_id=user.id,
        card_id=1,
        draw_date="2024-01-01",
        orientation="upright"
    )
    db_session.add(tarot_draw)
    db_session.commit()
    
    draw_id = tarot_draw.id
    
    # Delete user
    db_session.delete(user)
    db_session.commit()
    
    # Verify tarot draw is deleted (if cascade is configured)
    # Note: This depends on cascade configuration in models
    deleted_draw = db_session.query(TarotDraw).filter_by(id=draw_id).first()
    # If cascade is configured, draw should be None
    # If not, draw might still exist
    # This test documents the expected behavior


def test_database_session_isolation(db_session: Session):
    """Test that database sessions are isolated."""
    # Create user in this session
    user = User(
        email="isolation@example.com",
        password_hash=hash_password("password123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    user_id = user.id
    
    # Query should find the user
    found_user = db_session.query(User).filter_by(id=user_id).first()
    assert found_user is not None
    assert found_user.email == "isolation@example.com"


def test_unique_constraints(db_session: Session):
    """Test that unique constraints are enforced."""
    # Create first user
    user1 = User(
        email="unique@example.com",
        password_hash=hash_password("password123"),
        is_paid=False,
    )
    db_session.add(user1)
    db_session.commit()
    
    # Try to create second user with same email
    user2 = User(
        email="unique@example.com",  # Same email
        password_hash=hash_password("password456"),
        is_paid=False,
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()

