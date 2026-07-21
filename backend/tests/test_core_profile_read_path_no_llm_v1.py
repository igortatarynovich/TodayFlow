"""P0: GET / read-path must not run portrait LLM; only publish_portrait=True may."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.services.core_profile import CoreProfileService
from todayflow_backend.services.snapshot_provenance_v1 import build_snapshot_provenance, merge_snapshot_provenance


@pytest.fixture
def user_with_birth(db_session: Session) -> db_models.User:
    from todayflow_backend.services.auth import hash_password

    user = db_models.User(
        email="readpath-nolm@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    settings = db_models.UserSettings(
        user_id=user.id,
        first_name="Anna",
        locale="ru",
        gender="unspecified",
    )
    db_session.add(settings)
    astro = db_models.AstroProfile(
        user_id=user.id,
        label="Я",
        birth_date=date(1990, 5, 15),
        time_unknown=True,
        location_name="Moscow",
        latitude=55.75,
        longitude=37.61,
        is_primary=True,
        relation="self",
    )
    db_session.add(astro)
    db_session.commit()
    return user


def test_build_default_does_not_call_portrait_llm(db_session: Session, user_with_birth: db_models.User) -> None:
    service = CoreProfileService()
    service.reset_llm_call_counter()
    with patch(
        "todayflow_backend.services.core_profile.build_profile_portrait_v1",
        side_effect=AssertionError("portrait LLM must not run on read-path"),
    ):
        payload = service.build(db_session, user_with_birth)
    assert isinstance(payload, dict)
    assert payload.get("profile_hash")
    assert service.get_llm_call_counter() == 0
    assert "profile_contract_v1" not in payload or payload.get("profile_contract_v1") is None


def test_build_cached_or_baseline_never_calls_portrait(
    db_session: Session, user_with_birth: db_models.User
) -> None:
    service = CoreProfileService()
    with patch(
        "todayflow_backend.services.core_profile.build_profile_portrait_v1",
        side_effect=AssertionError("portrait LLM must not run"),
    ):
        payload = service.build_cached_or_baseline(db_session, user_with_birth)
    assert payload.get("numerology") is not None or payload.get("astro") is not None


def test_publish_portrait_calls_llm(db_session: Session, user_with_birth: db_models.User) -> None:
    service = CoreProfileService()
    service.reset_llm_call_counter()
    fake_contract = {
        "status": "ready",
        "identity_core": "test",
        "strengths": ["a", "b", "c"],
        "growth_zones": ["a", "b", "c"],
        "generation_meta": {"steps": [{"id": 1}]},
    }
    with patch(
        "todayflow_backend.services.core_profile.build_profile_portrait_v1",
        return_value=(fake_contract, {"summary": "x"}, None, False),
    ) as mocked:
        payload = service.build(db_session, user_with_birth, publish_portrait=True)
    assert mocked.called
    assert service.get_llm_call_counter() >= 1
    assert payload.get("snapshot_id") is not None
    assert payload.get("profile_contract_v1", {}).get("identity_core") == "test"


def test_snapshot_provenance_helper() -> None:
    core = {
        "snapshot_id": 1837,
        "profile_hash": "abc",
        "profile_version": "core-v3",
        "profile_contract_v1": {"status": "ready"},
    }
    prov = build_snapshot_provenance(core, source_depth="profile_enriched")
    assert prov["core_profile_snapshot_id"] == 1837
    assert prov["profile_hash"] == "abc"
    assert prov["profile_version"] == "core-v3"
    assert prov["generated_from_snapshot"] is True
    assert prov["source_depth"] == "profile_enriched"

    merged = merge_snapshot_provenance({"spread_id": "one_card"}, core)
    assert merged["spread_id"] == "one_card"
    assert merged["core_profile_snapshot_id"] == 1837


def test_compatibility_prefers_stored_life_path() -> None:
    from todayflow_backend.services.compatibility_engine import CompatibilityEngineService

    engine = CompatibilityEngineService()
    # preferred wins over birth calc
    assert engine._resolve_life_path(date(1990, 5, 15), preferred=7) == 7
    scored = engine._score_life_path_pair(7, 7)
    assert scored == 84
