"""B1.14 — Evolution consumer metrics tests."""

from __future__ import annotations

import copy
from datetime import UTC, datetime

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import assemble_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_evaluator import (
    RECOMMENDATION_USE_WITH_CAUTION,
    evaluate_day_content_package_v1,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_renderer import render_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_resolver import (
    resolve_content_entries_from_mapping,
)
from todayflow_backend.services.day_model_v1_interpreter import interpret_day_model_v1
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    DECISION_CALL_LLM,
    decide_day_content_llm_call_v1,
)
from todayflow_backend.services.evolution_calendar_runtime_policy_v1 import (
    BLOCK_CALENDAR_SYSTEM_NOT_READY,
    build_evolution_calendar_runtime_policy_v1,
)
from todayflow_backend.services.evolution_commerce_visibility_policy_v1 import (
    build_evolution_commerce_visibility_policy_v1,
)
from todayflow_backend.services.evolution_consumer_metrics_v1 import (
    EVOLUTION_CONSUMER_METRICS_V1_CONTRACT,
    EVOLUTION_CONSUMER_METRICS_V1_KEYS,
    SLICE_APPLIED,
    SLICE_IGNORED,
    SLICE_INVALID,
    build_evolution_consumer_metrics_v1,
    validate_evolution_consumer_metrics_v1,
)
from todayflow_backend.services.evolution_context_selector_wiring_v1 import (
    EXCLUSION_EVOLUTION_CAP,
    select_knowledge_context_with_evolution_v1,
)
from todayflow_backend.services.evolution_day_presentation_envelope_v1 import (
    wire_guide_decision_with_evolution_presentation_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_CALENDAR,
    CONSUMER_COMMERCE_VISIBILITY,
    CONSUMER_CONTEXT_SELECTOR,
    CONSUMER_DAY_ENGINE,
    CONSUMER_LLM_GATE,
    CONSUMER_PRACTICE_SELECTOR,
    extract_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    build_evolution_effect_runtime_policy_v1,
)
from todayflow_backend.services.evolution_llm_gate_wiring_v1 import (
    apply_evolution_caps_to_llm_gate_decision_v1,
)
from todayflow_backend.services.evolution_practice_selector_filter_v1 import (
    BLOCK_COMPLEXITY_ABOVE_STAGE,
    COMPLEXITY_ADVANCED,
    COMPLEXITY_BEGINNER,
    ENTITY_TYPE_PRACTICE,
    build_evolution_practice_selector_filter_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import build_evolution_user_state_v1
from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
)

WINDOW_START = "2026-06-01T00:00:00Z"
WINDOW_END = "2026-06-01T23:59:59Z"
NOW = datetime(2026, 5, 31, 12, 0, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()


@pytest.fixture
def cd() -> dict:
    return load_evolution_cd_v1()


def _metrics(**kwargs):
    return build_evolution_consumer_metrics_v1(
        window_start=WINDOW_START,
        window_end=WINDOW_END,
        **kwargs,
    )


def _artifact(consumer_id: str, artifact: dict, *, evolution_stage: str | None = None) -> dict:
    entry = {"consumer_id": consumer_id, "artifact": artifact}
    if evolution_stage is not None:
        entry["evolution_stage"] = evolution_stage
    return entry


def _policy_for_stage(cd: dict, stage: str, **policy_kwargs):
    progress_by_stage = {
        "seeker": {
            "confirmed_patterns": 0,
            "completed_cycles": 0,
            "reflection_events": 3,
            "active_days": 7,
            "signal_counts": {},
            "confidence": 0.4,
        },
        "architect": {
            "confirmed_patterns": 5,
            "completed_cycles": 3,
            "reflection_events": 21,
            "active_days": 120,
            "signal_counts": {"confirmed_pattern": 2},
            "confidence": 0.75,
        },
        "practitioner": {
            "confirmed_patterns": 2,
            "completed_cycles": 1,
            "reflection_events": 12,
            "active_days": 30,
            "signal_counts": {"practice_completed": 5},
            "confidence": 0.6,
        },
    }
    state = build_evolution_user_state_v1(
        user_id="user-1",
        current_stage=stage,
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot=progress_by_stage[stage],
        evolution_score_snapshot=50 if stage == "seeker" else 420,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    return build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        **policy_kwargs,
    )


def _llm_gate_artifact(cd: dict) -> dict:
    dm = aggregate_day_model_v1(
        tarot_entity_code=ANCHOR_TAROT,
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
    )
    interpretation = interpret_day_model_v1(dm)
    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    package = assemble_day_content_package_v1(interpretation, mapping, resolution)
    evaluation = evaluate_day_content_package_v1(package)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True
    evaluation["issues"] = list(evaluation.get("issues") or []) + [
        "E-CONFLICT:strategy_action+tempo_slow_down"
    ]
    render = render_day_content_package_v1(package, evaluation)
    base = decide_day_content_llm_call_v1(render, evaluation, surface="day_guidance_card")
    assert base["decision"] == DECISION_CALL_LLM
    llm_slice = extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(cd, "seeker"),
        CONSUMER_LLM_GATE,
    )
    return apply_evolution_caps_to_llm_gate_decision_v1(base, llm_slice)


