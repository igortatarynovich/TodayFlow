"""Tests for today_personal_day_signal_v1 deterministic selector."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.today_personal_day_signal_v1 import (
    select_personal_day_signal,
)


def _sample_foundation(activations: list[dict[str, Any]] | None) -> dict[str, Any]:
    return {
        "contract_version": "day_scenario_v1",
        "personal_natal_activations": activations,
        "celestial_events": {
            "contract_version": "day_events_pack_v1",
            "bodies": {
                "sun": {"body": "sun", "longitude": 45.0, "sign": "Taurus", "degree": 15.0},
                "moon": {"body": "moon", "longitude": 120.0, "sign": "Leo", "degree": 0.0},
                "saturn": {"body": "saturn", "longitude": 150.0, "sign": "Virgo", "degree": 0.0},
            },
            "houses": {"1": {"cusp": 0.0}, "4": {"cusp": 90.0}},
        },
    }


def test_select_personal_day_signal_returns_none_when_no_activations():
    assert select_personal_day_signal(None) is None
    assert select_personal_day_signal({}) is None
    assert select_personal_day_signal(_sample_foundation([])) is None


def test_select_personal_day_signal_picks_first_activation_and_verdicts():
    acts = [
        {
            "id": "act-1",
            "transiting_planet": "Saturn",
            "aspect": "square",
            "natal_point": "Moon",
            "orb_deg": 2.1,
            "strength": 0.8,
            "domain": "relationships",
            "text": "Saturn square Moon pressure on feelings",
        }
    ]
    foundation = _sample_foundation(acts)
    signal = select_personal_day_signal(foundation)
    assert signal is not None
    assert signal["contract_version"] == "personal_day_signal_v1"
    assert signal["main_signal"]["transiting_planet"] == "Saturn"
    assert signal["main_signal"]["aspect"] == "square"
    assert signal["main_signal"]["natal_point"] == "Moon"
    assert isinstance(signal["domain_verdicts"], list)
    assert len(signal["domain_verdicts"]) == 4
    domains = {v["domain"] for v in signal["domain_verdicts"]}
    assert domains == {"work", "money", "relationships", "energy"}
