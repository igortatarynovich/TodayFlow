"""P0.1 — GET /today/contract integration tests."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from todayflow_backend.api.morning_ritual import MorningRitualResponse
from todayflow_backend.services.today_contract_assembler_v1 import DOMAIN_IDS, DOMAIN_LENS_SLOTS

from .conftest import login_bearer_token
from datetime import date

from todayflow_backend.db.models import User
from todayflow_backend.services.day_scenario_native_llm_c1 import native_llm_to_day_scenario_v1
from todayflow_backend.services.day_scenario_project_v1 import project_day_scenario_onto_day_story_v1
from tests.test_native_c1_i0_generation_split_v1 import _global_native
from tests.test_personal_day_v1 import _insert_personal, _ready_story

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


def _seed_ready_personal(db, *, email: str, local_date: date = date(2026, 8, 25)) -> None:
    user = db.query(User).filter(User.email == email).one()
    scenario = native_llm_to_day_scenario_v1(_global_native())
    story = project_day_scenario_onto_day_story_v1(_ready_story(), scenario)
    story["symbolic_note"] = str(story.get("symbolic_note") or "")
    _insert_personal(db, user_id=int(user.id), local_date=local_date, story=story)


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


def test_get_today_contract_returns_model_b_structure(client: TestClient, db_session):
    headers = _auth_headers(client)
    _seed_ready_personal(db_session, email="today-contract@example.com")
    response = client.get(
        "/today/contract",
        params={"target_date": "2026-08-25"},
        headers=headers,
    )
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
        assert set(DOMAIN_LENS_SLOTS).issubset(set(lens.keys()))
    rel = domains["relationships"]
    assert all(str(rel[slot]).strip() for slot in DOMAIN_LENS_SLOTS)

    depth = body.get("depth_layer")
    assert isinstance(depth, dict)
    assert depth.get("version")
    assert "can_generate" in depth
    assert depth.get("access") in {"available", "cta"}
    assert isinstance(depth.get("menu"), list) and len(depth["menu"]) >= 2
    assert all(row.get("topic") and row.get("label") for row in depth["menu"])


def test_get_today_contract_has_no_legacy_keys(client: TestClient):
    headers = _auth_headers(client)
    response = client.get("/today/contract", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()

    top_keys = set(body.keys())
    assert not top_keys & _FORBIDDEN_TOP_KEYS

    # Wave B1 nests may include nested "reason" under welcome_glass — exclude from legacy scan.
    body_without_day_story = {
        k: v for k, v in body.items() if k not in {"day_story", "welcome_glass"}
    }
    serialized = json.dumps(body_without_day_story, ensure_ascii=False).lower()
    for forbidden in ("todayheadline", "todaydetail", '"insight"', '"watch"', '"reason"', '"spheres"'):
        assert forbidden not in serialized


def test_get_today_contract_includes_b1_nests(client: TestClient):
    headers = _auth_headers(client)
    response = client.get("/today/contract", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()

    glass = body.get("welcome_glass")
    assert isinstance(glass, dict)
    assert isinstance(glass.get("mood_tags"), list)
    assert "reason" in glass
    assert isinstance(glass.get("good_for"), list)

    progress = body.get("today_progress")
    assert isinstance(progress, dict)
    assert isinstance(progress.get("rows"), list)
    for row in progress["rows"]:
        assert row.get("kind") in {"habit", "ascetic", "practice"}
        assert isinstance(row.get("days_bool"), list)
        assert len(row["days_bool"]) == 7

    # color_guide may be null when day has no color name yet
    assert "color_guide" in body
    if body["color_guide"] is not None:
        assert body["color_guide"].get("name")


def test_get_today_contract_rejects_invalid_target_date(client: TestClient):
    headers = _auth_headers(client)
    response = client.get("/today/contract", params={"target_date": "2026-13-99"}, headers=headers)
    assert response.status_code == 400
    assert response.json().get("detail") == "invalid target_date"


def test_get_today_contract_missing_family_scenario_does_not_invent_family_domain(
    client: TestClient, db_session
):
    headers = _auth_headers(client)
    _seed_ready_personal(db_session, email="today-contract@example.com")
    morning = _morning_response_no_family()

    with patch(
        "todayflow_backend.api.today.get_morning_ritual_cached",
        new_callable=AsyncMock,
        return_value=morning,
    ):
        response = client.get(
            "/today/contract",
            params={"target_date": "2026-08-25"},
            headers=headers,
        )

    assert response.status_code == 200, response.text
    domains = response.json()["domains"]
    assert "family" not in domains
    rel = domains["relationships"]
    assert all(rel[slot].strip() for slot in DOMAIN_LENS_SLOTS)


@pytest.mark.parametrize("path", ["/today/contract"])
def test_today_contract_requires_auth(client: TestClient, path: str):
    response = client.get(path)
    assert response.status_code == 401
