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
    whys = [r["why_short"] for r in rows]
    assert len(set(whys)) == 4
    assert "Без явного сигнала" not in whys


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


def test_why_short_never_prints_planet_aspect_jargon():
    why = verdicts.why_short_for("Venus", "trine", "Saturn", "work")
    assert "Венера" not in why
    assert "трин" not in why.lower()
    assert "Сатурн" not in why
    assert "трин к" not in why.lower()


def test_conjunction_valence_stays_planet_dependent_not_binary_character():
    """Regression: conjunction is foundation character=neutral_amplifying — not
    harmonious/challenging. Signed valence still depends on transit planet."""
    from todayflow_backend.data.foundation_constants_v1 import (
        aspect_character,
        aspect_is_challenging,
        aspect_is_harmonious,
    )

    assert aspect_character("conjunction") == "neutral_amplifying"
    assert not aspect_is_harmonious("conjunction")
    assert not aspect_is_challenging("conjunction")

    assert verdicts.valence_domain("work", "conjunction", "venus", "sun") == 0.8
    assert verdicts.valence_domain("work", "conjunction", "jupiter", "mars") == 0.8
    assert verdicts.valence_domain("work", "conjunction", "saturn", "sun") == -0.55
    assert verdicts.valence_domain("work", "conjunction", "mars", "sun") == 0.75
    assert verdicts.valence_domain("work", "conjunction", "pluto", "sun") == 0.75
    assert verdicts.valence_domain("work", "conjunction", "mercury", "sun") == 0.0
    assert verdicts.valence_domain("money", "conjunction", "saturn", "venus") == -0.7
    assert verdicts.valence_domain("relationships", "conjunction", "mars", "venus") == -0.75
    assert verdicts.valence_domain("energy", "conjunction", "mars", "sun") == 0.85


def test_domain_magnitude_table_pins_draft_specials_unchanged():
    """Storage extract must not recalibrate draft weights."""
    from todayflow_backend.data import domain_magnitude_v1 as mag

    assert mag.CONTRACT_VERSION == "domain_magnitude_v1"
    assert mag.DOMAIN_MAGNITUDE_V1["money"]["special_cases"] == ()
    assert mag.DOMAIN_MAGNITUDE_V1["money"]["challenging_fallback"] == -0.75
    assert mag.DOMAIN_MAGNITUDE_V1["work"]["challenging_fallback"] == -0.65
    assert mag.DOMAIN_MAGNITUDE_V1["relationships"]["challenging_fallback"] == -0.7
    assert mag.DOMAIN_MAGNITUDE_V1["energy"]["challenging_fallback"] == -0.6
    # Irreversibility scale: money > relationships > work > energy, step 0.05
    order = mag.CHALLENGING_FALLBACK_IRREVERSIBILITY_ORDER
    fallbacks = [
        mag.DOMAIN_MAGNITUDE_V1[d]["challenging_fallback"] for d in order
    ]
    assert fallbacks == [-0.75, -0.7, -0.65, -0.6]
    assert all(
        abs((fallbacks[i + 1] - fallbacks[i]) - mag.CHALLENGING_FALLBACK_STEP) < 1e-9
        for i in range(len(fallbacks) - 1)
    )

    # Mars conjunction rule (documented): charge work/energy, friction relationships
    assert verdicts.valence_domain("work", "conjunction", "mars", "sun") == 0.75
    assert verdicts.valence_domain("energy", "conjunction", "mars", "sun") == 0.85
    assert verdicts.valence_domain("relationships", "conjunction", "mars", "venus") == -0.75
    assert verdicts.valence_domain("money", "conjunction", "mars", "venus") == -0.7

    # Money: no square special — falls to challenging_fallback
    assert verdicts.valence_domain("money", "square", "saturn", "venus") == -0.75
    # Work / energy square+mars specials preserved
    assert verdicts.valence_domain("work", "square", "mars", "mars") == 0.85
    assert verdicts.valence_domain("energy", "square", "mars", "mars") == 0.9
    assert verdicts.valence_domain("relationships", "square", "venus", "venus") == -0.8
    assert verdicts.valence_domain("work", "opposition", "saturn", "mc") == -0.55
    assert verdicts.valence_domain("work", "square", "saturn", "saturn") == -0.7
    # Harmonious still global 1.0
    assert verdicts.valence_domain("money", "trine", "saturn", "venus") == 1.0


def test_is_day_favorable_heuristic():
    assert not verdicts.is_day_favorable([])
    assert not verdicts.is_day_favorable(
        [
            {"domain": "work", "verdict": "open"},
            {"domain": "money", "verdict": "friction"},
            {"domain": "relationships", "verdict": "open"},
            {"domain": "energy", "verdict": "calm"},
        ]
    )
    assert not verdicts.is_day_favorable(
        [
            {"domain": "work", "verdict": "open"},
            {"domain": "money", "verdict": "calm"},
            {"domain": "relationships", "verdict": "calm"},
            {"domain": "energy", "verdict": "calm"},
        ]
    )
    assert verdicts.is_day_favorable(
        [
            {"domain": "work", "verdict": "open"},
            {"domain": "money", "verdict": "open"},
            {"domain": "relationships", "verdict": "calm"},
            {"domain": "energy", "verdict": "charged"},
        ]
    )
    # Soft aspects → open on matching domains
    assert verdicts.day_favorable_from_activations(
        [
            {
                "id": "a1",
                "transiting_planet": "Venus",
                "aspect": "trine",
                "natal_point": "Moon",
                "orb_deg": 1.0,
            },
            {
                "id": "a2",
                "transiting_planet": "Jupiter",
                "aspect": "sextile",
                "natal_point": "Venus",
                "orb_deg": 1.0,
            },
        ]
    )
