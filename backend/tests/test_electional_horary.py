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
    assert payload["verdict"] in {"supportive", "caution", "avoid"}
    assert payload["checklist"]


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
