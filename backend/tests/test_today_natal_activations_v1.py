"""Wave 2 — shared natal activations SoT + TTL snapshot."""

from datetime import date

from todayflow_backend.services import today_natal_activations_v1 as act
from todayflow_backend.services import today_domain_verdicts_v1 as verdicts
from todayflow_backend.services.day_scenario_v1 import build_scenario_foundation_v1


def setup_function():
    act.clear_snapshots()


def test_compute_natal_activations_ranks_by_strength_then_orb():
    rows = act.compute_natal_activations(
        [
            {
                "transiting_planet": "Saturn",
                "natal_planet": "Sun",
                "aspect": "square",
                "orb_delta": 2.0,
                "strength": "medium",
            },
            {
                "transiting_planet": "Mars",
                "natal_planet": "Mars",
                "aspect": "square",
                "orb_delta": 0.4,
                "strength": "exact",
            },
        ]
    )
    assert len(rows) == 2
    assert rows[0]["rank"] == 1
    assert rows[0]["transiting_planet"] == "Mars"
    assert rows[0]["exact_time_local"] is None
    assert rows[0]["id"].startswith("pt-")


def test_snapshot_ttl_reused_by_key():
    key = act.cache_key_for(7, date(2026, 8, 1))
    act.put_snapshot(
        key,
        [
            {
                "id": "pt-mars-square-sun",
                "transiting_planet": "Mars",
                "aspect": "square",
                "natal_point": "Sun",
                "orb_deg": 1.0,
                "exact_time_local": None,
                "rank": 1,
            }
        ],
    )
    hit = act.get_snapshot(key)
    assert hit is not None
    assert hit[0]["id"] == "pt-mars-square-sun"
    # Mutating returned copy must not poison cache
    hit[0]["id"] = "mutated"
    again = act.get_snapshot(key)
    assert again is not None
    assert again[0]["id"] == "pt-mars-square-sun"


def test_domain_verdicts_consume_shared_activations():
    activations = act.compute_natal_activations(
        [
            {
                "transiting_planet": "Mars",
                "natal_planet": "Mars",
                "aspect": "square",
                "orb_delta": 0.4,
                "strength": "exact",
            }
        ]
    )
    rows = verdicts.compute_domain_verdicts(activations)
    work = next(r for r in rows if r["domain"] == "work")
    assert work["logic_source"] == "top_driver_v1"
    assert work["verdict"] == "charged"
    assert work["driver_ids"] == [activations[0]["id"]]


def test_foundation_prefers_celestial_natal_activations():
    geo = act.compute_natal_activations(
        [
            {
                "id": "pt-venus-trine-moon",
                "transiting_planet": "Venus",
                "natal_planet": "Moon",
                "aspect": "trine",
                "orb_delta": 1.0,
                "strength": "strong",
            }
        ]
    )
    foundation = build_scenario_foundation_v1(
        interpretation={
            "derived_claims": [
                {
                    "id": "claim.personal.other",
                    "text": "Старый claim без геометрии",
                    "evidence_ids": [],
                    "layer": "personal",
                }
            ]
        },
        celestial_events={"natal_activations": geo},
    )
    personal = foundation["personal_natal_activations"]
    assert personal
    assert personal[0]["id"] == geo[0]["id"]
    assert personal[0]["transiting_planet"] == "Venus"
    assert "Венера" in personal[0]["text"] or "трин" in personal[0]["text"]
