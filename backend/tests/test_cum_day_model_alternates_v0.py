"""Tests for cum_day_model_alternates_v0 (UMTS §3.5 alternates)."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.compact_user_model_v0 import build_compact_user_model_v0
from todayflow_backend.services.cum_day_model_alternates_v0 import (
    build_day_model_recommendation_alternates_v0,
    resolve_day_model_entity_codes_v0,
)
from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
)


@pytest.fixture
def test_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="cum-alternates@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()


def test_resolve_entity_codes_requires_sun_sign():
    ref = date(2026, 7, 2)
    assert (
        resolve_day_model_entity_codes_v0(
            user_id=1,
            reference_date=ref,
            core_profile={"astro": {}, "numerology": {}},
        )
        is None
    )


def test_resolve_entity_codes_from_core_profile():
    ref = date(2026, 7, 2)
    codes = resolve_day_model_entity_codes_v0(
        user_id=42,
        reference_date=ref,
        core_profile={"astro": {"sun_sign": "Aries"}, "numerology": {}},
    )
    assert codes is not None
    assert codes["astrology_sign_code"] == "astrology.sign.aries"
    assert codes["astrology_planet_code"] == "astrology.planet.mars"
    assert codes["tarot_entity_code"].startswith("tarot.major.")
    assert codes["numerology_entity_code"].startswith("numerology.personal_day.")


def test_build_alternates_from_anchor_pipeline():
    alternates = build_day_model_recommendation_alternates_v0(
        user_id=1,
        reference_date=date(2026, 7, 2),
        entity_codes={
            "tarot_entity_code": ANCHOR_TAROT,
            "numerology_entity_code": ANCHOR_NUMEROLOGY,
            "astrology_planet_code": ANCHOR_PLANET,
            "astrology_sign_code": ANCHOR_SIGN,
        },
    )
    assert 1 <= len(alternates) <= 2
    assert all(alt["source"] == "day_model" for alt in alternates)
    assert all(alt["id"].startswith("rec-dm-") for alt in alternates)
    assert all(isinstance(alt["text"], str) and alt["text"] for alt in alternates)


def test_build_cum_attaches_day_model_alternates(db_session, test_user):
    payload = build_compact_user_model_v0(
        db_session,
        user_id=test_user.id,
        core_profile={
            "person": {"birth_date": "1990-03-21"},
            "astro": {"sun_sign": "Aries"},
            "numerology": {},
        },
        reference_date=date(2026, 7, 2),
    )
    alternates = payload["recommendations"]["alternates"]
    assert isinstance(alternates, list)
    assert len(alternates) <= 2
    if alternates:
        assert alternates[0]["source"] == "day_model"
