"""Tests for tarot API endpoints."""

import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User, TarotDraw, TarotFavorite, TarotReminderSetting


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


@pytest.mark.smoke
def test_get_public_daily_tarot_draw(client: TestClient):
    """Test getting public daily tarot draw (no auth required)."""
    response = client.get("/tarot/daily/public")
    assert response.status_code == 200
    data = response.json()
    
    assert "date" in data
    assert "card" in data
    assert "orientation" in data
    assert data["card"]["id"] is not None
    assert data["card"]["name"] is not None


@pytest.mark.smoke
def test_get_tarot_card_by_id_public(client: TestClient):
    """Major arcana reference card (no auth)."""
    response = client.get("/tarot/cards/0")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 0
    assert data["name"]
    assert "upright" in data
    assert "reversed" in data


@pytest.mark.smoke
def test_get_tarot_card_unknown_returns_404(client: TestClient):
    response = client.get("/tarot/cards/999")
    assert response.status_code == 404


def test_get_daily_tarot_draw_requires_auth(client: TestClient):
    """Test that daily tarot draw requires authentication."""
    response = client.get("/tarot/daily")
    assert response.status_code == 401


def test_get_daily_tarot_draw_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test getting daily tarot draw for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/tarot/daily", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "date" in data
    assert "card" in data
    assert "orientation" in data
    assert data["card"]["id"] is not None
    assert data["card"]["name"] is not None


