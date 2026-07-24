"""Tests for human_design Source Family (L3)."""

from __future__ import annotations

from datetime import date, time

from todayflow_backend.services.day_personal_v1 import build_day_personal_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_personal_sources
from todayflow_backend.services.day_sources.human_design import (
    GATE_WHEEL,
    longitude_to_gate_line,
    transit_gates_for_day,
)
from todayflow_backend.services.day_sources.registry import default_registry
from todayflow_backend.services.day_story_interpretation_v1 import (
    build_day_story_interpretation_v1,
)


def test_gate_41_at_aquarius_2():
    act = longitude_to_gate_line(302.0)
    assert act["gate"] == 41
    assert act["line"] == 1


def test_aries_0_is_gate_25():
    act = longitude_to_gate_line(0.0)
    assert act["gate"] == 25
    assert GATE_WHEEL[act["wheel_index"]] == 25


def test_human_design_registered_not_in_foundation():
    reg = default_registry()
    spec = reg.get("human_design")
    assert spec is not None
    assert spec.in_foundation is False
    assert spec.in_personal is True
    assert "human_design" not in [
        s.family_id
        for s in reg.resolve(DaySourceInputs(target_date=date(2026, 7, 24)), foundation_only=True)
    ]


def test_channels_known_pair():
    from todayflow_backend.services.day_sources.human_design import (
        build_channels_payload,
        resolve_channels,
    )

    ch = resolve_channels({1, 8, 99})
    assert any(c["id"] == "1-8" for c in ch)
    assert ch[0]["name_ru"] == "Вдохновение"

    payload = build_channels_payload(
        transit_gates={
            "sun": {"gate": 1},
            "earth": {"gate": 8},
            "moon": {"gate": 20},
        }
    )
    assert payload["capability_id"] == "channels"
    assert any(c["id"] == "1-8" for c in payload["channels"])
    centers = {c["id"] for c in payload["defined_centers"]}
    assert "g" in centers and "throat" in centers


def test_transit_gates_without_birth():
    transit = transit_gates_for_day(date(2026, 7, 24))
    assert 1 <= transit["sun"]["gate"] <= 64
    assert 1 <= transit["sun"]["line"] <= 6
    assert transit["earth"]["gate"] != transit["sun"]["gate"]
    assert transit["depth"] == "full_planet_set_mean_lon"
    bodies = {p["body"] for p in transit["planets"]}
    assert bodies >= {
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "Earth",
    }

    bundle = collect_personal_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    hd = bundle["sources"]["human_design"]
    assert hd["status"] == "ok"
    assert "transit_gates" in hd["capability_ids"]
    assert "channels" in hd["capability_ids"]
    assert "bodygraph_interaction" not in hd["capability_ids"]
    assert "channels" in hd["payload"]["channels"]
    assert "active_gates" in hd["payload"]["channels"]
    assert len(hd["payload"]["channels"]["active_gates"]["transit"]) >= 3


def test_bodygraph_when_birth_date():
    personal = build_day_personal_v1(
        {},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
        birth_time=time(14, 30),
        birth_lat=55.75,
        birth_lon=37.62,
    )
    assert personal["source_inputs"]["has_human_design"] is True
    hd = personal["human_design"]
    assert "bodygraph_interaction" in hd["capability_ids"]
    assert "channels" in hd["capability_ids"]
    assert hd["bodygraph"]["depth"] == "time_place_known"
    assert hd["bodygraph"]["personality"]["sun"]["gate"]
    assert len(hd["bodygraph"]["natal_gates"]) >= 4
    assert "channels" in hd["channels"]
    assert "active_gates" in hd["channels"]
    assert len(hd["channels"]["active_gates"]["natal"]) >= 4


def test_interpretation_can_include_hd_claim():
    interp = build_day_story_interpretation_v1(
        day_engine_brief={"anchor_summary": "Ось.", "do_hint": "Шаг.", "avoid_hint": "Стоп."},
        celestial_events={},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    assert interp["source_inputs"]["has_day_personal"] is True
    assert interp["day_personal"]["human_design"]["transit_gates"]["sun"]["gate"]
    claim_ids = {c["id"] for c in interp["derived_claims"]}
    assert any(i.startswith("claim.personal.hd.") for i in claim_ids)
    hd_claims = [c for c in interp["derived_claims"] if str(c["id"]).startswith("claim.personal.hd.")]
    assert 1 <= len(hd_claims) <= 2
    # Classical planet set feeds channels into beats; prefer channel when present.
    kinds_in_beats = {
        b.get("kind")
        for b in (interp["day_personal"]["human_design"].get("beats") or [])
        if isinstance(b, dict)
    }
    if "channel" in kinds_in_beats:
        assert any("channel" in str(c["id"]) for c in hd_claims)
