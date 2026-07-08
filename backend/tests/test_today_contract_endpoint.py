"""P0.1 — GET /today/contract integration tests."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from todayflow_backend.api.morning_ritual import MorningRitualResponse
from todayflow_backend.services.today_contract_assembler_v1 import DOMAIN_IDS, DOMAIN_LENS_SLOTS

from .conftest import login_bearer_token

_FORBIDDEN_TOP_KEYS = frozenset(
    {
        "spheres",
        "energy",
        "theme",
        "insight",
        "watch",
        "reason",
        "love",
        "work",
        "money",
        "morning",
        "fusion",
        "narrative",
    }
)


def _auth_headers(client: TestClient) -> dict[str, str]:
    email = "today-contract@example.com"
    password = "testpassword123"
    signup = client.post("/auth/signup", json={"email": email, "password": password})
    assert signup.status_code in (200, 201), signup.text
    token = login_bearer_token(client, email, password)
    return {"Authorization": f"Bearer {token}"}


def _collect_json_keys(obj: object, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            keys.add(path)
            keys.update(_collect_json_keys(value, path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            keys.update(_collect_json_keys(item, f"{prefix}[{i}]"))
    return keys


def _morning_response_no_family() -> MorningRitualResponse:
    return MorningRitualResponse(
        date="2026-06-22",
        tarot_card={"id": "test", "name": "Test"},
        tarot_explanation={"summary": "test"},
        numerology_number={"value": 1},
        numerology_explanation={"summary": "test"},
        daily_horoscope={
            "spine": {
                "best_mode": "Держи одну линию.",
                "first_move": "Один шаг по работе.",
                "main_risk": "Распыление.",
            },
            "scenarios": [
                {
                    "slug": "love",
                    "title": "Любовь",
                    "focus": "Честный контакт",
                    "summary": "Прямой разговор.",
                }
            ],
        },
        daily_recommendations={"what_to_do": "Один шаг.", "what_to_avoid": "Импульс."},
    )


def test_get_today_contract_returns_model_b_structure(client: TestClient):
    headers = _auth_headers(client)
    response = client.get("/today/contract", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["contract_version"] == "today_contract_v1"
    assert body.get("global_context", {}).get("period")
    assert body.get("personal_growth", {}).get("development_point")
    assert body.get("primary_action")
    assert body.get("generation_id")
    assert isinstance(body.get("progress"), dict)

    domains = body["domains"]
    for domain_id in DOMAIN_IDS:
        assert domain_id in domains
        lens = domains[domain_id]
        assert set(lens.keys()) == set(DOMAIN_LENS_SLOTS)
        for slot in DOMAIN_LENS_SLOTS:
            assert lens[slot].strip()


def test_get_today_contract_has_no_legacy_keys(client: TestClient):
    headers = _auth_headers(client)
    response = client.get("/today/contract", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()

    top_keys = set(body.keys())
    assert not top_keys & _FORBIDDEN_TOP_KEYS

    body_without_day_story = {k: v for k, v in body.items() if k != "day_story"}
    serialized = json.dumps(body_without_day_story, ensure_ascii=False).lower()
    for forbidden in ("todayheadline", "todaydetail", '"insight"', '"watch"', '"reason"', '"spheres"'):
        assert forbidden not in serialized


def test_get_today_contract_rejects_invalid_target_date(client: TestClient):
    headers = _auth_headers(client)
    response = client.get("/today/contract", params={"target_date": "2026-13-99"}, headers=headers)
    assert response.status_code == 400
    assert response.json().get("detail") == "invalid target_date"


def test_get_today_contract_missing_family_scenario_still_returns_family_lens(client: TestClient):
    headers = _auth_headers(client)
    morning = _morning_response_no_family()

    with patch(
        "todayflow_backend.api.today.get_morning_ritual_cached",
        new_callable=AsyncMock,
        return_value=morning,
    ):
        response = client.get("/today/contract", headers=headers)

    assert response.status_code == 200, response.text
    family = response.json()["domains"]["family"]
    assert all(family[slot].strip() for slot in DOMAIN_LENS_SLOTS)
    assert "семь" in family["status"].lower() or "дом" in family["status"].lower()


@pytest.mark.parametrize("path", ["/today/contract"])
def test_today_contract_requires_auth(client: TestClient, path: str):
    response = client.get(path)
    assert response.status_code == 401