def _context_selector_artifact(cd: dict) -> dict:
    context_slice = extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(cd, "seeker"),
        CONSUMER_CONTEXT_SELECTOR,
    )
    pool = [
        {
            "contract_version": "day_active_knowledge_v1",
            "knowledge_id": f"know-{index}",
            "source_knowledge_candidate_id": f"kcand-{index}",
            "knowledge_type": "content_affinity",
            "claim": claim,
            "confidence": 0.8,
            "evidence_count": 7,
            "evidence_window_days": 21,
            "evidence_signal_ids": ["lsig-1"],
            "source_pattern_id": "pat-test-001",
            "status": "active",
            "created_at": "2026-05-31T12:00:00Z",
            "last_confirmed_at": "2026-05-31T12:00:00Z",
            "expires_at": None,
            "review_required": False,
            "profile_update_allowed": False,
            "memory_update_allowed": False,
            "ranking_update_allowed": False,
        }
        for index, claim in enumerate(
            [
                "prefers_content_key_group:day.topic0",
                "responds_to_surface:day_guidance",
                "responds_to_tempo:slow",
            ]
        )
    ]
    return select_knowledge_context_with_evolution_v1(
        pool,
        day_context={"content_keys": ["day.topic0", "day.guidance", "slow"]},
        target_surface="day_guidance_card",
        evolution_slice=context_slice,
        now=NOW,
    )


def _day_envelope_artifact(cd: dict) -> dict:
    day_slice = extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(
            cd,
            "architect",
            source_systems_ready={"calendar_intelligence": True, "share_features": True},
        ),
        CONSUMER_DAY_ENGINE,
    )
    guide = {
        "contract_version": "guide_decision_v0",
        "locale": "ru",
        "headline": "Test",
        "subline": "Sub",
        "core_message": {"body": "body", "risk": "risk", "best_move": "move"},
        "do_items": ["one", "two", "three"],
        "avoid_items": ["a", "b", "c"],
        "energy_line": "energy",
        "focus_line": "focus",
        "risk_line": "risk",
        "risk_detail": "detail",
        "anchors": {"tempo": "steady", "day_direction": "growth"},
    }
    day_model = {
        "contract_version": "day_model_v0",
        "vector": {"direction": "growth", "summary": "grow"},
        "tempo": {"label": "steady", "summary": "steady day"},
        "risk": {"summary": "overload risk"},
        "strategy": {"summary": "one focus", "one_focus": "finish"},
        "scales": {"direction": "growth", "tempo": "steady"},
        "gate": {"vector_defined": True, "risk_defined": True},
    }
    wired = wire_guide_decision_with_evolution_presentation_v1(
        guide,
        evolution_slice=day_slice,
        day_model=day_model,
    )
    return wired["evolution_day_presentation_envelope"]


