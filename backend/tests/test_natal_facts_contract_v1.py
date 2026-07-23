"""natal_facts contract validation — Execution Rules."""

from datetime import date

from todayflow_backend.services.natal_facts_contract_v1 import (
    date_only_fallback,
    sun_sign_from_date,
    validate_natal_facts,
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
