"""natal_facts contract validation — Execution Rules."""

from datetime import date
from unittest.mock import patch

from todayflow_backend.services.astro import ChartResponse
from todayflow_backend.services.natal_facts_contract_v1 import (
    build_natal_facts_from_chart,
    date_only_fallback,
    generate_natal_facts,
    sun_sign_from_date,
    validate_natal_facts,
)


def _sample_chart() -> ChartResponse:
    return ChartResponse(
        mode="full",
        positions=[
            {"body": "Sun", "sign": "leo", "degree": 12.0, "longitude": 132.0, "house": 5, "retrograde": False},
            {"body": "Moon", "sign": "pisces", "degree": 8.0, "longitude": 338.0, "house": 12},
            {"body": "Mercury", "sign": "virgo", "degree": 2.0, "longitude": 152.0, "house": 6},
        ],
        houses={
            "1": {"sign": "aries", "degree": 10.0, "longitude": 10.0},
            "10": {"sign": "capricorn", "degree": 20.0, "longitude": 290.0},
        },
        metadata={"aspects": []},
    )


def test_sun_sign_parity():
    assert sun_sign_from_date(date(1990, 5, 15)) == "taurus"
    assert sun_sign_from_date(date(2000, 1, 20)) == "aquarius"


def test_date_only_strips_angles_and_houses():
    raw = {
        "planets": [{"id": "sun", "sign": "Leo", "degree": 12}],
        "angles": {"ascendant": {"sign": "virgo", "degree": 10, "absolute_longitude": 150}},
        "houses": [{"house": 1, "sign": "virgo", "degree": 10}],
        "unavailable_facts": [],
    }
    facts = validate_natal_facts(raw, expected_mode="date_only")
    assert facts["mode"] == "date_only"
    assert facts["angles"]["ascendant"] is None
    assert facts["houses"] == []
    assert any(u["key"] == "ascendant" for u in facts["unavailable_facts"])


def test_full_mode_keeps_angles():
    raw = {
        "planets": [{"id": "sun", "sign": "leo"}],
        "angles": {"ascendant": {"sign": "virgo", "degree": 10}},
        "houses": [{"house": 1, "sign": "virgo"}],
    }
    facts = validate_natal_facts(raw, expected_mode="full")
    assert facts["angles"]["ascendant"]["sign"] == "virgo"
    assert len(facts["houses"]) == 1


def test_fallback_has_sun_only():
    facts = date_only_fallback(date(1990, 5, 15))
    assert facts["planets"][0]["id"] == "sun"
    assert facts["planets"][0]["sign"] == "taurus"


def test_build_natal_facts_from_chart_maps_positions_and_houses():
    chart = _sample_chart()
    facts = build_natal_facts_from_chart(chart, mode="full")
    assert facts["provider"] == "astro_service"
    assert facts["mode"] == "full"
    planets = {p["id"]: p for p in facts["planets"]}
    assert planets["sun"]["sign"] == "leo"
    assert planets["sun"]["degree"] == 12.0
    assert planets["sun"]["house"] == 5
    assert planets["moon"]["sign"] == "pisces"
    assert facts["angles"]["ascendant"]["sign"] == "aries"
    assert facts["angles"]["mc"]["sign"] == "capricorn"
    assert any(h["house"] == 1 for h in facts["houses"])


def test_build_natal_facts_from_chart_strips_angles_for_date_only_mode():
    chart = _sample_chart()
    facts = build_natal_facts_from_chart(chart, mode="date_only")
    assert facts["mode"] == "date_only"
    assert facts["angles"]["ascendant"] is None
    assert facts["houses"] == []
    assert any(u["key"] == "ascendant" for u in facts["unavailable_facts"])


def test_generate_natal_facts_uses_chart_data_without_llm():
    available = {
        "birth_date": "1990-05-15",
        "mode": "full",
        "latitude": 55.75,
        "longitude": 37.62,
        "time_unknown": False,
        "birth_time": "12:00:00",
    }
    facts = generate_natal_facts(available_input=available, chart_data=_sample_chart())
    assert facts["provider"] == "astro_service"
    assert any(p["id"] == "sun" for p in facts["planets"])


def test_generate_natal_facts_falls_back_when_chart_service_fails():
    available = {
        "birth_date": "1990-05-15",
        "mode": "date_only",
        "time_unknown": True,
    }
    with patch("todayflow_backend.services.natal_facts_contract_v1.compute_chart_sync", side_effect=RuntimeError("service down")):
        facts = generate_natal_facts(available_input=available)
    assert facts["mode"] == "date_only"
    assert facts["planets"][0]["id"] == "sun"
    assert facts["planets"][0]["sign"] == "taurus"