def _practice_filter_artifact(cd: dict) -> dict:
    practice_slice = extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(cd, "seeker"),
        CONSUMER_PRACTICE_SELECTOR,
    )
    candidates = [
        {
            "candidate_id": "practice:breathing",
            "entity_type": ENTITY_TYPE_PRACTICE,
            "code": "breathing",
            "complexity_level": COMPLEXITY_BEGINNER,
            "path_themes": ["discipline"],
            "duration_minutes": 5,
            "has_definition": True,
        },
        {
            "candidate_id": "practice:visualization",
            "entity_type": ENTITY_TYPE_PRACTICE,
            "code": "visualization",
            "complexity_level": COMPLEXITY_ADVANCED,
            "path_themes": ["discipline"],
            "duration_minutes": 8,
            "has_definition": True,
        },
    ]
    return build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=practice_slice,
        path_context={"active_path_themes": ["discipline"]},
    )


def _calendar_policy_artifact(cd: dict) -> dict:
    calendar_slice = extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(
            cd,
            "architect",
            source_systems_ready={"calendar_intelligence": False, "share_features": False},
        ),
        CONSUMER_CALENDAR,
    )
    return build_evolution_calendar_runtime_policy_v1(
        calendar_slice,
        calendar_readiness={"calendar_intelligence": False},
    )


def _commerce_policy_artifact(cd: dict) -> dict:
    commerce_slice = extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(
            cd,
            "practitioner",
            source_systems_ready={"commerce_visibility": True},
        ),
        CONSUMER_COMMERCE_VISIBILITY,
    )
    return build_evolution_commerce_visibility_policy_v1(
        commerce_slice,
        commerce_readiness={"commerce_visibility": True},
    )


def test_empty_input_zero_metrics() -> None:
    metrics = _metrics(consumer_artifacts=[])

    assert metrics["consumer_counts"][CONSUMER_LLM_GATE] == 0
    assert metrics["slice_application_counts"][SLICE_APPLIED] == 0
    assert metrics["slice_application_counts"][SLICE_IGNORED] == 0
    assert metrics["cap_counts"] == {}
    assert metrics["block_reason_distribution"] == {}
    assert metrics["stage_distribution"] == {}
    assert metrics["readiness_blocks"] == {}


def test_llm_gate_cap_counted(cd: dict) -> None:
    artifact = _llm_gate_artifact(cd)
    metrics = _metrics(
        consumer_artifacts=[
            _artifact(CONSUMER_LLM_GATE, artifact, evolution_stage="seeker"),
        ]
    )

    assert metrics["consumer_counts"][CONSUMER_LLM_GATE] == 1
    assert metrics["slice_application_counts"][SLICE_APPLIED] == 1
    assert metrics["cap_counts"]["llm_slice_applied"] == 1
    assert metrics["cap_counts"]["llm_call_blocked_or_downgraded"] == 1
    assert "decision:call_llm->no_call" in metrics["block_reason_distribution"]


def test_context_selector_cap_counted(cd: dict) -> None:
    artifact = _context_selector_artifact(cd)
    metrics = _metrics(
        consumer_artifacts=[
            _artifact(CONSUMER_CONTEXT_SELECTOR, artifact, evolution_stage="seeker"),
        ]
    )

    assert metrics["consumer_counts"][CONSUMER_CONTEXT_SELECTOR] == 1
    assert metrics["cap_counts"]["context_ak_cap_applied"] == 1
    assert metrics["cap_counts"]["context_facts_blocked_evolution_cap"] >= 1
    assert metrics["block_reason_distribution"][EXCLUSION_EVOLUTION_CAP] >= 1


