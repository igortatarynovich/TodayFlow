"""Integration checks for core profile contract and consistency blocks."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="core-profile@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def _seed_profile_context(client: TestClient, headers: dict[str, str]) -> None:
    profile_response = client.put(
        "/account/profile",
        json={"first_name": "Vika", "last_name": "Flow", "locale": "ru_RU", "gender": "unspecified"},
        headers=headers,
    )
    assert profile_response.status_code == 200

    astro_response = client.post(
        "/account/astro-data",
        json={
            "label": "Primary",
            "birth_date": "1991-08-20",
            "birth_time": "08:30:00",
            "location_name": "Minsk",
            "latitude": 53.9,
            "longitude": 27.56,
            "is_primary": True,
        },
        headers=headers,
    )
    assert astro_response.status_code == 200

    numerology_response = client.post(
        "/numerology/name",
        json={"full_name": "Vika Flow", "birth_date": "1991-08-20"},
        headers=headers,
    )
    assert numerology_response.status_code == 200


def test_account_core_profile_contract(client: TestClient, auth_headers: dict[str, str]) -> None:
    _seed_profile_context(client, auth_headers)

    secondary_response = client.post(
        "/account/astro-data",
        json={
            "label": "Partner",
            "relation": "partner",
            "birth_date": "1992-03-10",
            "location_name": "Warsaw",
        },
        headers=auth_headers,
    )
    assert secondary_response.status_code == 200

    response = client.get("/account/core-profile", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()

    assert payload["profile_version"] == "core-v2"
    assert isinstance(payload["profile_hash"], str) and len(payload["profile_hash"]) == 40
    assert payload["is_ready"] is True
    assert payload["person"]["first_name"] == "Vika"
    assert payload["astro"]["relation"] == "self"
    assert payload["astro"]["sun_sign"] is not None
    assert payload["numerology"]["life_path"] is not None
    assert payload["baseline"]["archetype_seed"] is not None
    assert isinstance(payload["interpretation"], dict)
    assert "daily_lenses" not in payload["interpretation"]
    assert isinstance(payload["daily_interpretation"], dict)
    assert isinstance(payload["daily_interpretation"].get("daily_lenses"), dict)
    assert payload["profiles"]["primary_profile_id"] == payload["astro"]["profile_id"]
    assert payload["profiles"]["has_multiple_profiles"] is True
    assert len(payload["profiles"]["items"]) == 2
    assert any(item["relation"] == "partner" for item in payload["profiles"]["items"])


def test_day_flow_returns_consistency_block(client: TestClient, auth_headers: dict[str, str]) -> None:
    _seed_profile_context(client, auth_headers)

    response = client.get("/day-flow/", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()

    assert payload["core_profile"]["profile_version"] == "core-v2"
    assert "consistency" in payload and isinstance(payload["consistency"], dict)
    assert isinstance(payload["consistency"].get("rules_applied"), list)
    assert payload["consistency"].get("do_focus")
    assert payload["consistency"].get("avoid_focus")


def test_numerology_explain_returns_consistency_block(client: TestClient, auth_headers: dict[str, str]) -> None:
    _seed_profile_context(client, auth_headers)

    response = client.get("/numerology/daily/explain", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()

    assert payload["core_profile"]["profile_version"] == "core-v2"
    assert isinstance(payload.get("consistency"), dict)
    assert isinstance(payload["consistency"].get("rules_applied"), list)
    assert payload["number"]["reduced_value"] is not None
