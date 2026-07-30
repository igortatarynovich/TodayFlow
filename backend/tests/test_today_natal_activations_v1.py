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
    rows, degraded = hit
    assert degraded is False
    assert rows[0]["id"] == "pt-mars-square-sun"
    # Mutating returned copy must not poison cache
    rows[0]["id"] = "mutated"
    again = act.get_snapshot(key)
    assert again is not None
    again_rows, again_degraded = again
    assert again_degraded is False
    assert again_rows[0]["id"] == "pt-mars-square-sun"


def test_snapshot_preserves_degraded_flag():
    key = act.cache_key_for(7, date(2026, 8, 1))
    act.put_snapshot(key, [], degraded=True)
    hit = act.get_snapshot(key)
    assert hit == ([], True)


def test_exception_path_must_not_poison_cache_as_success():
    """Regression: failed resolve must not return [], False on the next hit."""
    import asyncio
    from types import SimpleNamespace

    class BoomTransit:
        async def _calculate_transits(self, *args, **kwargs):
            raise RuntimeError("boom")

    async def _run():
        return await act.resolve_natal_activations(
            user_id=2,
            local_date=date(2026, 7, 29),
            natal_chart=SimpleNamespace(positions={"Sun": 1}),
            birth_data=None,
            transit_service=BoomTransit(),
        )

    first = asyncio.run(_run())
    assert first == ([], True)
    assert act.get_snapshot(act.cache_key_for(2, date(2026, 7, 29))) is None


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
    assert personal[0]["text"]  # experiential why_short — no planet/aspect jargon required


def test_natal_conflict_driver_ids_prefers_pt_by_rank():
    ids = act.natal_conflict_driver_ids(
        [
            {"id": "claim.personal.x", "rank": 1},
            {"id": "pt-mars-square-sun", "rank": 2},
            {"id": "sky-semisquare-0", "rank": 1},
            {"id": "pt-venus-trine-moon", "rank": 1},
            {"id": "pt-uranus-biquintile-mars", "rank": 3},
        ],
        limit=2,
    )
    assert ids == ["pt-venus-trine-moon", "pt-mars-square-sun"]


def test_natal_conflict_driver_ids_empty_without_pt():
    assert act.natal_conflict_driver_ids([{"id": "moon-pisces"}, {"id": "claim.x"}]) == []