def test_day_envelope_counted(cd: dict) -> None:
    artifact = _day_envelope_artifact(cd)
    metrics = _metrics(
        consumer_artifacts=[
            _artifact(CONSUMER_DAY_ENGINE, artifact, evolution_stage="architect"),
        ]
    )

    assert metrics["consumer_counts"][CONSUMER_DAY_ENGINE] == 1
    assert metrics["cap_counts"]["day_envelope_created"] == 1
    assert metrics["cap_counts"]["day_depth_cap_applied"] == 1
    assert metrics["cap_counts"]["day_tone_policy_applied"] == 1


def test_practice_blocked_reasons_counted(cd: dict) -> None:
    artifact = _practice_filter_artifact(cd)
    metrics = _metrics(
        consumer_artifacts=[
            _artifact(CONSUMER_PRACTICE_SELECTOR, artifact, evolution_stage="seeker"),
        ]
    )

    assert metrics["consumer_counts"][CONSUMER_PRACTICE_SELECTOR] == 1
    assert metrics["cap_counts"]["practice_candidates_filtered_in"] == 1
    assert metrics["cap_counts"]["practice_candidates_blocked_out"] == 1
    assert metrics["block_reason_distribution"][BLOCK_COMPLEXITY_ABOVE_STAGE] == 1


def test_calendar_readiness_block_counted(cd: dict) -> None:
    artifact = _calendar_policy_artifact(cd)
    metrics = _metrics(
        consumer_artifacts=[
            _artifact(CONSUMER_CALENDAR, artifact, evolution_stage="architect"),
        ]
    )

    assert metrics["consumer_counts"][CONSUMER_CALENDAR] == 1
    assert metrics["readiness_blocks"][BLOCK_CALENDAR_SYSTEM_NOT_READY] == 1
    assert metrics["block_reason_distribution"][BLOCK_CALENDAR_SYSTEM_NOT_READY] == 1


def test_commerce_visibility_counted(cd: dict) -> None:
    artifact = _commerce_policy_artifact(cd)
    metrics = _metrics(
        consumer_artifacts=[
            _artifact(CONSUMER_COMMERCE_VISIBILITY, artifact, evolution_stage="practitioner"),
        ]
    )

    assert metrics["consumer_counts"][CONSUMER_COMMERCE_VISIBILITY] == 1
    assert metrics["cap_counts"]["commerce_visibility_observed"] == 1
    assert metrics["cap_counts"]["commerce_surfaces_allowed"] >= 1


def test_stage_distribution_correct(cd: dict) -> None:
    artifacts = [
        _artifact(CONSUMER_LLM_GATE, _llm_gate_artifact(cd), evolution_stage="seeker"),
        _artifact(CONSUMER_DAY_ENGINE, _day_envelope_artifact(cd), evolution_stage="architect"),
    ]
    metrics = _metrics(consumer_artifacts=artifacts)

    assert metrics["stage_distribution"]["seeker"] == 1
    assert metrics["stage_distribution"]["architect"] == 1


def test_mutation_flags_false() -> None:
    metrics = _metrics(consumer_artifacts=[])

    assert metrics["read_only"] is True
    assert metrics["promotion_allowed"] is False
    assert metrics["profile_update_allowed"] is False
    assert metrics["memory_update_allowed"] is False


def test_output_shape_stable(cd: dict) -> None:
    invalid_slice = copy.deepcopy(
        extract_evolution_effect_consumer_slice_v1(
            _policy_for_stage(cd, "seeker"),
            CONSUMER_CALENDAR,
        )
    )
    invalid_slice["consumer_id"] = "not_calendar"
    idle_calendar = build_evolution_calendar_runtime_policy_v1(invalid_slice)

    metrics = _metrics(
        consumer_artifacts=[
            _artifact(CONSUMER_CALENDAR, idle_calendar),
        ]
    )

    assert metrics["contract_version"] == EVOLUTION_CONSUMER_METRICS_V1_CONTRACT
    assert set(metrics.keys()) == EVOLUTION_CONSUMER_METRICS_V1_KEYS
    assert validate_evolution_consumer_metrics_v1(metrics) == []
    assert metrics["slice_application_counts"][SLICE_INVALID] == 1
