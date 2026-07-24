"""Tests for human_design Source Family (L3)."""

from __future__ import annotations

from datetime import date, time

from todayflow_backend.services.day_personal_v1 import build_day_personal_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_personal_sources
from todayflow_backend.services.day_sources.human_design import (
    GATE_WHEEL,
    LINE_SPAN,
    defined_centers_from_channels,
    longitude_to_gate_line,
    resolve_channels,
    resolve_profile_lines_cross,
    resolve_type_authority,
    resolve_variables,
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
    assert act["color"] == 1
    assert act["tone"] == 1
    assert act["orientation"] == "left"


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
    from todayflow_backend.services.day_sources.human_design import build_channels_payload

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


def test_type_authority_from_natal_channels():
    def pack(gates: set[int]):
        channels = resolve_channels(gates)
        centers = defined_centers_from_channels(channels)
        return resolve_type_authority(natal_channels=channels, natal_centers=centers)

    assert pack(set())["type"]["id"] == "reflector"
    assert pack(set())["authority"]["id"] == "lunar"

    gen = pack({3, 60})
    assert gen["type"]["id"] == "generator"
    assert gen["authority"]["id"] == "sacral"
    assert gen["motor_to_throat"] is False

    mg = pack({20, 34})
    assert mg["type"]["id"] == "manifesting_generator"
    assert mg["motor_to_throat"] is True

    man = pack({21, 45})
    assert man["type"]["id"] == "manifestor"
    assert man["authority"]["id"] == "ego"

    proj = pack({1, 8})
    assert proj["type"]["id"] == "projector"
    assert proj["authority"]["id"] == "self_projected"

    emo = pack({19, 49, 1, 8})
    assert emo["type"]["id"] == "projector"
    assert emo["authority"]["id"] == "emotional"


def test_profile_lines_cross_from_sun_earth():
    pack = resolve_profile_lines_cross(
        personality_sun={"gate": 1, "line": 3, "theme_ru": "самовыражение"},
        personality_earth={"gate": 2, "line": 3, "theme_ru": "направление"},
        design_sun={"gate": 13, "line": 5, "theme_ru": "слушатель"},
        design_earth={"gate": 7, "line": 5, "theme_ru": "роль лидера"},
    )
    assert pack["profile"]["id"] == "3/5"
    assert pack["angle"]["id"] == "right_angle"
    assert pack["profile"]["personality_role_ru"] == "Мученик"
    assert pack["profile"]["design_role_ru"] == "Еретик"
    assert pack["incarnation_cross"]["label"] == "1/2/13/7"
    assert pack["incarnation_cross"]["named_cross"] is None
    assert pack["incarnation_cross"]["conscious_sun"]["label"] == "1.3"

    jux = resolve_profile_lines_cross(
        personality_sun={"gate": 10, "line": 4},
        personality_earth={"gate": 15, "line": 4},
        design_sun={"gate": 2, "line": 1},
        design_earth={"gate": 1, "line": 1},
    )
    assert jux["profile"]["id"] == "4/1"
    assert jux["angle"]["id"] == "juxtaposition"

    left = resolve_profile_lines_cross(
        personality_sun={"gate": 20, "line": 5},
        personality_earth={"gate": 34, "line": 5},
        design_sun={"gate": 10, "line": 1},
        design_earth={"gate": 15, "line": 1},
    )
    assert left["profile"]["id"] == "5/1"
    assert left["angle"]["id"] == "left_angle"


def test_variables_from_color_tone():
    act_left = longitude_to_gate_line(302.0)
    assert act_left["gate"] == 41
    assert act_left["line"] == 1
    assert act_left["color"] == 1
    assert act_left["orientation"] == "left"

    act_right = longitude_to_gate_line(302.0 + LINE_SPAN * 0.75)
    assert act_right["line"] == 1
    assert act_right["color"] >= 4
    assert act_right["orientation"] == "right"

    pack = resolve_variables(
        personality_sun={**act_left, "gate": 1, "line": 1, "label": "1.1"},
        design_sun={**act_right, "gate": 2, "line": 1, "label": "2.1"},
        personality_north_node={**act_left, "gate": 10, "line": 2, "label": "10.2"},
        design_north_node={**act_right, "gate": 15, "line": 2, "label": "15.2"},
    )
    assert pack["capability_id"] == "variables"
    assert pack["digestion"]["orientation"] == "right"
    assert pack["perspective"]["orientation"] == "left"
    assert pack["environment"]["color_name_ru"]
    assert pack["motivation"]["color_name_ru"]
    assert len(pack["pattern"]) == 4
    assert pack["depth"] == "sun_node_colors"


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
    assert "type_authority" not in hd["capability_ids"]
    assert "profile_lines_cross" not in hd["capability_ids"]
    assert "variables" not in hd["capability_ids"]
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
    assert "type_authority" in hd["capability_ids"]
    assert "profile_lines_cross" in hd["capability_ids"]
    assert "variables" in hd["capability_ids"]
    assert str(hd["bodygraph"]["depth"]).startswith("time_place_known")
    assert hd["bodygraph"]["personality"]["sun"]["gate"]
    assert hd["bodygraph"]["personality"]["sun"]["color"] in range(1, 7)
    assert hd["bodygraph"]["personality"]["north_node"]["gate"]
    assert len(hd["bodygraph"]["natal_gates"]) >= 4
    assert "natal_defined_centers" in hd["channels"]
    assert hd["type_authority"]["type"]["id"] in {
        "manifestor",
        "generator",
        "manifesting_generator",
        "projector",
        "reflector",
    }
    assert hd["type_authority"]["authority"]["name_ru"]
    plc = hd["profile_lines_cross"]
    assert "/" in plc["profile"]["id"]
    assert plc["incarnation_cross"]["conscious_sun"]["gate"] == hd["bodygraph"]["personality"]["sun"]["gate"]
    assert plc["incarnation_cross"]["unconscious_sun"]["gate"] == hd["bodygraph"]["design"]["sun"]["gate"]
    assert hd["variables"]["digestion"]["color_name_ru"]
    assert hd["variables"]["perspective"]["orientation"] in {"left", "right"}
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
    assert 1 <= len(hd_claims) <= 3
    kinds_in_beats = {
        b.get("kind")
        for b in (interp["day_personal"]["human_design"].get("beats") or [])
        if isinstance(b, dict)
    }
    assert "type_authority" in kinds_in_beats
    assert "profile_lines_cross" in kinds_in_beats
    assert "variables" in kinds_in_beats
    joined = " ".join(str(c.get("text") or "") for c in hd_claims)
    assert "HD soft" in joined or "Профиль" in joined or "Variables" in joined
