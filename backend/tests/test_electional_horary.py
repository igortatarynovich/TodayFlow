"""Tests for electional_horary Source Family."""

from __future__ import annotations

from datetime import date, time

from todayflow_backend.services.day_personal_v1 import (
    build_day_personal_v1,
    personal_to_interpretation_claims,
)
from todayflow_backend.services.day_sources import DaySourceInputs, collect_personal_sources
from todayflow_backend.services.day_sources.electional_horary import (
    build_electional_horary_payload,
)
from todayflow_backend.services.day_sources.registry import default_registry


def test_registered_situational():
    reg = default_registry()
    spec = reg.get("electional_horary")
    assert spec is not None
    assert spec.in_foundation is False
    assert spec.in_personal is True
    assert spec.in_today is False


def test_skipped_without_explicit_request():
    bundle = collect_personal_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    row = bundle["sources"]["electional_horary"]
    assert row["status"] == "skipped"
    assert row["unavailable_reason"] == "missing_explicit_request"


def test_unavailable_without_geo_when_requested():
    bundle = collect_personal_sources(
        DaySourceInputs(target_date=date(2026, 7, 24), electional_requested=True)
    )
    row = bundle["sources"]["electional_horary"]
    assert row["status"] == "unavailable"
    assert row["unavailable_reason"] == "missing_geo"


def test_electional_checklist_ok():
    payload = build_electional_horary_payload(
        date(2026, 7, 24),
        electional_time=time(14, 30),
        lat=55.75,
        lon=37.62,
        timezone_name="Europe/Moscow",
    )
    assert payload["mode"] == "electional"
    assert "elective_checklist" in payload["capability_ids"]
    assert payload["ascendant"]["sign_ru"]
    assert payload["moon"]["dignity"]["id"]
    assert payload["moon"]["longitude_method"] == "mean_noon_plus_soft_drift"
    assert payload["verdict"] in {"supportive", "caution", "avoid"}
    assert payload["checklist"]
    assert payload["checklist_counts"]["pass"] + payload["checklist_counts"]["caution"] >= 1
    assert any(c["id"] == "planetary_hour" for c in payload["checklist"])
    assert payload["beats"][0]["kind"] == "verdict"
    assert isinstance(payload.get("planetary_hour"), dict)


def test_electional_near_lunar_aspect_window():
    payload = build_electional_horary_payload(
        date(2026, 7, 24),
        electional_time=time(12, 0),
        lat=55.75,
        lon=37.62,
        timezone_name="Europe/Moscow",
        celestial_events={
            "timed_lunar_aspects": [
                {
                    "title": "Луна □ Марс",
                    "aspect": "square",
                    "exact_time": "2026-07-24T13:00:00+03:00",
                }
            ]
        },
    )
    near = payload["nearest_lunar_aspect"]
    assert near is not None
    assert near["within_3h"] is True
    assert "timed_lunar_aspect_near" in payload["capability_ids"]
    assert any(c["id"] == "lunar_aspect_near" for c in payload["checklist"])


def test_electional_falls_back_to_birth_geo():
    active = build_day_personal_v1(
        {},
        target_date=date(2026, 7, 24),
        birth_lat=55.75,
        birth_lon=37.62,
        timezone="Europe/Moscow",
        electional_requested=True,
        electional_time=time(11, 0),
    )
    assert active["source_inputs"]["has_electional_horary"] is True
    assert active["electional_horary"]["planetary_hour"] is not None


def test_horary_mode_with_question():
    payload = build_electional_horary_payload(
        date(2026, 7, 24),
        electional_time=time(10, 0),
        lat=55.75,
        lon=37.62,
        question="Стоит ли подписывать договор сегодня?",
    )
    assert payload["mode"] == "horary"
    assert "horary_radicality_soft" in payload["capability_ids"]
    assert any(c["id"] == "horary_question" for c in payload["checklist"])


def test_day_personal_wires_only_when_requested():
    idle = build_day_personal_v1({}, target_date=date(2026, 7, 24))
    assert idle["source_inputs"]["has_electional_horary"] is False
    assert idle["source_inputs"]["electional_status"] == "skipped"

    active = build_day_personal_v1(
        {"void_of_course": {"status": "ok", "in_void_of_course": False}},
        target_date=date(2026, 7, 24),
        lat=55.75,
        lon=37.62,
        timezone="Europe/Moscow",
        electional_requested=True,
        electional_time=time(16, 0),
    )
    assert active["source_inputs"]["has_electional_horary"] is True
    assert active["electional_horary"]["verdict"]
    claims = personal_to_interpretation_claims(active)
    assert any(c["id"].startswith("claim.personal.electional.") for c in claims)
