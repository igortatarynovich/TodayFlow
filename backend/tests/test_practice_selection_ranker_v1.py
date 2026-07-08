"""C1.8 — Practice Selection Ranker tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.data.practice_context_association_registry_loader import (
    clear_practice_context_association_registry_cache,
    load_practice_context_association_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_loader import (
    clear_practice_definition_registry_cache,
    load_practice_definition_registry_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_PRACTICE_SELECTOR,
    extract_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    build_evolution_effect_runtime_policy_v1,
)
from todayflow_backend.services.evolution_practice_selector_filter_v1 import (
    COMPLEXITY_ADVANCED,
    ENTITY_TYPE_PRACTICE,
    build_evolution_practice_selector_filter_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import build_evolution_user_state_v1
from todayflow_backend.services.practice_selection_ranker_v1 import (
    PRACTICE_SELECTION_CONTEXT_SNAPSHOT_V1_CONTRACT,
    PRACTICE_SELECTION_RANK_OUTPUT_V1_CONTRACT,
    PRACTICE_SELECTION_RANK_RESULT_V1_CONTRACT,
    RANKED_CANDIDATE_V1_KEYS,
    SELECTION_DECISION_TRACE_V1_CONTRACT,
    build_practice_selector_filter_from_context_v1,
    rank_practice_selection_v1,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_practice_context_association_registry_cache()
    clear_practice_definition_registry_cache()
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    yield
    clear_practice_context_association_registry_cache()
    clear_practice_definition_registry_cache()
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()


def _snapshot(**overrides: object) -> dict:
    base = {
        "contract_version": PRACTICE_SELECTION_CONTEXT_SNAPSHOT_V1_CONTRACT,
        "strategy": "stabilize",
        "tempo": "keep_steady",
        "risk": "stagnation",
        "emotional_load": "neutral",
        "evolution_stage": "practitioner",
        "active_path_themes": ["clarity"],
        "rhythm_pattern_types": [],
        "energy_state": "moderate",
        "mood_state": "stable",
        "goal_categories": [],
        "knowledge_claim_prefixes": [],
    }
    base.update(overrides)
    return base


def _rank(**kwargs: object) -> dict:
    snapshot = kwargs.pop("context_snapshot", _snapshot())
    return rank_practice_selection_v1(snapshot, **kwargs)


def _codes_ranked(output: dict) -> list[str]:
    return [
        c["practice_definition_code"]
        for c in output["rank_result"]["ranked_candidates"]
    ]


def _code_index(output: dict, code: str) -> int:
    return _codes_ranked(output).index(code)


def test_recovery_context_ranks_reflection_breathing_above_planning() -> None:
    output = _rank(
        context_snapshot=_snapshot(
            strategy="recover",
            tempo="slow_down",
            risk="overpressure",
            emotional_load="intense",
            evolution_stage="observer",
            mood_state="stressed",
        )
    )
    ranked = _codes_ranked(output)
    assert _code_index(output, "reflection") < _code_index(output, "planning")
    assert _code_index(output, "breathing") < _code_index(output, "planning")


def test_plan_context_ranks_planning_above_reflection() -> None:
    output = _rank(
        context_snapshot=_snapshot(
            strategy="plan",
            tempo="keep_steady",
            risk="stagnation",
            emotional_load="neutral",
            evolution_stage="architect",
            goal_categories=["clarity"],
        )
    )
    assert _code_index(output, "planning") < _code_index(output, "reflection")


def test_overpressure_blocks_or_penalizes_body_activation() -> None:
    output = _rank(
        context_snapshot=_snapshot(
            strategy="recover",
            risk="overpressure",
            emotional_load="intense",
        )
    )
    blocked_codes = {
        b["practice_definition_code"] for b in output["rank_result"]["blocked_candidates"]
    }
    ranked = output["rank_result"]["ranked_candidates"]
    body_ranked = next(
        (c for c in ranked if c["practice_definition_code"] == "body_activation"),
        None,
    )
    assert "body_activation" in blocked_codes or (
        body_ranked is not None
        and (
            body_ranked.get("penalties")
            or float(body_ranked.get("rank_score") or 0)
            < float(
                next(
                    c["rank_score"]
                    for c in ranked
                    if c["practice_definition_code"] == "breathing"
                )
            )
        )
    )
    assert "body_activation" in blocked_codes


def test_b1_11_caps_remove_advanced_candidates(cd: dict | None = None) -> None:
    cd = cd or load_evolution_cd_v1()
    state = build_evolution_user_state_v1(
        user_id="user-rank-1",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot={
            "confirmed_patterns": 0,
            "completed_cycles": 0,
            "reflection_events": 3,
            "active_days": 7,
            "signal_counts": {},
            "confidence": 0.4,
        },
        evolution_score_snapshot=100,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="snap-1",
    )
    practice_slice = extract_evolution_effect_consumer_slice_v1(
        policy,
        CONSUMER_PRACTICE_SELECTOR,
    )
    advanced_candidates = [
        {
            "entity_type": ENTITY_TYPE_PRACTICE,
            "code": "meditation",
            "complexity_level": COMPLEXITY_ADVANCED,
            "path_themes": ["discipline"],
            "duration_minutes": 45,
            "has_definition": True,
        },
        {
            "entity_type": ENTITY_TYPE_PRACTICE,
            "code": "breathing",
            "complexity_level": "beginner",
            "path_themes": ["discipline"],
            "duration_minutes": 10,
            "has_definition": True,
        },
    ]
    b1_11 = build_evolution_practice_selector_filter_v1(
        advanced_candidates,
        evolution_slice=practice_slice,
    )
    output = _rank(practice_selector_filter=b1_11)
    blocked_codes = {
        b["practice_definition_code"] for b in output["rank_result"]["blocked_candidates"]
    }
    assert "meditation" in blocked_codes
    assert "breathing" in _codes_ranked(output)


def test_negative_associations_create_blocked_trace() -> None:
    output = _rank(
        context_snapshot=_snapshot(
            strategy="recover",
            risk="overpressure",
            emotional_load="intense",
        )
    )
    trace = output["selection_trace"]
    blocked = trace["blocked_because"]
    assert any(
        item.get("practice_definition_code") == "body_activation"
        for item in blocked
    )


def test_alternatives_considered_populated() -> None:
    output = _rank()
    assert len(output["rank_result"]["alternatives_considered"]) == 10
    assert output["selection_trace"]["alternatives_considered"]


def test_recommendation_and_selection_allowed_false() -> None:
    output = _rank()
    for candidate in output["rank_result"]["ranked_candidates"]:
        assert candidate["selection_allowed"] is False
        assert candidate["recommendation_allowed"] is False
    assert output["rank_result"]["selection_performed"] is False
    assert output["rank_result"]["recommendation_created"] is False


def test_no_llm_prompt_profile_fields() -> None:
    output = _rank()
    forbidden = {"user_id", "profile_id", "prompt", "llm_output", "recommendation", "final_selection"}
    for section in (output["rank_result"], output["selection_trace"]):
        assert forbidden.isdisjoint(set(section.keys()))


def test_output_shape_stable() -> None:
    output = _rank()
    assert output["contract_version"] == PRACTICE_SELECTION_RANK_OUTPUT_V1_CONTRACT
    assert (
        output["rank_result"]["contract_version"]
        == PRACTICE_SELECTION_RANK_RESULT_V1_CONTRACT
    )
    assert (
        output["selection_trace"]["contract_version"]
        == SELECTION_DECISION_TRACE_V1_CONTRACT
    )
    sample = output["rank_result"]["ranked_candidates"][0]
    assert set(sample.keys()) == RANKED_CANDIDATE_V1_KEYS


def test_trace_explains_why_not_planning_in_recovery() -> None:
    output = _rank(
        context_snapshot=_snapshot(
            strategy="recover",
            tempo="slow_down",
            risk="overpressure",
            emotional_load="intense",
        )
    )
    trace = output["selection_trace"]
    assert trace["top_candidate_reason"]
    top_code = output["rank_result"]["ranked_candidates"][0]["practice_definition_code"]
    assert top_code in {"breathing", "reflection", "gratitude"}
    assert "recover" in " ".join(trace["selected_because"]).lower() or any(
        "recover" in reason for reason in trace["selected_because"]
    )
    why_not = trace["why_not_top_alternatives"]
    assert why_not
    if output["rank_result"]["ranked_candidates"][0]["practice_definition_code"] != "planning":
        planning_rank = _code_index(output, "planning") if "planning" in _codes_ranked(output) else -1
        if planning_rank >= 0:
            assert planning_rank > 0


def test_uses_c1_7_registry_version() -> None:
    registry = load_practice_context_association_registry_v1()
    output = _rank()
    assert output["rank_result"]["association_registry_version"] == registry["version"]


def test_helper_builds_b1_11_filter_from_context() -> None:
    snapshot = _snapshot(active_path_themes=["discipline"])
    filt = build_practice_selector_filter_from_context_v1(snapshot)
    assert filt["selection_performed"] is False
