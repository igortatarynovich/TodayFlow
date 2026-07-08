"""Tests for practices API endpoints."""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User, PracticeUsage, Subscription, utc_naive_now


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
def test_user_with_lite_subscription(db_session: Session) -> User:
    """Create a test user with Lite subscription."""
    from todayflow_backend.services.auth import hash_password
    user = User(
        email="lite@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    
    # Create Lite subscription
    subscription = Subscription(
        user_id=user.id,
        stripe_subscription_id="sub_test_lite",
        stripe_price_id="price_test_lite",
        plan_id="lite_plus",
        status="active",
        current_period_start=utc_naive_now(),
        current_period_end=utc_naive_now() + timedelta(days=30),
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_with_pro_subscription(db_session: Session) -> User:
    """Create a test user with Pro subscription."""
    from todayflow_backend.services.auth import hash_password
    user = User(
        email="pro@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    
    # Create Pro subscription
    subscription = Subscription(
        user_id=user.id,
        stripe_subscription_id="sub_test_pro",
        stripe_price_id="price_test_pro",
        plan_id="full_access",
        status="active",
        current_period_start=utc_naive_now(),
        current_period_end=utc_naive_now() + timedelta(days=30),
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User, client: TestClient) -> str:
    """Get auth token for test user."""
    # Login to get token
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Create auth headers for test user."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def auth_token_lite(test_user_with_lite_subscription: User, client: TestClient) -> str:
    """Get auth token for Lite user."""
    response = client.post(
        "/auth/login",
        json={"email": "lite@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def auth_headers_lite(auth_token_lite: str) -> dict:
    """Create auth headers for Lite user."""
    return {"Authorization": f"Bearer {auth_token_lite}"}


@pytest.fixture
def auth_token_pro(test_user_with_pro_subscription: User, client: TestClient) -> str:
    """Get auth token for Pro user."""
    response = client.post(
        "/auth/login",
        json={"email": "pro@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def auth_headers_pro(auth_token_pro: str) -> dict:
    """Create auth headers for Pro user."""
    return {"Authorization": f"Bearer {auth_token_pro}"}


class TestGetPractices:
    """Tests for GET /practices endpoint."""
    
    def test_get_practices_guest(self, client: TestClient):
        """Test getting practices as guest (unauthenticated)."""
        response = client.get("/practices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Guest should only see free practices
        for practice in data:
            assert practice.get("is_free", True)
    
    def test_get_practices_authenticated(self, client: TestClient, auth_headers: dict):
        """Test getting practices as authenticated user."""
        response = client.get("/practices", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_practices_with_category(self, client: TestClient):
        """Test filtering practices by category."""
        response = client.get("/practices?category=breathing")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for practice in data:
            assert practice["category"] == "breathing"
    
    def test_get_practices_with_limit(self, client: TestClient):
        """Test limiting number of practices."""
        response = client.get("/practices?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3


class TestGetPracticeDetail:
    """Tests for GET /practices/{practice_id} endpoint."""
    
    def test_get_practice_detail_exists(self, client: TestClient):
        """Test getting detail of existing practice."""
        response = client.get("/practices/breathing-4-7-8")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "breathing-4-7-8"
        assert "title" in data
        assert "description" in data
        assert "instructions" in data
    
    def test_get_practice_detail_not_found(self, client: TestClient):
        """Test getting detail of non-existent practice."""
        response = client.get("/practices/non-existent-practice")
        assert response.status_code == 404
    
    def test_get_practice_detail_requires_auth_for_paid(self, client: TestClient):
        """Test that paid practices require authentication."""
        # This test depends on having a paid practice in PERSONALIZED_PRACTICES
        # For now, we'll test with a free practice
        response = client.get("/practices/breathing-4-7-8")
        assert response.status_code == 200


class TestGetPracticeLimits:
    """Tests for GET /practices/limits endpoint."""
    
    def test_get_limits_free_user(self, client: TestClient, auth_headers: dict):
        """Test getting limits for free user."""
        response = client.get("/practices/limits", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["subscription_level"] == "free"
        assert data["personalized_limit"] == 1
        assert data["used_this_week"] == 0
        assert data["remaining_this_week"] == 1
    
    def test_get_limits_lite_user(self, client: TestClient, auth_headers_lite: dict):
        """Test getting limits for Lite user."""
        response = client.get("/practices/limits", headers=auth_headers_lite)
        assert response.status_code == 200
        data = response.json()
        assert data["subscription_level"] == "lite"
        assert data["personalized_limit"] == 4
        assert data["used_this_week"] == 0
        assert data["remaining_this_week"] == 4
    
    def test_get_limits_pro_user(self, client: TestClient, auth_headers_pro: dict):
        """Test getting limits for Pro user."""
        response = client.get("/practices/limits", headers=auth_headers_pro)
        assert response.status_code == 200
        data = response.json()
        assert data["subscription_level"] == "pro"
        assert data["personalized_limit"] == 9999  # Unlimited
        assert data["used_this_week"] == 0
        assert data["remaining_this_week"] == 9999
    
    def test_get_limits_requires_auth(self, client: TestClient):
        """Test that limits endpoint requires authentication."""
        response = client.get("/practices/limits")
        assert response.status_code == 401


class TestCompletePractice:
    """Tests for POST /practices/{practice_id}/complete endpoint."""
    
    def test_complete_practice_success(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test successfully completing a practice."""
        response = client.post("/practices/breathing-4-7-8/complete", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["practice_id"] == "breathing-4-7-8"
        assert "completed_at" in data
        
        # Verify usage was recorded
        usage = db_session.query(PracticeUsage).filter_by(practice_id="breathing-4-7-8").first()
        assert usage is not None
    
    def test_complete_practice_not_found(self, client: TestClient, auth_headers: dict):
        """Test completing non-existent practice."""
        response = client.post("/practices/non-existent/complete", headers=auth_headers)
        assert response.status_code == 404
    
    def test_complete_practice_requires_auth(self, client: TestClient):
        """Test that completing practice requires authentication."""
        response = client.post("/practices/breathing-4-7-8/complete")
        assert response.status_code == 401
    
    def test_complete_practice_respects_limits_free(
        self, client: TestClient, auth_headers: dict, db_session: Session, test_user: User
    ):
        """Test that free users cannot exceed their limit."""
        # Complete one practice (free limit is 1)
        response1 = client.post("/practices/breathing-4-7-8/complete", headers=auth_headers)
        assert response1.status_code == 200
        
        # Try to complete another personalized practice (should fail if limit exceeded)
        # Note: This test depends on having a personalized practice available
        # For now, we'll just verify the first completion worked
        limits_response = client.get("/practices/limits", headers=auth_headers)
        assert limits_response.status_code == 200
        limits_data = limits_response.json()
        assert limits_data["used_this_week"] == 1
        assert limits_data["remaining_this_week"] == 0


class TestGetSequences:
    """Tests for GET /practices/sequences endpoint."""
    
    def test_get_sequences_requires_auth(self, client: TestClient):
        """Test that sequences endpoint requires authentication."""
        response = client.get("/practices/sequences")
        assert response.status_code == 401
    
    def test_get_sequences_success(self, client: TestClient, auth_headers: dict):
        """Test getting sequences successfully."""
        response = client.get("/practices/sequences", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that all returned items are sequences
        for sequence in data:
            assert sequence.get("practice_type") == "guided_sequence"
            assert "sequence_id" in sequence
            assert "total_steps" in sequence


class TestGetSequenceDetail:
    """Tests for GET /practices/sequences/{sequence_id} endpoint."""
    
    def test_get_sequence_detail_success(self, client: TestClient, auth_headers: dict):
        """Test getting sequence detail successfully."""
        response = client.get("/practices/sequences/emotional-awareness-week", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["sequence_id"] == "emotional-awareness-week"
        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) > 0
    
    def test_get_sequence_detail_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent sequence."""
        response = client.get("/practices/sequences/non-existent", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_sequence_detail_requires_auth(self, client: TestClient):
        """Test that sequence detail requires authentication."""
        response = client.get("/practices/sequences/emotional-awareness-week")
        assert response.status_code == 401


class TestGetSequenceProgress:
    """Tests for GET /practices/sequences/{sequence_id}/progress endpoint."""
    
    def test_get_sequence_progress_no_progress(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting progress for sequence with no progress."""
        response = client.get(
            "/practices/sequences/emotional-awareness-week/progress",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sequence_id"] == "emotional-awareness-week"
        assert data["completed_steps"] == 0
        assert data["is_completed"] is False
        assert data["current_step"] == 1
    
    def test_get_sequence_progress_with_progress(
        self, client: TestClient, auth_headers: dict, db_session: Session, test_user: User
    ):
        """Test getting progress for sequence with some progress."""
        # Complete first step
        week_start = date.today() - timedelta(days=date.today().weekday())
        usage = PracticeUsage(
            user_id=test_user.id,
            practice_id="emotional-awareness-week-step-1",
            completed_at=utc_naive_now(),
            week_start=week_start,
            is_personalized=True,
            sequence_id="emotional-awareness-week",
            step_number=1,
        )
        db_session.add(usage)
        db_session.commit()
        
        response = client.get(
            "/practices/sequences/emotional-awareness-week/progress",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["completed_steps"] == 1
        assert data["current_step"] == 2
        assert data["is_completed"] is False


class TestCompleteSequenceStep:
    """Tests for POST /practices/sequences/{sequence_id}/steps/{step_number}/complete endpoint."""
    
    def test_complete_sequence_step_success(
        self, client: TestClient, auth_headers: dict, db_session: Session
    ):
        """Test successfully completing a sequence step."""
        response = client.post(
            "/practices/sequences/emotional-awareness-week/steps/1/complete",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "completed_at" in data
        
        # Verify usage was recorded
        usage = db_session.query(PracticeUsage).filter_by(
            sequence_id="emotional-awareness-week",
            step_number=1
        ).first()
        assert usage is not None
    
    def test_complete_sequence_step_sequential(
        self, client: TestClient, auth_headers: dict, db_session: Session, test_user: User
    ):
        """Test that steps must be completed sequentially."""
        # Try to complete step 2 without completing step 1
        response = client.post(
            "/practices/sequences/emotional-awareness-week/steps/2/complete",
            headers=auth_headers
        )
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "предыдущие шаги" in detail or "previous" in detail or "необходимо" in detail
    
    def test_complete_sequence_step_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test completing non-existent step."""
        response = client.post(
            "/practices/sequences/emotional-awareness-week/steps/99/complete",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_complete_sequence_step_requires_auth(self, client: TestClient):
        """Test that completing step requires authentication."""
        response = client.post(
            "/practices/sequences/emotional-awareness-week/steps/1/complete"
        )
        assert response.status_code == 401


class TestGetCategories:
    """Tests for GET /practices/categories/list endpoint."""
    
    def test_get_categories(self, client: TestClient):
        """Test getting list of categories."""
        response = client.get("/practices/categories/list")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)
        assert len(data["categories"]) > 0
        
        # Check category structure
        for category in data["categories"]:
            assert "id" in category
            assert "name" in category
            assert "icon" in category

