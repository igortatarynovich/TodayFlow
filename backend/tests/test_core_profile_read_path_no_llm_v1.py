"""P0: GET / read-path must not run portrait LLM; publish uses deterministic CE path."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

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
    # Legacy profile portrait LLM path is removed; read-path must not trigger any LLM.
    payload = service.build(db_session, user_with_birth)
    assert isinstance(payload, dict)
    assert payload.get("profile_hash")
    assert service.get_llm_call_counter() == 0


def test_build_cached_or_baseline_never_calls_portrait(
    db_session: Session, user_with_birth: db_models.User
) -> None:
    service = CoreProfileService()
    # Legacy profile portrait LLM path is removed; baseline must use deterministic facts only.
    payload = service.build_cached_or_baseline(db_session, user_with_birth)
    assert payload.get("numerology") is not None or payload.get("astro") is not None


def test_read_path_is_ready_uses_hard_fields_only(
    db_session: Session, user_with_birth: db_models.User
) -> None:
    """Shell readiness must match publish: soft missing fields must not force setup again."""
    settings = (
        db_session.query(db_models.UserSettings)
        .filter(db_models.UserSettings.user_id == user_with_birth.id)
        .one()
    )
    # Soft gaps that previously made shell is_ready=false despite birth + life path.
    settings.first_name = None
    settings.gender = None
    db_session.add(
        db_models.NumerologyProfileRecord(
            user_id=user_with_birth.id,
            locale="ru",
            full_name="Anna",
            birth_date=date(1990, 5, 15),
            data={"life_path": {"reduced_value": 7}},
        )
    )
    db_session.commit()

    service = CoreProfileService()
    payload = service.build_cached_or_baseline(db_session, user_with_birth)

    assert payload.get("astro", {}).get("birth_date")
    assert payload.get("numerology", {}).get("life_path") == 7
    assert payload["is_ready"] is True
    assert "first_name" in payload["missing_fields"]
    assert "gender" in payload["missing_fields"]
    assert "astro_birth_time" in payload["missing_fields"]


def test_publish_portrait_uses_ce_deterministic_path(
    db_session: Session, user_with_birth: db_models.User
) -> None:
    """Publish now uses the deterministic CE cascade; no LLM credits are burned."""
    service = CoreProfileService()
    service.reset_llm_call_counter()
    payload = service.build(db_session, user_with_birth, publish_portrait=True)
    assert service.get_llm_call_counter() == 0
    assert payload.get("snapshot_id") is not None
    snap = service._load_snapshot(db_session, user_with_birth.id, str(payload["profile_hash"]))
    assert isinstance(snap, dict)
    assert isinstance(snap.get("profile_contract_v1"), dict)


def test_read_path_does_not_recompute_ce_when_stage5_present(
    db_session: Session, user_with_birth: db_models.User
) -> None:
    """Assemble-once: GET must not rebuild CE when Stage 5 already in the snapshot."""
    service = CoreProfileService()
    published = service.build(db_session, user_with_birth, publish_portrait=True)

    # Seed Stage 5 into the saved snapshot (simulates prior assemble).
    diagnostics = published.get("diagnostics") if isinstance(published.get("diagnostics"), dict) else {}
    diagnostics = {
        **diagnostics,
        "character_engine_stage5": {
            "ok": True,
            "stage5": {"status": "grounded", "validation": {"deterministic": True}},
        },
    }
    published["diagnostics"] = diagnostics
    service._save_snapshot(
        db=db_session,
        user_id=user_with_birth.id,
        profile_hash=str(published["profile_hash"]),
        payload=published,
    )
    service._cache.clear()

    with (
        patch(
            "todayflow_backend.services.character_engine_stage2_shadow_v0.maybe_attach_stage2_shadow",
            side_effect=AssertionError("stage2 must not rebuild on GET"),
        ),
        patch(
            "todayflow_backend.services.character_engine_stage3_shadow_v0.maybe_attach_stage3_shadow",
            side_effect=AssertionError("stage3 must not rebuild on GET"),
        ),
        patch(
            "todayflow_backend.services.character_engine_stage4_shadow_v0.maybe_attach_stage4_shadow",
            side_effect=AssertionError("stage4 must not rebuild on GET"),
        ),
        patch(
            "todayflow_backend.services.character_engine_stage5_shadow_v0.maybe_attach_stage5_shadow",
            side_effect=AssertionError("stage5 must not rebuild on GET"),
        ),
        patch(
            "todayflow_backend.services.character_engine_stage01_shadow_v0.maybe_attach_stage01_shadow",
            side_effect=AssertionError("stage01 must not rebuild on GET when stage5 present"),
        ),
    ):
        again = service.build_cached_or_baseline(db_session, user_with_birth)

    stage5 = ((again.get("diagnostics") or {}).get("character_engine_stage5") or {}).get("stage5")
    assert isinstance(stage5, dict)
    assert stage5.get("status") == "grounded"


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
