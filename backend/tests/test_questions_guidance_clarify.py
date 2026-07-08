"""POST /questions/reading/clarify — одна уточняющая карта на основной guidance_reading."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import GenerationLog, User
from todayflow_backend.services.auth import hash_password


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = User(
        email="guidance-clarify@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200, response.text
    return str(response.json()["token"])


def test_guidance_clarify_success_then_409(
    client: TestClient,
    db_session: Session,
    test_user: User,
    auth_token: str,
) -> None:
    parent = GenerationLog(
        user_id=test_user.id,
        module="questions",
        surface="guidance_reading",
        status="success",
        model="test",
        normalized_response={
            "question": "Что мне важно понять в ситуации с работой сейчас?",
            "lane": "money_career",
            "interpretation": {"summary": "Краткая линия основного разбора для теста."},
            "answer": {
                "clarity": "кратко",
                "explanation": "e",
                "forecast": "f",
                "decision": "d",
                "today": "t",
            },
            "suggested_route": {"href": "/today", "label": "Today", "reason": "r"},
        },
        input_payload={"topic": "work"},
    )
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)

    headers = {"Authorization": f"Bearer {auth_token}"}
    body = {
        "parent_generation_log_id": parent.id,
        "clarification_goal": "next_step",
        "selected_cards": [{"card_id": 0, "orientation": "upright"}],
    }
    r1 = client.post("/questions/reading/clarify", json=body, headers=headers)
    assert r1.status_code == 200, r1.text
    data = r1.json()
    assert data.get("is_clarification") is True
    assert data.get("clarification_parent_log_id") == parent.id
    assert data.get("clarification_goal") == "next_step"
    assert data.get("spread_id") == "one_card"
    assert len(data.get("tarot_cards") or []) == 1

    r2 = client.post("/questions/reading/clarify", json=body, headers=headers)
    assert r2.status_code == 409


def test_guidance_clarify_rejects_non_parent_surface(
    client: TestClient,
    db_session: Session,
    test_user: User,
    auth_token: str,
) -> None:
    wrong = GenerationLog(
        user_id=test_user.id,
        module="questions",
        surface="questions_answer",
        status="success",
        model="test",
        normalized_response={
            "question": "Короткий вопрос для теста?",
            "lane": "daily",
            "answer": {"clarity": "x", "explanation": "", "forecast": "", "decision": "", "today": ""},
        },
        input_payload={},
    )
    db_session.add(wrong)
    db_session.commit()
    db_session.refresh(wrong)

    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post(
        "/questions/reading/clarify",
        json={
            "parent_generation_log_id": wrong.id,
            "clarification_goal": "risk",
            "selected_cards": [{"card_id": 1, "orientation": "reversed"}],
        },
        headers=headers,
    )
    assert r.status_code == 404