def test_daily_draw_is_deterministic(client: TestClient, test_user: User, auth_token: str, db_session: Session):
    """Test that daily draw is deterministic (same card for same date)."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # First request
    response1 = client.get("/tarot/daily", headers=headers)
    assert response1.status_code == 200
    data1 = response1.json()
    card_id_1 = data1["card"]["id"]
    
    # Second request (should return same card)
    response2 = client.get("/tarot/daily", headers=headers)
    assert response2.status_code == 200
    data2 = response2.json()
    card_id_2 = data2["card"]["id"]
    
    assert card_id_1 == card_id_2
    assert data1["date"] == data2["date"]


def test_get_tarot_history_requires_auth(client: TestClient):
    """Test that tarot history requires authentication."""
    response = client.get("/tarot/history")
    assert response.status_code == 401


def test_get_tarot_history(client: TestClient, test_user: User, auth_token: str, db_session: Session):
    """Test getting tarot history."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a few historical draws
    for i in range(3):
        draw_date = date.today() - timedelta(days=i+1)
        draw = TarotDraw(
            user_id=test_user.id,
            card_id=1 + i,
            orientation="upright",
            draw_date=draw_date,
        )
        db_session.add(draw)
    db_session.commit()
    
    response = client.get("/tarot/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "today" in data
    assert "history" in data
    assert "streak_days" in data
    assert isinstance(data["history"], list)
    assert len(data["history"]) >= 3  # At least the ones we created


def test_generate_tarot_spread_requires_auth(client: TestClient):
    """Test that spread generation requires authentication."""
    response = client.post("/tarot/spread", json={})
    assert response.status_code == 401


def test_generate_tarot_spread(client: TestClient, test_user: User, auth_token: str):
    """Test generating a tarot spread."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Generate default spread
    response = client.post("/tarot/spread", json={}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "spread_id" in data
    assert "title" in data
    assert "cards" in data
    assert isinstance(data["cards"], list)
    assert len(data["cards"]) > 0
    
    # Each card should have position and card data
    for card_item in data["cards"]:
        assert "position" in card_item
        assert "card" in card_item
        assert "orientation" in card_item
        assert "meaning" in card_item


def test_get_spread_history_requires_auth(client: TestClient):
    """Test that spread history requires authentication."""
    response = client.get("/tarot/spread/history")
    assert response.status_code == 401


def test_get_spread_history(client: TestClient, test_user: User, auth_token: str):
    """Test getting spread history."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # First, generate a spread to have history
    response = client.post("/tarot/spread", json={}, headers=headers)
    assert response.status_code == 200
    
    # Then get history
    response = client.get("/tarot/spread/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "history" in data
    assert isinstance(data["history"], list)
    assert len(data["history"]) >= 1  # At least the one we just created


def test_get_tarot_favorites_requires_auth(client: TestClient):
    """Test that favorites require authentication."""
    response = client.get("/tarot/favorites")
    assert response.status_code == 401


def test_get_tarot_favorites_empty(client: TestClient, test_user: User, auth_token: str):
    """Test getting empty favorites list."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/tarot/favorites", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "favorites" in data
    assert isinstance(data["favorites"], list)
    assert len(data["favorites"]) == 0


def test_toggle_tarot_favorite_requires_auth(client: TestClient):
    """Test that toggle favorite requires authentication."""
    response = client.post("/tarot/favorites/toggle", json={"card_id": 1, "favorite": True})
    assert response.status_code == 401


def test_toggle_tarot_favorite_add(client: TestClient, test_user: User, auth_token: str, db_session: Session):
    """Test adding a card to favorites."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Toggle favorite (add) - favorite field is required by model but not used in logic
    response = client.post(
        "/tarot/favorites/toggle",
        json={"card_id": 1, "favorite": True},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "favorites" in data
    assert 1 in data["favorites"]
    
    # Verify it's persisted
    response = client.get("/tarot/favorites", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert 1 in data["favorites"]


def test_toggle_tarot_favorite_remove(client: TestClient, test_user: User, auth_token: str, db_session: Session):
    """Test removing a card from favorites."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # First add a favorite
    client.post(
        "/tarot/favorites/toggle",
        json={"card_id": 1, "favorite": True},
        headers=headers
    )
    
    # Verify it was added
    response = client.get("/tarot/favorites", headers=headers)
    assert 1 in response.json()["favorites"]
    
    # Then toggle again to remove it - favorite field is required by model but not used in logic
    response = client.post(
        "/tarot/favorites/toggle",
        json={"card_id": 1, "favorite": False},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "favorites" in data
    assert 1 not in data["favorites"]


def test_get_tarot_reminder_requires_auth(client: TestClient):
    """Test that reminder settings require authentication."""
    response = client.get("/tarot/reminder")
    assert response.status_code == 401


def test_get_tarot_reminder_default(client: TestClient, test_user: User, auth_token: str):
    """Test getting default reminder settings."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/tarot/reminder", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "enabled" in data
    assert "timezone" in data
    assert "hour" in data
    assert "minute" in data
    assert data["enabled"] is True
    assert data["timezone"] == "UTC"
    assert data["hour"] == 9
    assert data["minute"] == 0


def test_update_tarot_reminder_requires_auth(client: TestClient):
    """Test that updating reminder requires authentication."""
    response = client.put("/tarot/reminder", json={
        "enabled": True,
        "timezone": "Europe/Moscow",
        "hour": 10,
        "minute": 30
    })
    assert response.status_code == 401


def test_update_tarot_reminder(client: TestClient, test_user: User, auth_token: str):
    """Test updating reminder settings."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = client.put(
        "/tarot/reminder",
        json={
            "enabled": False,
            "timezone": "Europe/Moscow",
            "hour": 10,
            "minute": 30
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["enabled"] is False
    assert data["timezone"] == "Europe/Moscow"
    assert data["hour"] == 10
    assert data["minute"] == 30
    
    # Verify it's persisted
    response = client.get("/tarot/reminder", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is False
    assert data["timezone"] == "Europe/Moscow"


def test_tarot_spread_context_question_first_reading(client: TestClient, test_user: User, auth_token: str):
    """Question-first synthesis payload on POST /tarot/spread/context."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    deck = client.post("/tarot/deck/draw", json={"count": 3}, headers=headers)
    assert deck.status_code == 200, deck.text
    cards = deck.json()
    assert len(cards) >= 1
    selected = [{"card_id": cards[0]["id"], "orientation": "upright"}]

    response = client.post(
        "/tarot/spread/context",
        json={
            "spread_id": "one_card",
            "question": "Стоит ли менять работу?",
            "concern_domain": "work",
            "selected_cards": selected,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    reading = data.get("reading") or {}
    assert reading.get("meaning")
    assert reading.get("synthesis_why")
    assert reading.get("insight_holding")
    assert reading.get("today_suggestion")
    assert isinstance(reading.get("follow_up_chips"), list)
    assert len(reading.get("follow_up_chips") or []) >= 2
    assert "The " not in reading.get("meaning", "")
    assert reading.get("self_question") is None
    assert "generation_log_id" in data


def _assert_card_context_reading(reading, *, question: str, card_names: list[str]):
    meaning = (reading.meaning or "").lower()
    story = (reading.synthesis_why or "").lower()
    assert question.lower() in meaning
    assert "может" in meaning or "может" in story
    assert any(name.lower() in meaning for name in card_names)
    assert "могут означать" in story
    assert reading.insight_holding
    assert reading.today_suggestion


def test_compose_question_first_reading_relationship_ex_partner():
    """Synthesis names cards and what they may mean — no English card names."""
    from todayflow_backend.core import models
    from todayflow_backend.services.tarot_reading_synthesis import compose_question_first_reading

    question = "Что мне важно увидеть в истории с бывшим партнёром?"
    spread = models.TarotSpreadResult(
        spread_id="three_card",
        title="Три карты",
        cards=[
            models.TarotSpreadCard(
                card=models.TarotCard(id=12, name="The Hanged Man", keywords=[], upright="", reversed=""),
                orientation="upright",
                position=models.TarotSpreadPosition(id="past", title="Прошлое"),
                meaning="",
            ),
            models.TarotSpreadCard(
                card=models.TarotCard(id=2, name="The High Priestess", keywords=[], upright="", reversed=""),
                orientation="upright",
                position=models.TarotSpreadPosition(id="present", title="Настоящее"),
                meaning="",
            ),
            models.TarotSpreadCard(
                card=models.TarotCard(id=11, name="Justice", keywords=[], upright="", reversed=""),
                orientation="upright",
                position=models.TarotSpreadPosition(id="future", title="Будущее"),
                meaning="",
            ),
        ],
    )
    reading = compose_question_first_reading(
        spread,
        question=question,
        concern_domain="relationships",
    )
    _assert_card_context_reading(
        reading,
        question=question,
        card_names=["Повешенный", "Верховная"],
    )
    assert "The " not in reading.meaning
    assert len(reading.card_insights or []) == 3
    assert "повешенный" in (reading.insight_holding or "").lower()
    assert any(c.id == "let_go" for c in reading.follow_up_chips)
    assert reading.follow_up_prompt == "Что сейчас кажется самым важным?"


def test_compose_question_first_reading_money_calm_decision():
    from todayflow_backend.core import models
    from todayflow_backend.services.tarot_reading_synthesis import compose_question_first_reading

    spread = models.TarotSpreadResult(
        spread_id="guidance_work_money",
        title="Деньги",
        cards=[
            models.TarotSpreadCard(
                card=models.TarotCard(id=20, name="Judgement", keywords=[], upright="", reversed=""),
                orientation="reversed",
                position=models.TarotSpreadPosition(id="fear", title="Страх"),
                meaning="",
            ),
            models.TarotSpreadCard(
                card=models.TarotCard(id=16, name="Tower", keywords=[], upright="", reversed=""),
                orientation="upright",
                position=models.TarotSpreadPosition(id="reality", title="Реальность"),
                meaning="",
            ),
        ],
    )
    reading = compose_question_first_reading(
        spread,
        question="Какой взгляд поможет принять решение о деньгах спокойнее?",
        concern_domain="money",
    )
    _assert_card_context_reading(
        reading,
        question="Какой взгляд поможет принять решение о деньгах спокойнее?",
        card_names=["Суд", "Башня"],
    )
    assert len(reading.card_insights or []) >= 2
    assert any(c.card_name_ru.startswith("Суд") for c in (reading.card_insights or []))
    assert "суд" in (reading.insight_holding or "").lower() or "башня" in (reading.insight_holding or "").lower()
    assert reading.follow_up_prompt == "Что сейчас кажется самым важным?"
    assert any(c.id == "delayed_step" for c in reading.follow_up_chips)


def test_compose_question_first_reading_work_change_question():
    from todayflow_backend.core import models
    from todayflow_backend.services.tarot_reading_synthesis import compose_question_first_reading

    spread = models.TarotSpreadResult(
        spread_id="one_card",
        title="Одна карта",
        cards=[
            models.TarotSpreadCard(
                card=models.TarotCard(id=7, name="The Chariot", keywords=[], upright="", reversed=""),
                orientation="upright",
                position=models.TarotSpreadPosition(id="focus", title="Фокус"),
                meaning="",
            ),
        ],
    )
    reading = compose_question_first_reading(
        spread,
        question="Стоит ли менять работу?",
        concern_domain="work",
    )
    _assert_card_context_reading(
        reading,
        question="Стоит ли менять работу?",
        card_names=["Колесница"],
    )
    assert reading.follow_up_prompt == "Что сейчас кажется самым важным?"
    assert any(c.id == "stay" for c in reading.follow_up_chips)


def test_compose_question_first_reading_love_feelings_card_context():
    """Any question: name cards and what they may mean in context — no template dodge."""
    from todayflow_backend.core import models
    from todayflow_backend.services.tarot_reading_synthesis import compose_question_first_reading

    spread = models.TarotSpreadResult(
        spread_id="guidance_relationship_five",
        title="Любовный",
        cards=[
            models.TarotSpreadCard(
                card=models.TarotCard(id=0, name="The Fool", keywords=[], upright="", reversed=""),
                orientation="reversed",
                position=models.TarotSpreadPosition(id="you", title="Ты"),
                meaning="",
            ),
            models.TarotSpreadCard(
                card=models.TarotCard(id=18, name="The Moon", keywords=[], upright="", reversed=""),
                orientation="reversed",
                position=models.TarotSpreadPosition(id="other", title="Другой"),
                meaning="",
            ),
            models.TarotSpreadCard(
                card=models.TarotCard(id=3, name="The Empress", keywords=[], upright="", reversed=""),
                orientation="reversed",
                position=models.TarotSpreadPosition(id="dynamic", title="Динамика"),
                meaning="",
            ),
            models.TarotSpreadCard(
                card=models.TarotCard(id=15, name="The Devil", keywords=[], upright="", reversed=""),
                orientation="reversed",
                position=models.TarotSpreadPosition(id="risk", title="Где риск"),
                meaning="",
            ),
        ],
    )
    reading = compose_question_first_reading(
        spread,
        question="она меня любит или нет?",
        concern_domain="relationships",
    )
    meaning = (reading.meaning or "").lower()
    story = (reading.synthesis_why or "").lower()
    assert "скорее да" not in meaning
    assert "скорее нет" not in meaning
    assert "важнее не угадать" not in meaning
    assert "чего ты хочешь от близости" not in meaning
    assert "шут" in meaning
    assert "луна" in meaning
    assert "может" in meaning or "может" in story
    assert "любит или нет" in meaning
    assert "шут" in story and "луна" in story and "императрица" in story
    assert reading.insight_holding
    assert reading.insight_shifting
    assert any(c.id == "honest_talk" for c in reading.follow_up_chips)


def test_compose_question_first_reading_relationships_not_ex():
    from todayflow_backend.core import models
    from todayflow_backend.services.tarot_reading_synthesis import compose_question_first_reading

    spread = models.TarotSpreadResult(
        spread_id="guidance_relationship_five",
        title="Любовный",
        cards=[
            models.TarotSpreadCard(
                card=models.TarotCard(id=6, name="The Lovers", keywords=[], upright="", reversed=""),
                orientation="upright",
                position=models.TarotSpreadPosition(id="you", title="Ты"),
                meaning="",
            ),
            models.TarotSpreadCard(
                card=models.TarotCard(id=2, name="The High Priestess", keywords=[], upright="", reversed=""),
                orientation="upright",
                position=models.TarotSpreadPosition(id="other", title="Другой"),
                meaning="",
            ),
        ],
    )
    reading = compose_question_first_reading(
        spread,
        question="Что сейчас важно понять в отношениях с этим человеком?",
        concern_domain="relationships",
    )
    _assert_card_context_reading(
        reading,
        question="Что сейчас важно понять в отношениях с этим человеком?",
        card_names=["Влюблённые", "Верховная"],
    )
    assert "бывш" not in reading.meaning.lower()
    assert "важнее не угадать" not in reading.meaning.lower()

