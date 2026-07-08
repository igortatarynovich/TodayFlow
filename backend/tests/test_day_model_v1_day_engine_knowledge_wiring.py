"""A1.3 — Day Engine knowledge wiring tests."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_context import build_day_context_v0
from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_day_engine_knowledge_integration import (
    try_build_day_engine_knowledge_input_v1,
)
from todayflow_backend.services.day_model_v1_day_engine_knowledge_wiring import (
    DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_CONTRACT,
    DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_KEYS,
    PRESENTATION_LENGTH_SHORT,
    WIRING_RESULT_APPLIED,
    WIRING_RESULT_NOOP,
    WIRING_RESULT_REJECTED,
    build_knowledge_hints_layer,
    extract_day_model_core_snapshot,
    try_apply_day_engine_knowledge_v1,
    try_wire_day_engine_knowledge_from_context_v1,
    validate_day_engine_knowledge_wiring_result_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_BEHAVIOR,
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    select_knowledge_context_v1,
)


def _minimal_guide_decision(**overrides):
    base = {
        "contract_version": "guide_decision_v0",
        "locale": "ru",
        "headline": "Test headline",
        "subline": "A" * 400,
        "core_message": {"body": "body", "risk": "risk", "best_move": "move"},
        "do_items": ["step one", "step two", "step three"],
        "avoid_items": ["avoid one", "avoid two", "avoid three"],
        "energy_line": "energy",
        "focus_line": "focus",
        "risk_line": "risk",
        "risk_detail": "detail",
        "anchors": {"tempo": "steady", "day_direction": "growth"},
    }
    base.update(overrides)
    return base


def _minimal_day_model():
    return {
        "contract_version": "day_model_v0",
        "vector": {"direction": "growth", "summary": "grow"},
        "tempo": {"label": "steady", "summary": "steady day"},
        "risk": {"summary": "overload risk"},
        "strategy": {"summary": "one focus", "one_focus": "finish"},
        "scales": {"direction": "growth", "tempo": "steady"},
        "gate": {"vector_defined": True, "risk_defined": True},
    }


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-test-001",
        "source_knowledge_candidate_id": "kcand-test-001",
        "knowledge_type": KNOWLEDGE_TYPE_BEHAVIOR,
        "claim": "responds_to_action_mode:single_step",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
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
    base.update(overrides)
    return base


def _knowledge_input_from_active(active):
    slice_out = select_knowledge_context_v1([active], target_surface="day_guidance_card")
    outcome = try_build_day_engine_knowledge_input_v1(
        slice_out,
        day_model_snapshot=extract_day_model_core_snapshot(_minimal_day_model()),
    )
    assert outcome["knowledge_input"] is not None
    return outcome["knowledge_input"]


def test_single_action_hint_trims_do_items():
    knowledge_input = _knowledge_input_from_active(_active())
    guide = _minimal_guide_decision()
    outcome = try_apply_day_engine_knowledge_v1(
        knowledge_input,
        guide,
        day_model=_minimal_day_model(),
    )
    assert outcome["result"] == WIRING_RESULT_APPLIED
    wiring = outcome["wiring_result"]
    assert wiring is not None
    wired = wiring["guide_decision_with_knowledge"]
    assert len(wired["do_items"]) == 1
    assert wiring["presentation_adjustments"]["do_items_trimmed"] is True
    assert wiring["applied"] is True


def test_short_response_style_clips_subline():
    active = _active(
        knowledge_id="know-style",
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:short_action",
    )
    knowledge_input = _knowledge_input_from_active(active)
    outcome = try_apply_day_engine_knowledge_v1(
        knowledge_input,
        _minimal_guide_decision(),
    )
    wiring = outcome["wiring_result"]
    assert wiring is not None
    assert wiring["presentation_adjustments"]["presentation_length"] == PRESENTATION_LENGTH_SHORT
    assert wiring["presentation_adjustments"].get("subline_clipped") is True
    assert len(wiring["guide_decision_with_knowledge"]["subline"]) <= 280


def test_content_affinity_boosted_keys():
    active = _active(
        knowledge_type=KNOWLEDGE_TYPE_CONTENT_AFFINITY,
        claim="prefers_content_key_group:day.guidance",
    )
    knowledge_input = _knowledge_input_from_active(active)
    hints = build_knowledge_hints_layer(knowledge_input["hints"])
    assert hints["boosted_content_keys"] == ["day.guidance"]


def test_empty_hints_noop():
    slice_out = select_knowledge_context_v1([], target_surface="day_guidance_card")
    integration = try_build_day_engine_knowledge_input_v1(slice_out)
    outcome = try_apply_day_engine_knowledge_v1(
        integration["knowledge_input"],
        _minimal_guide_decision(),
    )
    assert outcome["result"] == WIRING_RESULT_NOOP
    wiring = outcome["wiring_result"]
    assert wiring is not None
    assert wiring["applied"] is False
    assert "knowledge_hints" in wiring["guide_decision_with_knowledge"]


def test_before_after_hashes_differ_when_applied():
    knowledge_input = _knowledge_input_from_active(_active())
    outcome = try_apply_day_engine_knowledge_v1(knowledge_input, _minimal_guide_decision())
    wiring = outcome["wiring_result"]
    assert wiring is not None
    assert wiring["before_snapshot_hash"] != wiring["after_snapshot_hash"]


def test_day_model_core_unchanged():
    day_model = _minimal_day_model()
    before = extract_day_model_core_snapshot(day_model)
    knowledge_input = _knowledge_input_from_active(_active())
    try_apply_day_engine_knowledge_v1(
        knowledge_input,
        _minimal_guide_decision(),
        day_model=day_model,
    )
    assert extract_day_model_core_snapshot(day_model) == before


def test_rejects_invalid_guide_decision():
    knowledge_input = _knowledge_input_from_active(_active())
    outcome = try_apply_day_engine_knowledge_v1(
        knowledge_input,
        {"contract_version": "wrong"},
    )
    assert outcome["result"] == WIRING_RESULT_REJECTED


def test_full_pipeline_from_context_slice():
    slice_out = select_knowledge_context_v1(
        [_active()],
        target_surface="day_guidance_card",
    )
    outcome = try_wire_day_engine_knowledge_from_context_v1(
        slice_out,
        _minimal_guide_decision(),
        day_model=_minimal_day_model(),
    )
    assert outcome["result"] == WIRING_RESULT_APPLIED
    assert outcome["knowledge_input"] is not None
    assert outcome["wiring_result"] is not None


def test_output_shape_stable():
    knowledge_input = _knowledge_input_from_active(_active())
    outcome = try_apply_day_engine_knowledge_v1(knowledge_input, _minimal_guide_decision())
    wiring = outcome["wiring_result"]
    assert wiring is not None
    assert set(wiring.keys()) == set(DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_KEYS)
    assert wiring["contract_version"] == DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_CONTRACT
    assert validate_day_engine_knowledge_wiring_result_v1(wiring) == []


def test_mutation_flags_false():
    knowledge_input = _knowledge_input_from_active(_active())
    wiring = try_apply_day_engine_knowledge_v1(
        knowledge_input,
        _minimal_guide_decision(),
    )["wiring_result"]
    assert wiring is not None
    assert wiring["profile_update_allowed"] is False
    assert wiring["memory_update_allowed"] is False
    assert wiring["ranking_model_update_allowed"] is False


def test_day_context_wires_active_knowledge():
    fusion = {
        "date": "2026-05-31",
        "scores": {"energy": 55},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {}},
        "recommendations": [],
        "encouragement": "",
    }
    ctx = build_day_context_v0(
        target_date=date(2026, 5, 31),
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        active_knowledge_list=[_active()],
    )
    layers = ctx["layers"]
    assert "knowledge_context_slice" in layers
    assert "day_engine_knowledge_input" in layers
    assert "day_engine_knowledge_wiring" in layers
    gd = layers["guide_decision"]
    assert "knowledge_hints" in gd
    assert len(gd["do_items"]) == 1


def test_day_context_without_active_knowledge_unchanged():
    fusion = {
        "date": "2026-05-31",
        "scores": {"energy": 55},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {}},
        "recommendations": [],
        "encouragement": "",
    }
    ctx = build_day_context_v0(
        target_date=date(2026, 5, 31),
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
    )
    assert "knowledge_context_slice" not in ctx["layers"]
    assert "knowledge_hints" not in ctx["layers"]["guide_decision"]
