"""Delta #2: selected_by vs portrait_influenced_by — Case A / time omit."""

from __future__ import annotations

from todayflow_backend.services.core_profile import CoreProfileService
from todayflow_backend.services.profile_baseline_archetype_v0 import archetype_seed_from_life_path
from todayflow_backend.services.profile_portrait_why_projection_v0 import (
    PROJECTION_VERSION,
    TITLE_RU,
    attach_portrait_why_v0,
    project_portrait_why_v0,
)


def test_life_path_mapping_matches_core_baseline() -> None:
    svc = CoreProfileService()
    for lp in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33):
        built = svc._build_baseline(
            {"sun_sign": "Aries", "sun_element": "fire", "sun_modality": "cardinal"},
            {"life_path": lp},
        )
        assert built["archetype_seed"] == archetype_seed_from_life_path(lp)


def test_case_a_pq001_selected_by_life_path_only() -> None:
    """pq-001: LP1 → Architect; sun/element/rhythm influence portrait, not label selection."""
    why = project_portrait_why_v0(
        numerology={"life_path": 1},
        baseline={
            "archetype_seed": "Architect",
            "element_focus": "Огонь как ясный импульс",
            "rhythm_style": "Быстрый старт без перегрева",
        },
        astro={
            "sun_sign": "Aries",
            "sun_element": "fire",
            "sun_modality": "cardinal",
            "birth_time": None,
            "time_unknown": True,
        },
        natal_summary={"available": False, "reason": "chart_not_cached"},
    )

    assert why["projection_version"] == PROJECTION_VERSION
    assert why["title"] == TITLE_RU
    assert why["rules"]["archetype_selected_only_by"] == "numerology.life_path"

    assert len(why["selected_by"]) == 1
    sel = why["selected_by"][0]
    assert sel["class"] == "selected_by"
    assert sel["life_path"] == 1
    assert sel["archetype_seed"] == "Architect"
    assert "числа пути 1" in sel["label"]
    assert "Овен" not in sel["label"]  # sun must not appear as selector cause

    ids = [row["id"] for row in why["portrait_influenced_by"]]
    assert ids == ["sun", "element", "rhythm"]
    assert all(row["class"] == "portrait_influenced_by" for row in why["portrait_influenced_by"])
    assert why["portrait_influenced_by"][0]["label"].startswith("Солнце в")
    assert why["portrait_influenced_by"][1]["label"] == "Стихия — огонь"
    # Exact baseline rhythm — no invented short gloss that drops words.
    assert why["portrait_influenced_by"][2]["value"] == "Быстрый старт без перегрева"

    omit_ids = {row["id"] for row in why["omitted"]}
    assert "asc" in omit_ids and "mc" in omit_ids
    assert why["honesty_line"]
    assert "ASC" in why["honesty_line"]


def test_with_time_includes_asc_when_natal_has_angles() -> None:
    why = project_portrait_why_v0(
        numerology={"life_path": 4},
        baseline={"archetype_seed": "Sage", "rhythm_style": "Опора на проверенное, без лишних рывков"},
        astro={
            "sun_sign": "Taurus",
            "sun_element": "earth",
            "birth_time": "12:00:00",
            "time_unknown": False,
        },
        natal_summary={
            "available": True,
            "angles": {"ascendant_sign": "Leo", "midheaven_sign": "Aries"},
            "luminaries": [{"name": "Moon", "sign": "Cancer"}],
        },
    )
    ids = [row["id"] for row in why["portrait_influenced_by"]]
    assert "moon" in ids
    assert "asc" in ids
    assert "mc" in ids
    assert why["honesty_line"] is None
    assert why["omitted"] == []


def test_attach_is_ephemeral_on_payload() -> None:
    payload = {
        "astro": {"sun_sign": "Aries", "sun_element": "fire", "time_unknown": True},
        "numerology": {"life_path": 1},
        "baseline": {"archetype_seed": "Architect", "rhythm_style": "Быстрый старт без перегрева"},
        "person": {"locale": "ru"},
        "natal_summary": {"available": False},
    }
    out = attach_portrait_why_v0(payload)
    assert "portrait_why_v0" in out
    assert out["portrait_why_v0"]["selected_by"][0]["archetype_seed"] == "Architect"
