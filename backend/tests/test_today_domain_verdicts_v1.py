"""Wave 2 Phase B — top_driver_v1 domain verdicts."""

from todayflow_backend.services import today_domain_verdicts_v1 as verdicts


def test_top_driver_not_sum_for_clustered_work():
    """Several hard work aspects: sum would stay deep negative; top-driver can be charged Mars square."""
    activations = [
        {
            "id": "a1",
            "transiting_planet": "Saturn",
            "aspect": "square",
            "natal_point": "Sun",
            "orb_deg": 1.0,
        },
        {
            "id": "a2",
            "transiting_planet": "Saturn",
            "aspect": "square",
            "natal_point": "MC",
            "orb_deg": 1.2,
        },
        {
            "id": "a3",
            "transiting_planet": "Mars",
            "aspect": "square",
            "natal_point": "Mars",
            "orb_deg": 0.4,
        },
    ]
    rows = verdicts.compute_domain_verdicts(activations)
    work = next(r for r in rows if r["domain"] == "work")
    assert work["logic_source"] == "top_driver_v1"
    assert work["verdict"] == "charged"
    assert work["driver_ids"] == ["a3"]
    assert "Марс" not in work["why_short"]
    assert "квадрат" not in work["why_short"].lower()
    assert work["why_short"]  # experiential bank, not empty


def test_empty_activations_calm_all_domains():
    rows = verdicts.compute_domain_verdicts([])
    assert [r["domain"] for r in rows] == ["work", "money", "relationships", "energy"]
    assert all(r["verdict"] == "calm" for r in rows)


def test_map_weight_bands():
    assert verdicts.map_weight_to_verdict(0.0) == "calm"
    assert verdicts.map_weight_to_verdict(0.9, aspect="conjunction") == "open"
    assert verdicts.map_weight_to_verdict(0.5, aspect="square") == "charged"
    assert verdicts.map_weight_to_verdict(0.5, aspect="trine") == "open"
    assert verdicts.map_weight_to_verdict(-0.4) == "friction"


def test_activations_from_transit_dicts():
    acts = verdicts.activations_from_transit_objects(
        [
            {
                "transiting_planet": "Venus",
                "natal_planet": "Moon",
                "aspect": "trine",
                "orb_delta": 1.5,
            }
        ]
    )
    rows = verdicts.compute_domain_verdicts(acts)
    rel = next(r for r in rows if r["domain"] == "relationships")
    assert rel["verdict"] == "open"
