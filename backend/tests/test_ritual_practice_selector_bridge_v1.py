"""Tests for ritual practice selector bridge (uses real practice selector/library)."""

from __future__ import annotations

from todayflow_backend.services.ritual_practice_selector_bridge_v1 import (
    build_ritual_practice_selection_context,
    select_practice_for_ritual,
)


def test_build_context_has_required_keys():
    ctx = build_ritual_practice_selection_context(
        ritual_context={
            "mood": "anxious",
            "head_topic": "body",
            "tarot_name_ru": "Отшельник",
            "numerology_value": 7,
        },
        decision_engine={"hero": {"focus": "act", "energy_label": "driven", "risk": "overreach"}},
        core_profile={"evolution": {"stage": "observer"}, "baseline": {"goals": [{"category": "body"}]}},
    )
    assert ctx["contract_version"] == "practice_selection_context_snapshot_v1"
    assert ctx["strategy"] == "act"
    assert ctx["tempo"] == "driven"
    assert ctx["risk"] == "overreach"
    assert ctx["mood_state"] == "anxious"
    assert ctx["energy_state"] == "moderate"
    assert ctx["emotional_load"] == "high"
    assert ctx["evolution_stage"] == "observer"
    assert "body" in ctx["active_path_themes"]
    assert "tarot:Отшельник" in ctx["active_path_themes"]
    assert "numerology:7" in ctx["active_path_themes"]
    assert ctx["goal_categories"] == ["body"]


def test_select_practice_returns_top_candidate_from_library():
    rec = select_practice_for_ritual(
        ritual_context={"mood": "calm", "head_topic": "general", "tarot_name_ru": "Звезда", "numerology_value": 3},
        decision_engine={"hero": {"focus": "stabilize", "energy_label": "steady", "risk": "low"}},
    )
    assert rec is not None
    assert rec.get("contract_version") == "ritual_practice_recommendation_v1"
    assert rec.get("practice_code")
    assert rec.get("title")
    assert rec.get("selected_before_llm") is True


def test_select_practice_returns_deterministic_default_for_empty_context():
    rec = select_practice_for_ritual(
        ritual_context=None,
    )
    assert rec is not None
    assert rec.get("practice_code")
    assert rec.get("selected_before_llm") is True
