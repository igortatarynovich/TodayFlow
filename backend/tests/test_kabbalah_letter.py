"""Tests for kabbalah_letter Source Family."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_personal_v1 import (
    build_day_personal_v1,
    personal_to_interpretation_claims,
)
from todayflow_backend.services.day_sources import DaySourceInputs, collect_personal_sources
from todayflow_backend.services.day_sources.kabbalah_letter import (
    build_kabbalah_letter_payload,
    gregorian_to_hebrew,
)
from todayflow_backend.services.day_sources.registry import default_registry


def test_rosh_hashanah_5785():
    h = gregorian_to_hebrew(date(2024, 10, 3))
    assert h["year"] == 5785
    assert h["month_id"] == "tishrei"
    assert h["day"] == 1


def test_elul_before_rosh_hashanah():
    h = gregorian_to_hebrew(date(2024, 10, 2))
    assert h["year"] == 5784
    assert h["month_id"] == "elul"
    assert h["day"] == 29


def test_payload_capabilities_and_school():
    payload = build_kabbalah_letter_payload(date(2026, 7, 24))
    assert "hebrew_date" in payload["capability_ids"]
    assert "date_gematria" in payload["capability_ids"]
    assert "sefira_soft" in payload["capability_ids"]
    assert payload["school_canon"] == "civil_hebrew_calendar_mispar_v0"
    assert payload["hebrew_date"]["label_ru"]
    assert payload["sefira"]["name_ru"]


def test_registered_personal_not_foundation():
    reg = default_registry()
    spec = reg.get("kabbalah_letter")
    assert spec is not None
    assert spec.in_foundation is False
    assert spec.in_personal is True
    assert spec.in_today is False
    assert "kabbalah_letter" not in [
        s.family_id
        for s in reg.resolve(DaySourceInputs(target_date=date(2026, 7, 24)), foundation_only=True)
    ]


def test_day_personal_includes_kabbalah_without_claims():
    bundle = collect_personal_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    assert bundle["sources"]["kabbalah_letter"]["status"] == "ok"

    personal = build_day_personal_v1({}, target_date=date(2026, 7, 24))
    assert personal["source_inputs"]["has_kabbalah_letter"] is True
    assert personal["kabbalah_letter"]["hebrew_date"]["year"]
    # Canon: no Today claim wiring yet.
    claim_ids = {c["id"] for c in personal_to_interpretation_claims(personal)}
    assert not any(i.startswith("claim.personal.kabbalah") for i in claim_ids)
